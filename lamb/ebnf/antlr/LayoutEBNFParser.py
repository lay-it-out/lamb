# Generated from ./LayoutEBNF.g4 by ANTLR 4.10.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,22,58,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,3,0,12,8,0,
        1,0,5,0,15,8,0,10,0,12,0,18,9,0,1,0,1,0,3,0,22,8,0,3,0,24,8,0,1,
        0,1,0,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,39,8,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,5,2,49,8,2,10,2,12,2,52,9,2,1,3,1,3,
        1,4,1,4,1,4,0,1,4,5,0,2,4,6,8,0,2,2,0,8,10,12,16,2,0,5,7,11,11,61,
        0,16,1,0,0,0,2,27,1,0,0,0,4,38,1,0,0,0,6,53,1,0,0,0,8,55,1,0,0,0,
        10,12,3,2,1,0,11,10,1,0,0,0,11,12,1,0,0,0,12,13,1,0,0,0,13,15,5,
        3,0,0,14,11,1,0,0,0,15,18,1,0,0,0,16,14,1,0,0,0,16,17,1,0,0,0,17,
        23,1,0,0,0,18,16,1,0,0,0,19,21,3,2,1,0,20,22,5,3,0,0,21,20,1,0,0,
        0,21,22,1,0,0,0,22,24,1,0,0,0,23,19,1,0,0,0,23,24,1,0,0,0,24,25,
        1,0,0,0,25,26,5,0,0,1,26,1,1,0,0,0,27,28,5,20,0,0,28,29,5,4,0,0,
        29,30,3,4,2,0,30,3,1,0,0,0,31,32,6,2,-1,0,32,39,5,20,0,0,33,39,5,
        19,0,0,34,35,5,17,0,0,35,36,3,4,2,0,36,37,5,18,0,0,37,39,1,0,0,0,
        38,31,1,0,0,0,38,33,1,0,0,0,38,34,1,0,0,0,39,50,1,0,0,0,40,41,10,
        2,0,0,41,49,3,4,2,3,42,43,10,1,0,0,43,44,3,8,4,0,44,45,3,4,2,2,45,
        49,1,0,0,0,46,47,10,3,0,0,47,49,3,6,3,0,48,40,1,0,0,0,48,42,1,0,
        0,0,48,46,1,0,0,0,49,52,1,0,0,0,50,48,1,0,0,0,50,51,1,0,0,0,51,5,
        1,0,0,0,52,50,1,0,0,0,53,54,7,0,0,0,54,7,1,0,0,0,55,56,7,1,0,0,56,
        9,1,0,0,0,7,11,16,21,23,38,48,50
    ]

