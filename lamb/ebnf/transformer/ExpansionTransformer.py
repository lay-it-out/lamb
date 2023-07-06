from typing import List

from lamb.ebnf.ast import *


def expand_rules(rules: List[RuleNode]) -> List[RuleNode]:
    ret = []
    for rule in rules:
        if isinstance(rule.expression, BinaryExpressionNode) \
                and rule.expression.op == BinaryExpressionNode.BinaryOp.OrOp:

            ret.append(RuleNode(
                rule.variable,
                rule.expression.expr1,
                original_text=f'{rule.variable} ::= {rule.expression.expr1.original_text}',
                tree_id=rule.expression.expr1.tree_id
            ))
            ret.append(RuleNode(
                rule.variable,
                rule.expression.expr2,
                original_text=f'{rule.variable} ::= {rule.expression.expr2.original_text}',
                tree_id=rule.expression.expr2.tree_id
            ))
        else:
            ret.append(rule)
    return ret
