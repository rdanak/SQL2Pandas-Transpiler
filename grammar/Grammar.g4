grammar Grammar;

// ─────────────────────────────────────────
//  PARSER RULES
// ─────────────────────────────────────────

statement
    : query
    | create_table_statement
    ;

// CREATE TABLE

create_table_statement
    : CREATE TABLE variable LPAREN column_definition (COMMA column_definition)* RPAREN TERMINATOR?
    ;

column_definition
    : variable data_type
    ;

data_type
    : INT_TYPE | VARCHAR | FLOAT_TYPE
    ;

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

// ─────────────────────────────────────────
//  LEXER RULES  
// ─────────────────────────────────────────

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
CREATE  : [cC][rR][eE][aA][tT][eE];
TABLE   : [tT][aA][bB][lL][eE];    

// datatypes

INT_TYPE   : [iI][nN][tT];
VARCHAR    : [vV][aA][rR][cC][hH][aA][rR];
FLOAT_TYPE : [fF][lL][oO][aA][tT];

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
