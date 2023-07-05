from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Set

from ebnf.ast import (BinaryExpressionNode, RuleNode, UnaryExpressionNode,
                      VariableExpressionNode)
from interaction.metric_printer import print_metric
from utils.SymbolIdMapper import SymbolIdMapper
from verification.predicate import get_predicate_for_rule
from pysmt.shortcuts import And, Or, Bool, get_formula_size
from pysmt.solvers.solver import Solver


def build_reachable_condition(start_var: str, rule_dict: Dict[str, List[RuleNode]],
                              variables: Dict[str, Any], mapper: SymbolIdMapper, word_len: int, solver: Solver,
                              nullable: Set[str]):
    exists_dict: DefaultDict[str, List[Any]] = defaultdict(list)

    for A, A_index in mapper.variable_items():
        for left in range(1, word_len + 1):
            for right in range(left, word_len + 1):
                ident_q_A = f'q${left}${right}${A_index}'
                condition_start = Bool(A == start_var and left == 1 and right == word_len)
                exists_dict[ident_q_A].append(condition_start)

    for A, A_index in mapper.variable_items():
        for left in range(1, word_len + 1):

            for right in range(left - 1, word_len + 1):
                for rule in rule_dict[A]:
                    if isinstance(rule.expression, VariableExpressionNode):
                        B = rule.expression.variable
                        B_index = mapper.get_id_for_variable(B)
                        ident_q_B = f'q${left}${right}${B_index}'
                        exists_dict[ident_q_B].append(variables[f'q${left}${right}${A_index}'])
                    elif isinstance(rule.expression, UnaryExpressionNode):
                        assert isinstance(rule.expression.expr, VariableExpressionNode)
                        B = rule.expression.expr.variable
                        B_index = mapper.get_id_for_variable(B)
                        ident_q_B = f'q${left}${right}${B_index}'
                        exists_dict[ident_q_B].append(And(
                            variables[f'q${left}${right}${A_index}'],
                            get_predicate_for_rule(rule, variables, left, right)
                        ))
                    elif isinstance(rule.expression, BinaryExpressionNode):
                        assert isinstance(rule.expression.expr1, VariableExpressionNode)
                        assert isinstance(rule.expression.expr2, VariableExpressionNode)
                        B, C = rule.expression.expr1.variable, rule.expression.expr2.variable
                        B_index = mapper.get_id_for_variable(B)
                        C_index = mapper.get_id_for_variable(C)
                        if C in nullable:
                            exists_dict[f'q${left}${right}${B_index}'].append(variables[f'q${left}${right}${A_index}'])
                        for h in range(left - 1, right):
                            cond_B = And(variables[f'q${left}${right}${A_index}'],
                                         variables[f'x${h + 1}${right}${C_index}'],
                                         get_predicate_for_rule(rule, variables, left, h + 1)
                                         if h != left - 1 else Bool(True))
                            # /\ for BinaryOp, constraints hold if any side is []
                            exists_dict[f'q${left}${h}${B_index}'].append(cond_B)

                        if B in nullable:
                            exists_dict[f'q${left}${right}${C_index}'].append(variables[f'q${left}${right}${A_index}'])
                        for h in range(left, right + 1):
                            cond_C = And(variables[f'q${left}${right}${A_index}'],
                                         variables[f'x${left}${h}${B_index}'],
                                         get_predicate_for_rule(rule, variables, left, h + 1)
                                         if h != right else Bool(True))
                            exists_dict[f'q${h + 1}${right}${C_index}'].append(cond_C)

    formula_size = 0
    for A, A_index in mapper.variable_items():
        for left in range(1, word_len + 1):
            for right in range(left, word_len + 1):
                ident_q = f'q${left}${right}${A_index}'
                cond_to_add = variables[ident_q].Implies(Or(exists_dict[ident_q]))
                formula_size += get_formula_size(cond_to_add)
                solver.add_assertion(cond_to_add)

    print_metric({'type': 'assertion_count', 'data': {
        'name': 'sentence reachable', 'count': formula_size
    }})
