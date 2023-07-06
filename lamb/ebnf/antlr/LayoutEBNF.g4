grammar LayoutEBNF;

document : (ruleItem? SEMICOLON)* (ruleItem SEMICOLON?)? EOF;
ruleItem : NonTerminal GeneratingOp expr;

expr : NonTerminal
     | StringLiteral
     | LBracket expr RBracket
     | expr unaryop
     | expr expr // concat
     | expr binaryop expr 
     ;

unaryop : KleenePlus | KleeneStar | Optional | SameLineOp 
         | OffsideOp | OffsideEquOp | AlignedKleenePlus | AlignedKleeneStar;
binaryop : IndentOp | StartSameLineOp | AlignOp | OrOp;

WHITESPACE : [\t ]+ -> channel(HIDDEN);

CRLF : ('\r' '\n'? | '\n') -> skip;
SEMICOLON : ';';

GeneratingOp : '::=';
IndentOp : '->';
StartSameLineOp : '|~';
AlignOp : '<>' | '||';
OffsideOp : '|>';
OffsideEquOp : '>>';
SameLineOp: '~';
OrOp : '|';
KleenePlus : '+';
KleeneStar : '*';
Optional : '?';
AlignedKleenePlus : '|+|';
AlignedKleeneStar : '|*|';
LBracket : '(';
RBracket : ')';

StringLiteral : StringLiteralDQuote | StringLiteralSQuote;

fragment StringLiteralDQuote : '"' SCharInDQuote* '"';
fragment StringLiteralSQuote : '\'' SCharInSQuote* '\'';

fragment SCharInDQuote : SCharRaw | '\'';
fragment SCharInSQuote : SCharRaw | '"';
fragment SCharRaw : ~["'\\\r\n] | EscapeSequence;
fragment EscapeSequence : '\\' ['"?abfnrtv\\];

NonTerminal : IdentChar+;

fragment IdentChar : ('a'..'z') | ('A'..'Z') | ('0'..'9') | '-';

LineComment : '//' ~[\r\n]* -> channel(HIDDEN);
BlockComment : '/*' .*? '*/' -> channel(HIDDEN);
