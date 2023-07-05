from verification.predicate import get_predicate_for_rule
from utils.SymbolIdMapper import SymbolIdMapper
from ebnf.ast import BinaryExpressionNode, ExpressionNode, LiteralExpressionNode, RuleNode, UnaryExpressionNode, VariableExpressionNode
from typing import DefaultDict, Dict, List, Set
from pysmt.shortcuts import And
from pysmt.solvers.solver import Model
import itertools

def _create_expr_node_with_rule(cls, *args, **kwargs):
    rule = kwargs['rule']
    del kwargs['rule']
    node = cls(*args, **kwargs)
    node._rule = rule
    return node

def search_all_ambiguous_trees(model: Model, rule_dict: DefaultDict[str, List[RuleNode]],
    l: int, r: int, variables: Dict, mapper: SymbolIdMapper, nullable: Set[str], A: str) -> List[ExpressionNode]:
    """N.B.: only return all ambiguous trees that differ with each other on the first layer.
    [l, r] is a closed interval.
    """
    ret = []

    if l == r:
        for rule in rule_dict[A]:
            if isinstance(rule.expression, LiteralExpressionNode):
                index_a = mapper.get_id_for_literal(rule.expression.content)
                if model.get_py_value(variables[f'x${l}'], model_completion=True) == index_a:
                    ret.append(_create_expr_node_with_rule(LiteralExpressionNode, rule.expression.content, rule=rule))
    
    for rule in rule_dict[A]:
        if isinstance(rule.expression, UnaryExpressionNode):
            assert rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideOp\
                or rule.expression.op == UnaryExpressionNode.UnaryOp.SameLineOp\
                or rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideEquOp
            assert isinstance(rule.expression.expr, VariableExpressionNode)
            B = rule.expression.expr.variable
            B_index = mapper.get_id_for_variable(B)
            cond = And(
                variables[f'x${l}${r}${B_index}'],
                get_predicate_for_rule(rule, variables, l, r)
            )
            if model.get_py_value(cond, model_completion=True):
                subtrees = search_all_ambiguous_trees(model, rule_dict, l, r, variables, mapper, nullable, B)
                ret.extend([_create_expr_node_with_rule(UnaryExpressionNode, x, rule.expression.op, rule=rule) for x in subtrees])

        elif isinstance(rule.expression, VariableExpressionNode):
            B = rule.expression.variable
            B_index = mapper.get_id_for_variable(B)
            if model.get_py_value(variables[f'x${l}${r}${B_index}'], model_completion=True):
                subtrees = search_all_ambiguous_trees(model, rule_dict, l, r, variables, mapper, nullable, B)
                ret.extend([_create_expr_node_with_rule(UnaryExpressionNode, x, UnaryExpressionNode.UnaryOp.NoOp, rule=rule) for x in subtrees])
        
        elif isinstance(rule.expression, BinaryExpressionNode):
            assert isinstance(rule.expression.expr1, VariableExpressionNode)
            assert isinstance(rule.expression.expr2, VariableExpressionNode)
            B, C = rule.expression.expr1.variable, rule.expression.expr2.variable
            op = rule.expression.op
            B_index = mapper.get_id_for_variable(B)
            C_index = mapper.get_id_for_variable(C)

            if C in nullable and model.get_py_value(variables[f'x${l}${r}${B_index}'], model_completion=True):
                subtrees = search_all_ambiguous_trees(model, rule_dict, l, r, variables, mapper, nullable, B)
                ret.extend([_create_expr_node_with_rule(UnaryExpressionNode, x, UnaryExpressionNode.UnaryOp.NoOp, rule=rule) for x in subtrees])
            if B in nullable and model.get_py_value(variables[f'x${l}${r}${C_index}'], model_completion=True):
                subtrees = search_all_ambiguous_trees(model, rule_dict, l, r, variables, mapper, nullable, C)
                ret.extend([_create_expr_node_with_rule(UnaryExpressionNode, x, UnaryExpressionNode.UnaryOp.NoOp, rule=rule) for x in subtrees])
            
            for h in range(l, r):
                cond1 = (variables[f'x${l}${h}${B_index}'])
                cond2 = (variables[f'x${h+1}${r}${C_index}'])
                cond3 = get_predicate_for_rule(rule, variables, l, h+1)
                if not model.get_py_value(And(cond1, cond2, cond3), model_completion=True):
                    continue
                subtree_left = search_all_ambiguous_trees(model, rule_dict, l, h, variables, mapper, nullable, B)
                subtree_right = search_all_ambiguous_trees(model, rule_dict, h+1, r, variables, mapper, nullable, C)
                ret.extend([
                    _create_expr_node_with_rule(BinaryExpressionNode, x, y, rule.expression.op, rule=rule)
                    for x, y in itertools.product(subtree_left, subtree_right)
                ]),
    
    return ret
