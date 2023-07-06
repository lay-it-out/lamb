from typing import Any, DefaultDict, Dict, Tuple

from pysmt.shortcuts import TRUE, FALSE, FreshSymbol, And, Or, Iff, Not, Equals, Int, get_formula_size

from lamb.ebnf.ast import *
from lamb.interaction.metric_printer import print_metric
from lamb.utils.SymbolIdMapper import SymbolIdMapper
from lamb.verification.predicate import get_predicate_for_rule


def at_least_two_holds(xs):
    if len(xs) and isinstance(xs[0], tuple):
        xs = [x[0] for x in xs]
    u = [FreshSymbol() for i in range(len(xs))]
    v = [FreshSymbol() for i in range(len(xs))]

    if len(xs) < 2: return FALSE()

    ret = TRUE()

    ret = And(ret, Iff(u[0], xs[0]))
    ret = And(ret, Not(v[0]))
    ret = And(ret, v[-1])
    for i in range(1, len(xs)):
        ret = And(ret, Iff(u[i], Or(u[i - 1], xs[i])))
        ret = And(ret, Iff(v[i], Or(v[i - 1], And(u[i - 1], xs[i]))))

    return ret


def generate_non_trivial_ambiguity_condition(
        rule_dict: DefaultDict[str, List[RuleNode]],
        i: int, j: int,
        variables: Dict,
        mapper: SymbolIdMapper,
        nullable: Set[str],
        A: str
) -> List:
    ret = []

    if i == j:
        for rule in rule_dict[A]:
            if isinstance(rule.expression, LiteralExpressionNode):
                index_a = mapper.get_id_for_literal(rule.expression.content)
                ret.append((Equals(variables[f'x${i}'], Int(index_a)),
                            f'Single token: {rule.original_text} => {A} ::= {rule.expression.content}'))
    for rule in rule_dict[A]:
        if isinstance(rule.expression, UnaryExpressionNode):
            assert rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideOp \
                   or rule.expression.op == UnaryExpressionNode.UnaryOp.SameLineOp \
                   or rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideEquOp
            assert isinstance(rule.expression.expr, VariableExpressionNode)
            B = rule.expression.expr.variable
            B_index = mapper.get_id_for_variable(B)
            ret.append((
                And(
                    variables[f'x${i}${j}${B_index}'],
                    get_predicate_for_rule(rule, variables, i, j)
                ),
                f'Unary Operator Expression: {rule.original_text} => {A} ::= ({rule.expression.expr.variable}){rule.expression.op}'
            ))
        elif isinstance(rule.expression, VariableExpressionNode):
            B = rule.expression.variable
            B_index = mapper.get_id_for_variable(B)
            ret.append((variables[f'x${i}${j}${B_index}'],
                        f'Unit expression: {rule.original_text} => {A} ::= {rule.expression.variable}'))
        elif isinstance(rule.expression, BinaryExpressionNode):
            assert isinstance(rule.expression.expr1, VariableExpressionNode)
            assert isinstance(rule.expression.expr2, VariableExpressionNode)
            B, C = rule.expression.expr1.variable, rule.expression.expr2.variable
            op = rule.expression.op
            B_index = mapper.get_id_for_variable(B)
            C_index = mapper.get_id_for_variable(C)

            if C in nullable:
                ret.append((variables[f'x${i}${j}${B_index}'],
                            f'Rule like A::=B op C with nullable C: {rule.original_text} => {A} ::= {B} {op.value} {C}'))
            if B in nullable:
                ret.append((variables[f'x${i}${j}${C_index}'],
                            f'Rule like A::=B op C with nullable B: {rule.original_text} => {A} ::= {B} {op.value} {C}'))

            for h in range(i, j):
                cond1 = (variables[f'x${i}${h}${B_index}'])
                cond2 = (variables[f'x${h + 1}${j}${C_index}'])
                cond3 = get_predicate_for_rule(rule, variables, i, h + 1)
                ret.append((And(cond1, cond2, cond3),
                            f'Rule like A::=B op C with non-null B&C, splitted as [{i},{h}],[{h + 1},{j}]: {rule.original_text} => {A} ::= {B} {op.value} {C}'))

    return ret


def build_ambiguity_condition(
        rule_dict: DefaultDict[str, List[RuleNode]], n: int, variables: Dict,
        mapper: SymbolIdMapper, nullable: Set[str], ambiguously_nullable: Set[str]
) -> List[Tuple[Any, str, str]]:
    """Build the ambiguity condition for rules.

    TODO: Docs
    """
    ret = []
    formula_size = 0

    for H, H_index in mapper.variable_items():
        for hl in range(1, n + 1):
            # [hl, hl - 1]
            hr = hl - 1
            if H_index in ambiguously_nullable:
                ret.append((
                    variables[f'q${hl}${hr}${H_index}'],
                    (H, (hl, hr))
                ))
            # non-empty intervals
            for hr in range(hl, n + 1):
                P = generate_non_trivial_ambiguity_condition(rule_dict, hl, hr, variables, mapper, nullable, H)
                ret.append(
                    (
                        And(variables[f'q${hl}${hr}${H_index}'], at_least_two_holds(P)),
                        (H, (hl, hr)),
                    )
                )
                formula_size += get_formula_size(ret[-1][0])

    print_metric({'type': 'assertion_count', 'data': {
        'name': 'ambiguity', 'count': formula_size
    }})

    return ret
