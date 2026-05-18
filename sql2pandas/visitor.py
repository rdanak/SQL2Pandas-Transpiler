from sql2pandas.generated.GrammarVisitor import GrammarVisitor
from sql2pandas.generated.GrammarParser import GrammarParser

class SQLToPandasVisitor(GrammarVisitor):
    def visitQuery(self, ctx):
        table      = self.visit(ctx.table_list())
        select     = self.visit(ctx.select_list())
        quantifier = self.visit(ctx.quantifier()) if ctx.quantifier() else None
        condition  = self.visit(ctx.where_statement())    if ctx.where_statement()    else None
        groupby    = self.visit(ctx.group_by_statement()) if ctx.group_by_statement() else None
        having     = self.visit(ctx.having_statement())   if ctx.having_statement()   else None
        orderby    = self.visit(ctx.order_by_statement()) if ctx.order_by_statement() else None
        limit      = self.visit(ctx.limit_statement())    if ctx.limit_statement()    else None

        lines = []
        lines.append(f"df = {table}")

        if condition:
            lines.append(f"df = df[{condition}]")

        if groupby:
            lines.append(f"df = df.groupby({groupby})")
            if select["type"] == "agg":
                lines.append(f"df = df.agg({select['aggs']})")
                if select["aliases"]:
                    lines.append(f"df = df.rename(columns={select['aliases']})")
        else:
            if select["type"] == "cols":
                if quantifier == "DISTINCT":
                    lines.append(f"df = df[{select['columns']}].drop_duplicates()")
                else:
                    lines.append(f"df = df[{select['columns']}]")
            elif select["type"] == "star":
                if quantifier == "DISTINCT":
                    lines.append(f"df = df.drop_duplicates()")
            elif select["type"] == "agg":
                lines.append(f"df = df.agg({select['aggs']})")
                if select["aliases"]:
                    lines.append(f"df = df.rename(columns={select['aliases']})")

        if having:
            lines.append(f"df = df.filter(lambda df: {having})")
        if orderby:
            lines.append(f"df = df.sort_values({orderby})")
        if limit:
            lines.append(f"df = df.head({limit})")

        return "\n".join(lines)

    def visitQuantifier(self, ctx):
        return ctx.getText().upper()

    def visitSelect_list(self, ctx):
        if ctx.STAR():
            return {"type": "star"}
        
        columns = []
        aggs    = {}
        aliases = {}

        for col in ctx.select_column():
            result = self.visit(col)
            if isinstance(result, tuple):
                agg_func, col_name, alias = result
                aggs[col_name] = agg_func
                if alias:
                    aliases[col_name] = alias
            else:
                columns.append(result)

        return {"type": "agg" if aggs else "cols", "columns": columns, "aggs": aggs, "aliases": aliases}

    def visitSelect_column(self, ctx):
        if ctx.aggregate_function():
            agg   = self.visit(ctx.aggregate_function())
            col   = self.visit(ctx.column_reference()) if ctx.column_reference() else "*"
            alias = self.visit(ctx.alias()) if ctx.alias() else None
            return (agg, col, alias)

        col   = self.visit(ctx.expression())
        return col

    def visitAlias(self, ctx):
        return self.visit(ctx.variable())

    def visitColumn_reference(self, ctx):
        if ctx.DOT():
            return f"{ctx.variable(0).getText()}.{ctx.variable(1).getText()}"
        return self.visit(ctx.variable(0))

    def visitTable_list(self, ctx):
        return self.visit(ctx.table_statement(0))

    def visitTable_statement(self, ctx):
        table = self.visit(ctx.variable())
        
        for join in ctx.join_statement():
            table += self.visit(join)
        
        return table

    def visitJoin_statement(self, ctx):
        join_type = self.visit(ctx.join_type())
        table     = self.visit(ctx.variable())
        left_col  = self.visit(ctx.condition().expression().operand(0))
        right_col = self.visit(ctx.condition().expression().operand(1))
        return f".merge({table}, how='{join_type}', left_on='{left_col}', right_on='{right_col}')"

    def visitJoin_type(self, ctx):
        if ctx.LEFT():   return "left"
        if ctx.RIGHT():  return "right"
        if ctx.FULL():   return "outer"
        if ctx.CROSS():  return "cross"
        return "inner"

    def visitWhere_statement(self, ctx):
        return self.visit(ctx.condition())

    def visitOrCondition(self, ctx):
        left  = self.visit(ctx.condition(0))
        right = self.visit(ctx.condition(1))
        return f"({left}) | ({right})"

    def visitAndCondition(self, ctx):
        left  = self.visit(ctx.condition(0))
        right = self.visit(ctx.condition(1))
        return f"({left}) & ({right})"

    def visitNotCondition(self, ctx):
        return f"~({self.visit(ctx.condition())})"

    def visitParenCondition(self, ctx):
        return self.visit(ctx.condition())

    def visitExprCondition(self, ctx):
        return self.visit(ctx.expression())

    def visitCompExpr(self, ctx):
        left  = self.visit(ctx.operand(0))
        right = self.visit(ctx.operand(1))
        op    = ctx.COMP_OPERATOR().getText()
        op    = "==" if op == "=" else op
        return f"df['{left}'] {op} {right}"

    def visitNullExpr(self, ctx):
        col = self.visit(ctx.operand())
        if ctx.NOT():
            return f"df['{col}'].notna()"
        return f"df['{col}'].isna()"

    def visitBetweenExpr(self, ctx):
        col   = self.visit(ctx.operand(0))
        low   = self.visit(ctx.operand(1))
        high  = self.visit(ctx.operand(2))
        if ctx.NOT():
            return f"~df['{col}'].between({low}, {high})"
        return f"df['{col}'].between({low}, {high})"

    def visitLikeExpr(self, ctx):
        col     = self.visit(ctx.operand())
        pattern = ctx.STRING().getText().strip("'\"")
        pattern = pattern.replace("%", ".*").replace("_", ".")
        if ctx.NOT():
            return f"~df['{col}'].str.match('{pattern}')"
        return f"df['{col}'].str.match('{pattern}')"

    def visitInExpr(self, ctx):
        col    = self.visit(ctx.operand())
        values = self.visit(ctx.value_list())
        if ctx.NOT():
            return f"~df['{col}'].isin({values})"
        return f"df['{col}'].isin({values})"

    def visitSimpleExpr(self, ctx):
        return self.visit(ctx.operand())

    def visitArithOperand(self, ctx):
        left  = self.visit(ctx.operand(0))
        right = self.visit(ctx.operand(1))
        op    = ctx.ARITHMETIC_OPERATOR().getText()
        return f"{left} {op} {right}"

    def visitParenOperand(self, ctx):
        return f"({self.visit(ctx.operand())})"

    def visitAggOperand(self, ctx):
        agg = self.visit(ctx.aggregate_function())
        col = self.visit(ctx.column_reference()) if ctx.column_reference() else "*"
        return f"{agg}({col})"

    def visitColOperand(self, ctx):
        return self.visit(ctx.column_reference())

    def visitLitOperand(self, ctx):
        return self.visit(ctx.literal())

    def visitValue_list(self, ctx):
        values = [self.visit(lit) for lit in ctx.literal()]
        return str(values)

    def visitGroup_by_statement(self, ctx):
        columns = [self.visit(col) for col in ctx.column_reference()]
        return str(columns)

    def visitHaving_statement(self, ctx):
        return self.visit(ctx.condition())

    def visitOrder_by_statement(self, ctx):
        columns   = [self.visit(item.column_reference()) for item in ctx.order_item()]
        ascending = [not bool(item.DESC()) for item in ctx.order_item()]
        return f"{columns}, ascending={ascending}"

    def visitOrder_item(self, ctx):
        return self.visit(ctx.column_reference())

    def visitLimit_statement(self, ctx):
        return ctx.INTEGER(0).getText()

    def visitLiteral(self, ctx:GrammarParser.LiteralContext):
        if ctx.STRING():
            return ctx.STRING().getText()
        elif ctx.number():
            return self.visit(ctx.number())
        elif ctx.TRUE():
            return "True"
        elif ctx.FALSE():
            return "False"
        elif ctx.NULL_():
            return "None"

    def visitNumber(self, ctx:GrammarParser.NumberContext):
        sign = "-" if ctx.MINUS() else ""
        value = ctx.INTEGER().getText() if ctx.INTEGER() else ctx.FLOAT().getText()
        return sign + value

    def visitAggregate_function(self, ctx:GrammarParser.Aggregate_functionContext):
        match ctx.getText().upper():
            case "MIN":   return "min"
            case "MAX":   return "max"
            case "COUNT": return "count"
            case "SUM":   return "sum"
            case "AVG":   return "mean"

    def visitVariable(self, ctx:GrammarParser.VariableContext):
        return ctx.ID().getText()
