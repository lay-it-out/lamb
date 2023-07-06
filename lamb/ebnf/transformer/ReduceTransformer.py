""" Run after DESUGAR and EXPANSION.
Rules has subexpressions of type VariableExpressionNode, BinaryExpressionNode and UnaryExpressionNode
"""
from collections import defaultdict, deque
from typing import DefaultDict, Deque, List, Set, Tuple, Union

from lamb.ebnf.ast import BinaryExpressionNode, EmptyExpressionNode, LeafNode, LiteralExpressionNode, RuleNode, \
    UnaryExpressionNode, VariableExpressionNode


def calculate_reachable(rules: List[RuleNode]):
    assert len(rules) > 0
    todo: Deque[str] = deque()
    rule_dict: DefaultDict[str, List[RuleNode]] = defaultdict(list)
    reachable: Set[str] = set()

    for rule in rules: rule_dict[rule.variable].append(rule)
    reachable.add(rules[0].variable)
    todo.append(rules[0].variable)
    while len(todo):
        u = todo.popleft()
        for rule in rule_dict[u]:
            if isinstance(rule.expression, VariableExpressionNode):
                if rule.expression.variable in reachable: continue
                reachable.add(rule.expression.variable)
                todo.append(rule.expression.variable)
            elif not isinstance(rule.expression, LeafNode):
                assert isinstance(rule.expression, BinaryExpressionNode) \
                       or isinstance(rule.expression, UnaryExpressionNode)
                for x in rule.expression.children():
                    assert isinstance(x, VariableExpressionNode)
                    if x.variable in reachable: continue
                    reachable.add(x.variable)
                    todo.append(x.variable)

    return [x for x in rules if x.variable in reachable]


def calculate_generating(rules: List[RuleNode]):
    assert len(rules) > 0
    todo: Deque[str] = deque()
    generating: Set[str] = set()
    occurs_content_type = Union[str, Tuple[str, str]]
    occurs: DefaultDict[str, List[occurs_content_type]] = defaultdict(list)

    for rule in rules:
        if isinstance(rule.expression, VariableExpressionNode):
            occurs[rule.expression.variable].append(rule.variable)
        elif isinstance(rule.expression, UnaryExpressionNode):
            assert isinstance(rule.expression.expr, VariableExpressionNode)
            occurs[rule.expression.expr.variable].append(rule.variable)
    for rule in rules:
        if isinstance(rule.expression, BinaryExpressionNode):
            b = rule.expression.expr1
            c = rule.expression.expr2
            assert isinstance(b, VariableExpressionNode) and isinstance(c, VariableExpressionNode)
            occurs[b.variable].append((rule.variable, c.variable))
            occurs[c.variable].append((rule.variable, b.variable))
    for rule in rules:
        if isinstance(rule.expression, LiteralExpressionNode) or isinstance(rule.expression, EmptyExpressionNode):
            generating.add(rule.variable)
            todo.append(rule.variable)

    while len(todo):
        b = todo.popleft()
        for x in occurs[b]:
            if isinstance(x, str):
                a = x
            else:
                a, c = x
                if c not in generating: continue
            if a not in generating:
                generating.add(a)
                todo.append(a)

    ret = []
    for rule in rules:
        if rule.variable not in generating: continue
        if isinstance(rule.expression, VariableExpressionNode) \
                and rule.expression.variable not in generating: continue
        if (isinstance(rule.expression, BinaryExpressionNode) or isinstance(rule.expression, UnaryExpressionNode)):
            violating_children = [x for x in rule.expression.children() if x.variable not in generating]
            if len(violating_children) > 0: continue
        ret.append(rule)
    return ret


def reduce_rules(rules: List[RuleNode]) -> List[RuleNode]:
    rules = calculate_generating(rules)
    rules = calculate_reachable(rules)
    return rules
