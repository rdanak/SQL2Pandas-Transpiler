# SQL2Pandas-Transpiler

---

- Marcin Dutka *`marcindutka@student.agh.edu.pl`*
- Robert Danak *`rdanak@student.agh.edu.pl`*

---

### 1. Cel Projektu

  Budowa ***transpilera***, który przyjmuje zapytanie **SQL** (określony podzbiór języka) i generuje kod w języku **Python** przy wykorzystaniu biblioteki **Pandas** do operacji na strukturach danych typu DataFrame.

### 2. Rodzaj translatora

  **Transpiler** - *kompilator źródło-źródło*

### 3. Planowany język implementacji

  **Python**

### 4. Sposób realizacji parsera

  Użycie generatora parserów **ANTLR4**

### 5. Opis tokenów

| **Kategoria**              | **Token**             | **Opis**                    | **Wzorzec**                             |
|----------------------------|-----------------------|-----------------------------|------------------------------------------|
| **Słowa kluczowe**         | `SELECT`              | Start zapytania             | `(?i)SELECT`                             |
|                            | `FROM`                | Źródło danych               | `(?i)FROM`                               |
|                            | `WHERE`               | Filtrowanie                 | `(?i)WHERE`                              |
|                            | `GROUP`               | Klauzula grupowania         | `(?i)GROUP`                              |
|                            | `BY`                  | Słowo pomocnicze            | `(?i)BY`                                 |
|                            | `ORDER`               | Klauzula sortowania         | `(?i)ORDER`                              |
|                            | `HAVING`              | Filtr po grupowaniu         | `(?i)HAVING`                             |
|                            | `LIMIT`               | Limit wierszy               | `(?i)LIMIT`                              |
|                            | `OFFSET`              | Przesunięcie wierszy        | `(?i)OFFSET`                             |
|                            | `ASC`                 | Sortowanie rosnące          | `(?i)ASC`                                |
|                            | `DESC`                | Sortowanie malejące         | `(?i)DESC`                               |
|                            | `AS`                  | Alias                       | `(?i)AS`                                 |
|                            | `ON`                  | Warunek złączenia           | `(?i)ON`                                 |
|                            | `IN`                  | Operator zbioru             | `(?i)IN`                                 |
|                            | `IS`                  | Sprawdzenie typu/wartości   | `(?i)IS`                                 |
|                            | `NOT`                 | Negacja logiczna            | `(?i)NOT`                                |
|                            | `AND`                 | Koniunkcja logiczna         | `(?i)AND`                                |
|                            | `OR`                  | Alternatywa logiczna        | `(?i)OR`                                 |
|                            | `BETWEEN`             | Zakres wartości             | `(?i)BETWEEN`                            |
|                            | `LIKE`                | Dopasowanie wzorca          | `(?i)LIKE`                               |
|                            | `NULL_`               | Wartość pusta               | `(?i)NULL`                               |
|                            | `TRUE`                | Prawda                      | `(?i)TRUE`                               |
|                            | `FALSE`               | Fałsz                       | `(?i)FALSE`                              |
|                            | `DISTINCT`            | Unikalne wartości           | `(?i)DISTINCT`                           |
|                            | `ALL`                 | Wszystkie wartości          | `(?i)ALL`                                |
|                            | `INNER`               | Złączenie wewnętrzne        | `(?i)INNER`                              |
|                            | `OUTER`               | Złączenie zewnętrzne        | `(?i)OUTER`                              |
|                            | `LEFT`                | Złączenie lewostronne       | `(?i)LEFT`                               |
|                            | `RIGHT`               | Złączenie prawostronne      | `(?i)RIGHT`                              |
|                            | `FULL`                | Złączenie pełne             | `(?i)FULL`                               |
|                            | `CROSS`               | Iloczyn kartezjański        | `(?i)CROSS`                              |
|                            | `JOIN`                | Złączenie tabel             | `(?i)JOIN`                               |
| **Funkcje agregujące**     | `MIN`                 | Minimum                     | `(?i)MIN`                                |
|                            | `MAX`                 | Maksimum                    | `(?i)MAX`                                |
|                            | `COUNT`               | Zliczanie                   | `(?i)COUNT`                              |
|                            | `SUM`                 | Suma                        | `(?i)SUM`                                |
|                            | `AVG`                 | Średnia                     | `(?i)AVG`                                |
| **Operatory i interpunkcja** | `COMP_OPERATOR`     | Operatory porównania        | `<>\|!=\|>=\|<=\|>\|<\|=`                |
|                            | `ARITHMETIC_OPERATOR` | Operatory arytmetyczne      | `\+\|-\|\/\|%`                           |
|                            | `COMMA`               | Przecinek                   | `,`                                      |
|                            | `DOT`                 | Kropka                      | `\.`                                     |
|                            | `LPAREN`              | Nawias otwierający          | `\(`                                     |
|                            | `RPAREN`              | Nawias zamykający           | `\)`                                     |
|                            | `MINUS`               | Znak minus (osobny)         | `-`                                      |
|                            | `STAR`                | Gwiazdka                    | `\*`                                     |
|                            | `TERMINATOR`          | Koniec zapytania            | `;`                                      |
| **Dane (Literały)**        | `ID`                  | Nazwy obiektów              | `[a-zA-Z_][a-zA-Z0-9_]*`                 |
|                            | `INTEGER`             | Liczba całkowita            | `[0-9]+`                                 |
|                            | `FLOAT`               | Liczba zmiennoprzecinkowa   | `[0-9]+\.[0-9]*\|\.[0-9]+`               |
|                            | `STRING`              | Ciąg znaków                 | `'[^']*'\|"[^"]*"`                       |
| **Techniczne**             | `BLOCK_COMMENT`       | Komentarz blokowy           | `\/\*[\s\S]*?\*\/`                       |
|                            | `LINE_COMMENT`        | Komentarz liniowy           | `--.*`                                   |
|                            | `WS`                  | Białe znaki                 | `\s+`                                    |

