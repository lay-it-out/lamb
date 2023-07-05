from ebnf.ast import *
from typing import List, Optional
from ebnf.antlr.LayoutEBNFParser import LayoutEBNFParser
from .antlr.LayoutEBNFVisitor import LayoutEBNFVisitor

class LayoutEBNFVisitorImpl(LayoutEBNFVisitor):

    @staticmethod
    def extract_original_text(ctx):
        token_source = ctx.start.getTokenSource()
        input_stream = token_source.inputStream
        start, stop  = ctx.start.start, ctx.stop.stop
        return input_stream.getText(start, stop)

    # Visit a parse tree produced by LayoutEBNFParser#document.
    def visitDocument(self, ctx: Optional[LayoutEBNFParser.DocumentContext]):
        rules: Optional[List] = ctx.ruleItem()
        document_node = DocumentNode()

        for rule_ctx in rules:
            rule_node = self.visitRuleItem(rule_ctx)
            document_node.append_rule(rule_node)

        return document_node

    # Visit a parse tree produced by LayoutEBNFParser#ruleItem.
    def visitRuleItem(self, ctx: LayoutEBNFParser.RuleItemContext):
        expr_node = self.visitExpr(ctx.expr())
        return RuleNode(ctx.NonTerminal().getText(), expr_node,
            original_text=LayoutEBNFVisitorImpl.extract_original_text(ctx))

    # Visit a parse tree produced by LayoutEBNFParser#expr.
    def visitExpr(self, ctx: LayoutEBNFParser.ExprContext) -> Optional[ExpressionNode]:
        subexpr = ctx.expr()
        if not subexpr:
            if ctx.NonTerminal() is not None:
                return VariableExpressionNode(ctx.NonTerminal().getText())
            elif ctx.StringLiteral() is not None:
                literal = ctx.StringLiteral().getText()
                return LiteralExpressionNode(literal[1:-1])
        elif len(subexpr) == 1:
            if ctx.LBracket() is not None:  # bracket
                return self.visitExpr(subexpr[0])
            else:  # unary operator
                return UnaryExpressionNode(
                    self.visitExpr(subexpr[0]),
                    UnaryExpressionNode.UnaryOp(ctx.unaryop().getText()),
                    original_text=LayoutEBNFVisitorImpl.extract_original_text(ctx)
                )
        elif len(subexpr) == 2:
            if ctx.binaryop() is not None:
                op_text = ctx.binaryop().getText()
                if op_text == '<>': op_text = '||'
                binop = BinaryExpressionNode.BinaryOp(op_text)
            else:
                binop = BinaryExpressionNode.BinaryOp.ConcatOp
            return BinaryExpressionNode(
                self.visitExpr(subexpr[0]),
                self.visitExpr(subexpr[1]),
                binop,
                original_text=LayoutEBNFVisitorImpl.extract_original_text(ctx)
            )
        else:
            return None


del LayoutEBNFParser
