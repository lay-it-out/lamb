from typing import List, Tuple, Union

from pysmt.shortcuts import TRUE, And, Implies, GT, Int, Equals, GE, Plus

from lamb.ebnf.ast import BinaryExpressionNode, RuleNode, UnaryExpressionNode

UnaryOp = UnaryExpressionNode.UnaryOp
BinaryOp = BinaryExpressionNode.BinaryOp


def position_seq_conform_to_rule(
        position_seq: List[Tuple[int, int]],
        i: int, j: int, op: Union[BinaryOp, UnaryOp]) -> bool:
    if i > j:
        return True
    if op == BinaryOp.AlignOp:
        return position_seq[i][1] == position_seq[j][1]
    elif op == BinaryOp.IndentOp:
        return (position_seq[j][1] > position_seq[i][1]) and (position_seq[j][0] == position_seq[j - 1][0] + 1)
    elif op == BinaryOp.StartSameLineOp:
        return (position_seq[j][0] == position_seq[i][0])
    elif op == UnaryOp.OffsideOp:
        for k in range(i + 1, j + 1):
            if position_seq[k][0] > position_seq[i][0] and position_seq[k][1] <= position_seq[i][1]: return False
        return True
    elif op == UnaryOp.OffsideEquOp:
        for k in range(i + 1, j + 1):
            if position_seq[k][0] > position_seq[i][0] and position_seq[k][1] < position_seq[i][1]: return False
        return True
    elif op == UnaryOp.SameLineOp:
        for k in range(i + 1, j + 1):
            if position_seq[k][0] != position_seq[k - 1][0]: return False
        return True
    else:
        raise NotImplementedError()


def get_predicate(op, variables: dict, i: int, j: int, is_binary: bool, strict: bool = True,
                  syn_prefix: str = ''): # strict: do not allow unary ops on binary nodes
    if i > j:
        return TRUE()
    if is_binary:
        if op == BinaryOp.ConcatOp:
            return TRUE()
        elif op == BinaryOp.AlignOp:
            return variables[f'{syn_prefix}col${i}'].Equals(variables[f'{syn_prefix}col${j}'])
        elif op == BinaryOp.IndentOp:
            return And(
                GT(variables[f'{syn_prefix}col${j}'], variables[f'{syn_prefix}col${i}']),
                Equals(variables[f'{syn_prefix}line${j}'], Plus(variables[f'{syn_prefix}line${j - 1}'], Int(1)))
            )
        elif op == BinaryOp.StartSameLineOp:
            return Equals(variables[f'{syn_prefix}line${j}'], variables[f'{syn_prefix}line${i}'])
        elif strict:
            raise NotImplementedError()

    if op == UnaryOp.OffsideOp:
        assert i <= j
        ret = TRUE()
        for k in range(i + 1, j + 1):
            ret = And(ret, Implies(
                GT(variables[f'{syn_prefix}line${k}'], variables[f'{syn_prefix}line${i}']),
                GT(variables[f'{syn_prefix}col${k}'], variables[f'{syn_prefix}col${i}'])
            ))
        return ret
    elif op == UnaryOp.OffsideEquOp:
        assert i <= j
        ret = TRUE()
        for k in range(i + 1, j + 1):
            ret = And(ret, Implies(
                GT(variables[f'{syn_prefix}line${k}'], variables[f'{syn_prefix}line${i}']),
                GE(variables[f'{syn_prefix}col${k}'], variables[f'{syn_prefix}col${i}'])
            ))
        return ret
    elif op == UnaryOp.SameLineOp:
        assert i <= j
        ret = TRUE()
        for k in range(i + 1, j + 1):
            ret = And(ret, variables[f'{syn_prefix}line${k}'].Equals(variables[f'{syn_prefix}line${k - 1}']))
        return ret
    else:
        raise NotImplementedError()


def get_predicate_for_rule(rule: RuleNode, variables, i, j, syn_prefix: str = ''):
    assert isinstance(rule.expression, (BinaryExpressionNode, UnaryExpressionNode))
    op = rule.expression.op
    return get_predicate(op, variables, i, j, isinstance(rule.expression, BinaryExpressionNode),
                         syn_prefix=syn_prefix)
