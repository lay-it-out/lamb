from ebnf.ast import BinaryExpressionNode, EmptyExpressionNode, RuleNode, UnaryExpressionNode, VariableExpressionNode
from typing import List, Deque, DefaultDict, Set, Tuple, Union
from collections import deque, defaultdict


def get_nullable_variables(rules: List[RuleNode]) -> Tuple[Set[str], Set[str]]:
    occurs_content_type = Union[str, Tuple[str, str]]
    nullable: Set[str] = set()
    ambig_nullable: Set[str] = set()
    todo: Deque[str] = deque()
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
        if isinstance(rule.expression, EmptyExpressionNode):
            nullable.add(rule.variable)
            todo.append(rule.variable)
    
    while len(todo):
        b = todo.popleft()
        for x in occurs[b]:
            if isinstance(x, str):
                a = x
            else:
                a, c = x
                if c not in nullable:
                    continue
            if a not in nullable:
                nullable.add(a)
                todo.append(a)
            else:
                ambig_nullable.add(a)
    
    return nullable, ambig_nullable
