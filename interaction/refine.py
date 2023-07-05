from typing import Dict, Tuple, List
from uuid import UUID

from ebnf.ast import *
from verification.predicate import *


refinable_binary_ops = [BinaryOp.AlignOp, BinaryOp.IndentOp]
refinable_unary_ops = [UnaryOp.OffsideOp, UnaryOp.SameLineOp, UnaryOp.OffsideEquOp]

def convert_reformatted_to_position_seq(reformatted: Dict[int, Tuple[int, int]], l: int, r: int):
    ret: List[Optional[Tuple[int, int]]] = [None]
    for i in range(l, r + 1):
        ret.append(reformatted[i])
    return ret


def calculate_word_len_of_subtree(node: ExpressionNode):
    if isinstance(node, LeafNode):
        if isinstance(node, LiteralExpressionNode):
            node._size = 1
        elif isinstance(node, EmptyExpressionNode):
            node._size = 0
        else:
            raise NotImplementedError()
    else:
        node._size = 0
        for x in node.children():
            calculate_word_len_of_subtree(x)
            node._size += x._size


def refine_dfs(node: ExpressionNode,
               position_seq: List[Tuple[int, int]],
               interval: Tuple[int, int],
               all_constraints: Dict[UUID, Set[Union[BinaryOp, UnaryOp]]]):
    left, right = interval
    if left > right:
        return

    UnaryOp = UnaryExpressionNode.UnaryOp
    BinaryOp = BinaryExpressionNode.BinaryOp
    constraint_op = set()

    assert isinstance(node._rule, RuleNode)
    if isinstance(node._rule.expression, BinaryExpressionNode) and \
            node._rule.expression.op == BinaryOp.ConcatOp:
        if isinstance(node, BinaryExpressionNode):
            # if A->BC has a null B/C, binary constraints will not be generated
            mid = left + node.expr1._size  # [left, mid), [mid, right]
            for op in refinable_binary_ops:
                if position_seq_conform_to_rule(position_seq, left, mid, op):
                    constraint_op.add(op)
        else:
            constraint_op.update(refinable_binary_ops)
    for op in refinable_unary_ops:
        if position_seq_conform_to_rule(position_seq, left, right, op):
            constraint_op.add(op)
    all_constraints[node._rule.uuid].intersection_update(constraint_op)

    # recursion
    if isinstance(node, BinaryExpressionNode):
        mid = left + node.expr1._size  # [left, mid), [mid, right]
        refine_dfs(node.expr1, position_seq, (left, mid - 1), all_constraints)
        refine_dfs(node.expr2, position_seq, (mid, right), all_constraints)
    else:
        for x in node.children():
            refine_dfs(x, position_seq, interval, all_constraints)


def generate_all_constraint_op(rule: RuleNode):
    ret = set(refinable_unary_ops)
    if isinstance(rule.expression, BinaryExpressionNode) \
            and rule.expression.op == BinaryOp.ConcatOp:
        ret.update(refinable_binary_ops)
    return ret


def refine(parse_trees: List[ExpressionNode],
           reformatted_list: List[Dict[int, Tuple[int, int]]],
           rules: List[RuleNode], l: int, r: int):
    """calculates how "refinable rules" can be refined using layout operators.
    """

    all_constraints: Dict[UUID, set] = {}
    for rule in rules:
        all_constraints[rule.uuid] = generate_all_constraint_op(rule)

    for tree, reformatted_item in zip(parse_trees, reformatted_list):
        position_seq = convert_reformatted_to_position_seq(reformatted_item, l, r)
        calculate_word_len_of_subtree(tree)
        refine_dfs(tree, position_seq, (1, tree._size), all_constraints)

    return all_constraints
