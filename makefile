ANTLR_VERSION = 4.13.1
ANTLR_JAR     = antlr4/antlr-$(ANTLR_VERSION)-complete.jar
ANTLR_URL     = https://www.antlr.org/download/antlr-$(ANTLR_VERSION)-complete.jar
GRAMMAR       = Grammar.g4
GRAMMAR_DIR   = grammar
OUTPUT        = sql2pandas/generated

get_antlr:
	mkdir -p antlr4
	wget -O $(ANTLR_JAR) $(ANTLR_URL)

generate:
	cd $(GRAMMAR_DIR) && java -jar ../$(ANTLR_JAR) -Dlanguage=Python3 -visitor -o ../$(OUTPUT) $(GRAMMAR)

clean:
	rm -rf $(OUTPUT)/*.py $(OUTPUT)/*.tokens $(OUTPUT)/*.interp