class LayoutEBNFParser ( Parser ):

    grammarFileName = "LayoutEBNF.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "';'", "'::='", 
                     "'->'", "'|~'", "<INVALID>", "'|>'", "'>>'", "'~'", 
                     "'|'", "'+'", "'*'", "'?'", "'|+|'", "'|*|'", "'('", 
                     "')'" ]

    symbolicNames = [ "<INVALID>", "WHITESPACE", "CRLF", "SEMICOLON", "GeneratingOp", 
                      "IndentOp", "StartSameLineOp", "AlignOp", "OffsideOp", 
                      "OffsideEquOp", "SameLineOp", "OrOp", "KleenePlus", 
                      "KleeneStar", "Optional", "AlignedKleenePlus", "AlignedKleeneStar", 
                      "LBracket", "RBracket", "StringLiteral", "NonTerminal", 
                      "LineComment", "BlockComment" ]

    RULE_document = 0
    RULE_ruleItem = 1
    RULE_expr = 2
    RULE_unaryop = 3
    RULE_binaryop = 4

    ruleNames =  [ "document", "ruleItem", "expr", "unaryop", "binaryop" ]

    EOF = Token.EOF
    WHITESPACE=1
    CRLF=2
    SEMICOLON=3
    GeneratingOp=4
    IndentOp=5
    StartSameLineOp=6
    AlignOp=7
    OffsideOp=8
    OffsideEquOp=9
    SameLineOp=10
    OrOp=11
    KleenePlus=12
    KleeneStar=13
    Optional=14
    AlignedKleenePlus=15
    AlignedKleeneStar=16
    LBracket=17
    RBracket=18
    StringLiteral=19
    NonTerminal=20
    LineComment=21
    BlockComment=22

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DocumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(LayoutEBNFParser.EOF, 0)

        def SEMICOLON(self, i:int=None):
            if i is None:
                return self.getTokens(LayoutEBNFParser.SEMICOLON)
            else:
                return self.getToken(LayoutEBNFParser.SEMICOLON, i)

        def ruleItem(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LayoutEBNFParser.RuleItemContext)
            else:
                return self.getTypedRuleContext(LayoutEBNFParser.RuleItemContext,i)


        def getRuleIndex(self):
            return LayoutEBNFParser.RULE_document

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDocument" ):
                listener.enterDocument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDocument" ):
                listener.exitDocument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDocument" ):
                return visitor.visitDocument(self)
            else:
                return visitor.visitChildren(self)




    def document(self):

        localctx = LayoutEBNFParser.DocumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_document)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 11
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==LayoutEBNFParser.NonTerminal:
                        self.state = 10
                        self.ruleItem()


                    self.state = 13
                    self.match(LayoutEBNFParser.SEMICOLON) 
                self.state = 18
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 23
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==LayoutEBNFParser.NonTerminal:
                self.state = 19
                self.ruleItem()
                self.state = 21
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==LayoutEBNFParser.SEMICOLON:
                    self.state = 20
                    self.match(LayoutEBNFParser.SEMICOLON)




            self.state = 25
            self.match(LayoutEBNFParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RuleItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NonTerminal(self):
            return self.getToken(LayoutEBNFParser.NonTerminal, 0)

        def GeneratingOp(self):
            return self.getToken(LayoutEBNFParser.GeneratingOp, 0)

        def expr(self):
            return self.getTypedRuleContext(LayoutEBNFParser.ExprContext,0)


        def getRuleIndex(self):
            return LayoutEBNFParser.RULE_ruleItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRuleItem" ):
                listener.enterRuleItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRuleItem" ):
                listener.exitRuleItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRuleItem" ):
                return visitor.visitRuleItem(self)
            else:
                return visitor.visitChildren(self)




    def ruleItem(self):

        localctx = LayoutEBNFParser.RuleItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_ruleItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self.match(LayoutEBNFParser.NonTerminal)
            self.state = 28
            self.match(LayoutEBNFParser.GeneratingOp)
            self.state = 29
            self.expr(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NonTerminal(self):
            return self.getToken(LayoutEBNFParser.NonTerminal, 0)

        def StringLiteral(self):
            return self.getToken(LayoutEBNFParser.StringLiteral, 0)

        def LBracket(self):
            return self.getToken(LayoutEBNFParser.LBracket, 0)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LayoutEBNFParser.ExprContext)
            else:
                return self.getTypedRuleContext(LayoutEBNFParser.ExprContext,i)


        def RBracket(self):
            return self.getToken(LayoutEBNFParser.RBracket, 0)

        def binaryop(self):
            return self.getTypedRuleContext(LayoutEBNFParser.BinaryopContext,0)


        def unaryop(self):
            return self.getTypedRuleContext(LayoutEBNFParser.UnaryopContext,0)


        def getRuleIndex(self):
            return LayoutEBNFParser.RULE_expr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr" ):
                listener.enterExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr" ):
                listener.exitExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpr" ):
                return visitor.visitExpr(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = LayoutEBNFParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 4
        self.enterRecursionRule(localctx, 4, self.RULE_expr, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 38
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [LayoutEBNFParser.NonTerminal]:
                self.state = 32
                self.match(LayoutEBNFParser.NonTerminal)
                pass
            elif token in [LayoutEBNFParser.StringLiteral]:
                self.state = 33
                self.match(LayoutEBNFParser.StringLiteral)
                pass
            elif token in [LayoutEBNFParser.LBracket]:
                self.state = 34
                self.match(LayoutEBNFParser.LBracket)
                self.state = 35
                self.expr(0)
                self.state = 36
                self.match(LayoutEBNFParser.RBracket)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 50
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 48
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
                    if la_ == 1:
                        localctx = LayoutEBNFParser.ExprContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 40
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 41
                        self.expr(3)
                        pass

                    elif la_ == 2:
                        localctx = LayoutEBNFParser.ExprContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 42
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 43
                        self.binaryop()
                        self.state = 44
                        self.expr(2)
                        pass

                    elif la_ == 3:
                        localctx = LayoutEBNFParser.ExprContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 46
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 47
                        self.unaryop()
                        pass

             
                self.state = 52
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class UnaryopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def KleenePlus(self):
            return self.getToken(LayoutEBNFParser.KleenePlus, 0)

        def KleeneStar(self):
            return self.getToken(LayoutEBNFParser.KleeneStar, 0)

        def Optional(self):
            return self.getToken(LayoutEBNFParser.Optional, 0)

        def SameLineOp(self):
            return self.getToken(LayoutEBNFParser.SameLineOp, 0)

        def OffsideOp(self):
            return self.getToken(LayoutEBNFParser.OffsideOp, 0)

        def OffsideEquOp(self):
            return self.getToken(LayoutEBNFParser.OffsideEquOp, 0)

        def AlignedKleenePlus(self):
            return self.getToken(LayoutEBNFParser.AlignedKleenePlus, 0)

        def AlignedKleeneStar(self):
            return self.getToken(LayoutEBNFParser.AlignedKleeneStar, 0)

        def getRuleIndex(self):
            return LayoutEBNFParser.RULE_unaryop

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnaryop" ):
                listener.enterUnaryop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnaryop" ):
                listener.exitUnaryop(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryop" ):
                return visitor.visitUnaryop(self)
            else:
                return visitor.visitChildren(self)




    def unaryop(self):

        localctx = LayoutEBNFParser.UnaryopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_unaryop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << LayoutEBNFParser.OffsideOp) | (1 << LayoutEBNFParser.OffsideEquOp) | (1 << LayoutEBNFParser.SameLineOp) | (1 << LayoutEBNFParser.KleenePlus) | (1 << LayoutEBNFParser.KleeneStar) | (1 << LayoutEBNFParser.Optional) | (1 << LayoutEBNFParser.AlignedKleenePlus) | (1 << LayoutEBNFParser.AlignedKleeneStar))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BinaryopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IndentOp(self):
            return self.getToken(LayoutEBNFParser.IndentOp, 0)

        def StartSameLineOp(self):
            return self.getToken(LayoutEBNFParser.StartSameLineOp, 0)

        def AlignOp(self):
            return self.getToken(LayoutEBNFParser.AlignOp, 0)

        def OrOp(self):
            return self.getToken(LayoutEBNFParser.OrOp, 0)

        def getRuleIndex(self):
            return LayoutEBNFParser.RULE_binaryop

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBinaryop" ):
                listener.enterBinaryop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBinaryop" ):
                listener.exitBinaryop(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBinaryop" ):
                return visitor.visitBinaryop(self)
            else:
                return visitor.visitChildren(self)




    def binaryop(self):

        localctx = LayoutEBNFParser.BinaryopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_binaryop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << LayoutEBNFParser.IndentOp) | (1 << LayoutEBNFParser.StartSameLineOp) | (1 << LayoutEBNFParser.AlignOp) | (1 << LayoutEBNFParser.OrOp))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[2] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 1)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 3)
         




