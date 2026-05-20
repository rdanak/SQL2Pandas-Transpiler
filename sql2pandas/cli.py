import sys
import antlr4 as antlr
from sql2pandas.generated.GrammarLexer import GrammarLexer
from sql2pandas.generated.GrammarParser import GrammarParser
from sql2pandas.visitor import SQLToPandasVisitor


def transpile(sql: str) -> str:
    stream  = antlr.InputStream(sql)
    lexer   = GrammarLexer(stream)
    tokens  = antlr.CommonTokenStream(lexer)
    parser  = GrammarParser(tokens)
    tree    = parser.statement() # This will need to change once the grammar has a new entry point (yeah, it truly did change after all)

    visitor = SQLToPandasVisitor()
    return visitor.visit(tree)


def main():
    if len(sys.argv) < 2:
        print("Usage: sql2pandas <input.sql> [-o output.py]")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r") as f:
        sql = f.read()

    result = transpile(sql)

    if "-o" in sys.argv:
        output_file = sys.argv[sys.argv.index("-o") + 1]
        with open(output_file, "w") as f:
            f.write(result)
        print(f"Written to {output_file}")
    else:
        print(result)


if __name__ == "__main__":
    main()
