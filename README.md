# SQL2Pandas-Transpiler
---
- Marcin Dutka *`marcindutka@student.agh.edu.pl`*
- Robert Danak *`rdanak@student.agh.edu.pl`*
---
### 1. Cel Projektu:
  Budowa ***transpilera***, który przyjmuje zapytanie **SQL** (określony podzbiór języka) i generuje kod w języku **Python** przy wykorzystaniu biblioteki **Pandas** do operacji na strukturach danych typu DataFrame.
### 2. Rodzaj translatora:
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
|                     | `JOIN_OPS`   | Typy join'ów              | ```(?i)(INNER\|LEFT\|RIGHT\|FULL(\s+OUTER)?\|CROSS)?\s*JOIN``` |
| **Operatory**       | `LOGIC_OP`   | Operatory logiczne        | ```(?i)(AND\|OR\|NOT)```                                       |
|                     | `AGG_FUNC`   | Funkcje agregujące        | ```(?i)(COUNT\|SUM\|AVG\|MIN\|MAX)```                          |
|                     | `COMP_OP`    | Operatory porównania      | ```!=\|<>\|>=\|<=\|>\|<\|=```                                  |
|                     | `STRUCT`     | Symbole strukturalne      | ```,\|\(\|\)```                                                |
|                     | `ARYT_OP`    | Operatory arytmetyczne    | ```\+\|\-\|\/\|%```                                            |
|                     | `STAR`       | Uniwersalny znak gwiazdki | `\*`                                                           |
| **Dane (Literały)** | `ID`         | Nazwy tabel/kolumn        | `(?i)[a-z_]\w*`                                                |
|                     | `NUMBER`     | Liczby (int/float)        | `\d+(\.\d+)?`                                                  |
|                     | `STRING`     | Teksty                    | `'[^']*'`                                                      |
| **Techniczne**      | `WS`         | Białe znaki               | `\s+`                                                          |
