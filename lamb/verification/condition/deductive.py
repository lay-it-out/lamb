from collections import defaultdict
from typing import DefaultDict, Dict, Any
from lamb.interaction.metric_printer import print_metric
from lamb.interaction.synthesis import get_predicate_choices

from lamb.verification.predicate import get_predicate_for_rule
from lamb.utils.SymbolIdMapper import SymbolIdMapper
from lamb.ebnf.ast import *
from pysmt.shortcuts import FALSE, Implies, Int, Equals, Or, And, Iff, get_formula_size
from pysmt.solvers.solver import Solver

formula_size = 0


def extend_deductive_condition_by_one(new_len: int, s: Solver, variables: Dict,
                                      mapper: SymbolIdMapper, rule_dict: DefaultDict[str, List[RuleNode]],
                                      nullable: Set[str],
                                      is_synthesis: bool = False,
                                      syn_prefix: str = '') -> List[Any]:
    assert (not is_synthesis) or (syn_prefix != '')
    global formula_size
    ret = []
    j = new_len
    for i in range(1, new_len + 1):
        for A, index_A in mapper.variable_items():
            assert A
            premise = (variables[f'{syn_prefix}x${i}${j}${index_A}'])
            implied = FALSE()

            if i == j:
                for rule in rule_dict[A]:
                    if isinstance(rule.expression, LiteralExpressionNode):
                        index_literal = mapper.get_id_for_literal(rule.expression.content)
                        implied = Or(implied, Equals(variables[f'{syn_prefix}x${i}'], Int(index_literal)))

            for rule in rule_dict[A]:
                if isinstance(rule.expression, VariableExpressionNode):
                    B = rule.expression.variable
                    index_B = mapper.get_id_for_variable(B)
                    if A == B: continue
                    implied = Or(implied, variables[f'{syn_prefix}x${i}${j}${index_B}'])

                elif isinstance(rule.expression, UnaryExpressionNode):
                    assert isinstance(rule.expression.expr, VariableExpressionNode)
                    assert rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideOp \
                           or rule.expression.op == UnaryExpressionNode.UnaryOp.SameLineOp \
                           or rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideEquOp

                    B = rule.expression.expr.variable
                    index_B = mapper.get_id_for_variable(B)
                    if A == B: continue

                    cond1 = (variables[f'{syn_prefix}x${i}${j}${index_B}'])
                    if is_synthesis:
                        cond2 = get_predicate_choices(rule, variables, i, j, syn_prefix=syn_prefix)
                    else:
                        cond2 = get_predicate_for_rule(rule, variables, i, j, syn_prefix=syn_prefix)

                    implied = Or(implied, And(cond1, cond2))

                elif isinstance(rule.expression, BinaryExpressionNode):
                    assert isinstance(rule.expression.expr1, VariableExpressionNode)
                    assert isinstance(rule.expression.expr2, VariableExpressionNode)
                    B, C = rule.expression.expr1.variable, rule.expression.expr2.variable
                    index_B = mapper.get_id_for_variable(B)
                    index_C = mapper.get_id_for_variable(C)
                    if A != B and C in nullable:
                        implied = Or(implied, variables[f'{syn_prefix}x${i}${j}${index_B}'])
                    if A != C and B in nullable:
                        implied = Or(implied, variables[f'{syn_prefix}x${i}${j}${index_C}'])
                    for h in range(i, j):
                        cond1 = (variables[f'{syn_prefix}x${i}${h}${index_B}'])
                        cond2 = (variables[f'{syn_prefix}x${h + 1}${j}${index_C}'])
                        if is_synthesis:
                            cond3 = get_predicate_choices(rule, variables, i, h + 1,
                                                          syn_prefix=syn_prefix)
                        else:
                            cond3 = get_predicate_for_rule(rule, variables, i, h + 1, syn_prefix=syn_prefix)
                        implied = Or(implied, And(cond1, cond2, cond3))
            if is_synthesis:
                cond_to_add = Iff(premise, implied)
            else:
                cond_to_add = Implies(premise, implied)
            s.add_assertion(cond_to_add)
            ret.append(cond_to_add)
            if not is_synthesis:
                formula_size += get_formula_size(cond_to_add)
        # end for A
    # end for i
    if not is_synthesis:
        print_metric({'type': 'assertion_count', 'data': {
            'name': 'deductive', 'count': formula_size
        }})
    return ret
