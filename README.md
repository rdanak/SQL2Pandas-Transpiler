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

| **Kategoria**       | **Token ID** | **Opis**                  | **Zoptymalizowane Wyrażenie**                                  |
| ------------------- | ------------ | ------------------------- | -------------------------------------------------------------- |
| **Słowa kluczowe**  | `SELECT`     | Start zapytania           | ```(?i)SELECT```                                               |
|                     | `FROM`       | Źródło danych             | ```(?i)FROM```                                                 |
|                     | `WHERE`      | Filtrowanie               | ```(?i)WHERE```                                                |
|                     | `GROUP_BY`   | Grupowanie                | ```(?i)GROUP\s+BY```                                           |
|                     | `ORDER_BY`   | Sortowanie                | ```(?i)ORDER\s+BY```                                           |
|                     | `HAVING`     | Filtr po GROUP BY         | `(?i)HAVING`                                                   |
|                     | `ASC_DESC`   | Kierunek sortowania       | `(?i)(ASC\|DESC)`                                              |
|                     | `LIMIT`      | Limit wierszy             | ```(?i)LIMIT```                                                |
|                     | `DISTINCT`   | Wybór unikalnych wartości | ```(?i)DISTINCT```                                             |
|                     | `ALL  `      | Wybór wszystkich wartości | ```(?i)ALL```                                                  |
|                     | `JOIN_OPS`   | Typy join'ów              | ```(?i)(INNER\|LEFT\|RIGHT\|FULL(\s+OUTER)?\|CROSS)?\s*JOIN``` |
| **Operatory**       | `LOGIC_OP`   | Operatory logiczne        | ```(?i)(AND\|OR\|NOT)```                                       |
|                     | `COUNT`      | Funkcje licząca           | ```(?i)COUNT```                                                |
|                     | `SUM`        | Funkcje sumująca          | ```(?i)SUM```                                                  |
|                     | `AVG`        | Funkcje licząca średnią   | ```(?i)AVG```                                                  |
|                     | `MIN`        | Znalezienie minimum       | ```(?i)MIN```                                                  |
|                     | `MAX`        | Znalezienie maksimum      | ```(?i)MAX```                                                  |
|                     | `COMP_OP`    | Operatory porównania      | ```!=\|<>\|>=\|<=\|>\|<\|=```                                  |
|                     | `STRUCT`     | Symbole strukturalne      | ```,\|\(\|\)```                                                |
|                     | `ARYT_OP`    | Operatory arytmetyczne    | ```\+\|\-\|\/\|%```                                            |
|                     | `STAR`       | Uniwersalny znak gwiazdki | `\*`                                                           |
| **Dane (Literały)** | `ID`         | Nazwy tabel/kolumn        | `(?i)[a-z_]\w*`                                                |
|                     | `NUMBER`     | Liczby (int/float)        | `\d+(\.\d+)?`                                                  |
|                     | `STRING`     | Teksty                    | `'[^']*'`                                                      |
| **Techniczne**      | `WS`         | Białe znaki               | `\s+`                                                          |
|                     | `TERMINATOR` | Znak końca kwerendy       | `;`                                                            |

### 6. Gramatyka

  Została napisana w notacji generatora parserów ANTLR4.

```

grammar Grammar;

query
    : SELECT quantifier? select_list FROM table_list
      where_statement?
      group_by_statement?
      having_statement?
      order_by_statement?
      limit_statement?
      TERMINATOR
    ;

quantifier
    : DISTINCT | ALL
    ;

select_list
    : STAR
    | select_column (',' select_column)*
    ;

select_column
    : variable
    | aggregate_function '(' quantifier? variable ')' alias?
    ;

alias
    : AS variable
    ;

table_list
    : table_statement alias? (',' table_statement alias?)*
    ;

table_statement
    : variable (join_statement)*
    ;

join_statement
    : join_type variable ON column_reference '=' column_reference
    ;

column_reference
    : variable ('.' variable)?
    ;

join_type
    : INNER? JOIN
    | LEFT OUTER? JOIN
    | RIGHT OUTER? JOIN
    | FULL OUTER? JOIN
    ;

where_statement
    : WHERE condition
    ;

condition
    : expression ((AND | OR) expression)*
    ;

expression
    : (variable | any_type) COMP_OPERATOR (variable | any_type)
    ;

numeric_expression
    : numeric_type
    | numeric_expression ARITHMETIC_OPERATOR numeric_type
    ;

group_by_statement
    : GROUP_BY variable (',' variable)*
    ;

order_by_statement
    : ORDER_BY variable (ASC | DESC)? (',' variable (ASC | DESC)?)*
    ;

having_statement
    : HAVING having_expression ((AND | OR) having_expression)*
    ;

having_expression
    : aggregate_function '(' variable ')' COMP_OPERATOR any_type
    ;

limit_statement
    : LIMIT INTEGER
    ;

any_type
    : STRING | INTEGER | FLOAT
    ;

numeric_type
    : INTEGER | FLOAT
    ;

variable
    : ID
    ;

aggregate_function
    : MIN | MAX | COUNT | SUM | AVG
    ;

SELECT   : [sS][eE][lL][eE][cC][tT];
FROM     : [fF][rR][oO][mM];
WHERE    : [wW][hH][eE][rR][eE];
GROUP_BY : [gG][rR][oO][uU][pP] ' ' [bB][yY];
ORDER_BY : [oO][rR][dD][eE][rR] ' ' [bB][yY];
HAVING   : [hH][aA][vV][iI][nN][gG];
ASC      : [aA][sS][cC];
DESC     : [dD][eE][sS][cC];
LIMIT    : [lL][iI][mM][iI][tT];
INNER    : [iI][nN][nN][eE][rR];
OUTER    : [oO][uU][tT][eE][rR];
LEFT     : [lL][eE][fF][tT];
RIGHT    : [rR][iI][gG][hH][tT];
FULL     : [fF][uU][lL][lL];
JOIN     : [jJ][oO][iI][nN];
AND      : [aA][nN][dD];
OR       : [oO][rR];
NOT      : [nN][oO][tT];
ON       : [oO][nN];
MIN      : [mM][iI][nN];
MAX      : [mM][aA][xX];
COUNT    : [cC][oO][uU][nN][tT];
SUM      : [sS][uU][mM];
AVG      : [aA][vV][gG];

COMP_OPERATOR       : '<>' | '=' | '<' | '>' | '<=' | '>=';
ARITHMETIC_OPERATOR : '+' | '-' | '/' | '%';
AS       : [aA][sS];
DISTINCT : [dD][iI][sS][tT][iI][nN][cC][tT];
ALL      : [aA][lL][lL];

TERMINATOR : ';';

STAR : '*';

ID : [a-zA-Z] [a-zA-Z0-9_]*;

INTEGER : '-'? ([0-9] | [1-9] [0-9]*);
FLOAT : [0-9]+ '.' [0-9]+;

STRING 
    : '\'' (~['])* '\'' 
    | '"' (~["])* '"' 
    ;

WS : [ \t\r\n]+ -> skip;
```
