import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sql2pandas'))
from cli import transpile

def test_simple_select():
    sql    = "SELECT name FROM users;"
    result = transpile(sql)
    assert result == (
        "df = users\n"
        "df = df[['name']]"
    )


def test_select_multiple_columns():
    sql    = "SELECT name, age, email FROM users;"
    result = transpile(sql)
    assert result == (
        "df = users\n"
        "df = df[['name', 'age', 'email']]"
    )


def test_select_star():
    sql    = "SELECT * FROM users;"
    result = transpile(sql)
    assert result == (
        "df = users"
    )


def test_select_with_where():
    sql    = "SELECT name FROM users WHERE age > 18;"
    result = transpile(sql)
    assert result == (
        "df = users\n"
        "df = df[df['age'] > 18]\n"
        "df = df[['name']]"
    )


def test_where_and():
    sql    = "SELECT x, y FROM table WHERE x > 3 AND y < 7;"
    result = transpile(sql)
    assert result == (
        "df = table\n"
        "df = df[(df['x'] > 3) & (df['y'] < 7)]\n"
        "df = df[['x', 'y']]"
    )


def test_where_or():
    sql    = "SELECT name FROM users WHERE age < 18 OR age > 65;"
    result = transpile(sql)
    assert result == (
        "df = users\n"
        "df = df[(df['age'] < 18) | (df['age'] > 65)]\n"
        "df = df[['name']]"
    )


def test_order_by_desc():
    sql    = "SELECT name, age FROM users WHERE age > 18 ORDER BY age DESC LIMIT 10;"
    result = transpile(sql)
    assert result == (
        "df = users\n"
        "df = df[df['age'] > 18]\n"
        "df = df[['name', 'age']]\n"
        "df = df.sort_values(['age'], ascending=[False])\n"
        "df = df.head(10)"
    )


def test_group_by_with_aggregate():
    sql    = "SELECT department, COUNT(id) FROM employees GROUP BY department;"
    result = transpile(sql)
    assert result == (
        "df = employees\n"
        "df = df.groupby(['department'])\n"
        "df = df.agg({'id': 'count'})"
    )


def test_distinct():
    sql    = "SELECT DISTINCT department FROM employees;"
    result = transpile(sql)
    assert result == (
        "df = employees\n"
        "df = df[['department']].drop_duplicates()"
    )


def test_limit():
    sql    = "SELECT name FROM users LIMIT 5;"
    result = transpile(sql)
    assert result == (
        "df = users\n"
        "df = df[['name']]\n"
        "df = df.head(5)"
    )
