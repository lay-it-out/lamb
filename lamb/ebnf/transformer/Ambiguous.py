from typing import List, Set

from lamb.ebnf.ast import RuleNode, VariableExpressionNode


def get_nonempty_ambiguous_symbols(rules: List[RuleNode]) -> Set[str]:
    ret: Set[str] = set()

    for rule in rules:
        if isinstance(rule.expression, VariableExpressionNode) \
                and rule.variable == rule.expression.variable:
            ret.add(rule.variable)

    return ret
