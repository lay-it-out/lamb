# Generated from ./LayoutEBNF.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LayoutEBNFParser import LayoutEBNFParser
else:
    from LayoutEBNFParser import LayoutEBNFParser

# This class defines a complete generic visitor for a parse tree produced by LayoutEBNFParser.

class LayoutEBNFVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LayoutEBNFParser#document.
    def visitDocument(self, ctx:LayoutEBNFParser.DocumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LayoutEBNFParser#ruleItem.
    def visitRuleItem(self, ctx:LayoutEBNFParser.RuleItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LayoutEBNFParser#expr.
    def visitExpr(self, ctx:LayoutEBNFParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LayoutEBNFParser#unaryop.
    def visitUnaryop(self, ctx:LayoutEBNFParser.UnaryopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LayoutEBNFParser#binaryop.
    def visitBinaryop(self, ctx:LayoutEBNFParser.BinaryopContext):
        return self.visitChildren(ctx)



del LayoutEBNFParser