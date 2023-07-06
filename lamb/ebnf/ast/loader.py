import sys
from typing import Optional
from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.error.Errors import ParseCancellationException
from lamb.ebnf.ast import DocumentNode
from antlr4 import FileStream, CommonTokenStream
from lamb.ebnf.antlr.LayoutEBNFLexer import LayoutEBNFLexer
from lamb.ebnf.antlr.LayoutEBNFParser import LayoutEBNFParser
from lamb.ebnf.LayoutEBNFVisitorImpl import LayoutEBNFVisitorImpl

def load_file_into_ast(filename:str='debug/if-else.bnf') -> Optional[DocumentNode]:
    file_stream = FileStream(filename)
    lexer = LayoutEBNFLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = LayoutEBNFParser(token_stream)
    parser._errHandler = BailErrorStrategy()
    visitor = LayoutEBNFVisitorImpl()
    try:
        ast: DocumentNode = visitor.visit(parser.document()) # type: ignore
        return ast
    except ParseCancellationException:
        print('Syntax Error', file=sys.stderr)
        return None