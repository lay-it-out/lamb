from collections import defaultdict
from typing import DefaultDict, Dict, Any
from lamb.interaction.metric_printer import print_metric

from lamb.verification.predicate import get_predicate_for_rule
from lamb.utils.SymbolIdMapper import SymbolIdMapper
from lamb.ebnf.ast import *
from pysmt.shortcuts import FALSE, Implies, Int, Equals, Or, And, Iff, get_formula_size
from pysmt.solvers.solver import Solver

formula_size = 0


def extend_deductive_condition_by_one(new_len: int, s: Solver, variables: Dict,
                                      mapper: SymbolIdMapper, rule_dict: DefaultDict[str, List[RuleNode]],
                                      nullable: Set[str]) -> List[Any]:
    global formula_size
    ret = []
    j = new_len
    for i in range(1, new_len + 1):
        for A, index_A in mapper.variable_items():
            assert A
            premise = (variables[f'x${i}${j}${index_A}'])
            implied = FALSE()

            if i == j:
                for rule in rule_dict[A]:
                    if isinstance(rule.expression, LiteralExpressionNode):
                        index_literal = mapper.get_id_for_literal(rule.expression.content)
                        implied = Or(implied, Equals(variables[f'x${i}'], Int(index_literal)))

            for rule in rule_dict[A]:
                if isinstance(rule.expression, VariableExpressionNode):
                    B = rule.expression.variable
                    index_B = mapper.get_id_for_variable(B)
                    if A == B: continue
                    implied = Or(implied, variables[f'x${i}${j}${index_B}'])

                elif isinstance(rule.expression, UnaryExpressionNode):
                    assert isinstance(rule.expression.expr, VariableExpressionNode)
                    assert rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideOp \
                           or rule.expression.op == UnaryExpressionNode.UnaryOp.SameLineOp \
                           or rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideEquOp

                    B = rule.expression.expr.variable
                    index_B = mapper.get_id_for_variable(B)
                    if A == B: continue

                    cond1 = (variables[f'x${i}${j}${index_B}'])
                    cond2 = get_predicate_for_rule(rule, variables, i, j)

                    implied = Or(implied, And(cond1, cond2))

                elif isinstance(rule.expression, BinaryExpressionNode):
                    assert isinstance(rule.expression.expr1, VariableExpressionNode)
                    assert isinstance(rule.expression.expr2, VariableExpressionNode)
                    B, C = rule.expression.expr1.variable, rule.expression.expr2.variable
                    index_B = mapper.get_id_for_variable(B)
                    index_C = mapper.get_id_for_variable(C)
                    if A != B and C in nullable:
                        implied = Or(implied, variables[f'x${i}${j}${index_B}'])
                    if A != C and B in nullable:
                        implied = Or(implied, variables[f'x${i}${j}${index_C}'])
                    for h in range(i, j):
                        cond1 = (variables[f'x${i}${h}${index_B}'])
                        cond2 = (variables[f'x${h + 1}${j}${index_C}'])
                        cond3 = get_predicate_for_rule(rule, variables, i, h + 1)
                        implied = Or(implied, And(cond1, cond2, cond3))
            cond_to_add = Implies(premise, implied)
            s.add_assertion(cond_to_add)
            ret.append(cond_to_add)
            formula_size += get_formula_size(cond_to_add)
        # end for A
    # end for i
    print_metric({'type': 'assertion_count', 'data': {
        'name': 'deductive', 'count': formula_size
    }})
    return ret