### 6. Gramatyka

  Została napisana w notacji generatora parserów ANTLR4.

```

grammar Grammar;

//  PARSER RULES

query
    : SELECT quantifier? select_list
      FROM table_list
      where_statement?
      group_by_statement?
      having_statement?
      order_by_statement?
      limit_statement?
      TERMINATOR
    ;

quantifier
    : DISTINCT
    | ALL
    ;

// SELECT list

select_list
    : STAR
    | select_column (COMMA select_column)*
    ;

select_column
    : aggregate_function LPAREN quantifier? (column_reference | STAR) RPAREN alias?
    | expression alias?
    ;

alias
    : AS variable
    | variable
    ;

// column / table references

column_reference
    : variable (DOT variable)?
    ;

// FROM / JOIN

table_list
    : table_statement (COMMA table_statement)*
    ;

table_statement
    : variable alias? join_statement*
    ;

join_statement
    : join_type variable alias? ON condition
    ;

join_type
    : INNER? JOIN
    | LEFT  OUTER? JOIN
    | RIGHT OUTER? JOIN
    | FULL  OUTER? JOIN
    | CROSS JOIN
    ;

// WHERE

where_statement
    : WHERE condition
    ;

// conditions / expressions 

condition
    : NOT condition                                   # notCondition
    | condition AND condition                         # andCondition
    | condition OR  condition                         # orCondition
    | LPAREN condition RPAREN                         # parenCondition
    | expression                                      # exprCondition
    ;

expression
    : operand COMP_OPERATOR operand                   # compExpr
    | operand IS NOT? NULL_                           # nullExpr
    | operand NOT? BETWEEN operand AND operand        # betweenExpr
    | operand NOT? LIKE STRING                        # likeExpr
    | operand NOT? IN LPAREN value_list RPAREN        # inExpr
    | operand                                         # simpleExpr
    ;

operand
    : operand ARITHMETIC_OPERATOR operand             # arithOperand
    | LPAREN operand RPAREN                           # parenOperand
    | aggregate_function LPAREN (column_reference | STAR) RPAREN  # aggOperand
    | column_reference                                # colOperand
    | literal                                         # litOperand
    ;

value_list
    : literal (COMMA literal)*
    ;

// GROUP BY 

group_by_statement
    : GROUP BY column_reference (COMMA column_reference)*
    ;

// HAVING

having_statement
    : HAVING condition
    ;

// ORDER BY

order_by_statement
    : ORDER BY order_item (COMMA order_item)*
    ;

order_item
    : column_reference (ASC | DESC)?
    ;

// LIMIT / OFFSET

limit_statement
    : LIMIT INTEGER (OFFSET INTEGER)?
    ;

// literals & primitives

literal
    : STRING
    | number
    | TRUE
    | FALSE
    | NULL_
    ;

number
    : MINUS? (INTEGER | FLOAT)
    ;

aggregate_function
    : MIN | MAX | COUNT | SUM | AVG
    ;

variable
    : ID
    ;

//  LEXER RULES  

// keywords

SELECT   : [sS][eE][lL][eE][cC][tT];
FROM     : [fF][rR][oO][mM];
WHERE    : [wW][hH][eE][rR][eE];
GROUP    : [gG][rR][oO][uU][pP];
BY       : [bB][yY];
ORDER    : [oO][rR][dD][eE][rR];
HAVING   : [hH][aA][vV][iI][nN][gG];
LIMIT    : [lL][iI][mM][iI][tT];
OFFSET   : [oO][fF][fF][sS][eE][tT];
ASC      : [aA][sS][cC];
DESC     : [dD][eE][sS][cC];
AS       : [aA][sS];
ON       : [oO][nN];
IN       : [iI][nN];
IS       : [iI][sS];
NOT      : [nN][oO][tT];
AND      : [aA][nN][dD];
OR       : [oO][rR];
BETWEEN  : [bB][eE][tT][wW][eE][eE][nN];
LIKE     : [lL][iI][kK][eE];
NULL_    : [nN][uU][lL][lL];
TRUE     : [tT][rR][uU][eE];
FALSE    : [fF][aA][lL][sS][eE];
DISTINCT : [dD][iI][sS][tT][iI][nN][cC][tT];
ALL      : [aA][lL][lL];
INNER    : [iI][nN][nN][eE][rR];
OUTER    : [oO][uU][tT][eE][rR];
LEFT     : [lL][eE][fF][tT];
RIGHT    : [rR][iI][gG][hH][tT];
FULL     : [fF][uU][lL][lL];
CROSS    : [cC][rR][oO][sS][sS];
JOIN     : [jJ][oO][iI][nN];

// aggregate functions

MIN      : [mM][iI][nN];
MAX      : [mM][aA][xX];
COUNT    : [cC][oO][uU][nN][tT];
SUM      : [sS][uU][mM];
AVG      : [aA][vV][gG];

// operators & punctuation 

COMP_OPERATOR       : '<>' | '!=' | '=' | '<=' | '>=' | '<' | '>';
ARITHMETIC_OPERATOR : '+' | '-' | '/' | '%';
COMMA    : ',';
DOT      : '.';
LPAREN   : '(';
RPAREN   : ')';
MINUS    : '-';
STAR     : '*';
TERMINATOR : ';';

// literals

ID      : [a-zA-Z_] [a-zA-Z0-9_]*;

INTEGER : [0-9]+;

FLOAT   : [0-9]+ '.' [0-9]*
        | '.' [0-9]+
        ;

STRING  : '\'' (~['\r\n] | '\'\'')*  '\''
        | '"'  (~["\r\n] | '""')*    '"'
        ;

// whitespace & comments

BLOCK_COMMENT : '/*' .*? '*/' -> skip;
LINE_COMMENT  : '--' ~[\r\n]* -> skip;
WS            : [ \t\r\n]+   -> skip;
```

### 8. Krótka instrukcja obsługi

#### Wymagania wstępne
- Java (wymagana przez ANTLR)
- Python 3.14+
- uv

#### Przygotowanie

1. Sklonuj repozytorium
```bash
   git clone https://github.com/ty/SQL2Pandas-Transpiler && cd SQL2Pandas-Transpiler
```

2. Pobierz ANTLR
```bash
   make get_antlr
```

3. Wygeneruj pliki parsera
```bash
   make generate
```

4. Zainstaluj zależności
```bash
   uv sync
```

#### Użycie

Transpilacja pliku SQL do kodu pandas:
```bash
uv run sql2pandas plik.sql
```

Zapis wyniku do pliku:
```bash
uv run sql2pandas plik.sql -o wynik.py
```

### Drzewo Projektu
```
SQL2Pandas-Transpiler/
├── .gitignore
├── .python-version
├── grammar/
│   └── Grammar.g4
├── makefile
├── pyproject.toml
├── README.md
├── sql2pandas/
│   ├── __init__.py
│   ├── cli.py
│   ├── generated/
│   │   └── .gitkeep
│   └── visitor.py
├── test/
│   └── test_select.py
└── uv.lock
```

