from typing import Dict, List
from pysmt.shortcuts import Symbol, Implies, Or, TRUE, And

from ebnf.ast import RuleNode, UnaryExpressionNode, BinaryExpressionNode
from verification.predicate import BinaryOp, UnaryOp, get_predicate_for_rule, get_predicate

SYN_OP_CHOICES = [
    BinaryOp.AlignOp,
    BinaryOp.IndentOp,
    # BinaryOp.StartSameLineOp,
    UnaryOp.OffsideOp,
    UnaryOp.OffsideEquOp,
    UnaryOp.SameLineOp,
]

SYN_PHI_TILDE_PREFIX = "PhiTilde"


def get_syn_var_name(rule: RuleNode, op: BinaryOp | UnaryOp) -> str:
    assert isinstance(rule.expression, BinaryExpressionNode) or (not isinstance(op, BinaryOp))
    return f'{SYN_PHI_TILDE_PREFIX}${op.name}${rule.uuid.hex}'


def get_predicate_vars(rules: List[RuleNode]) -> Dict:
    ret = dict()
    for rule in rules:
        for op in SYN_OP_CHOICES:
            # check if the operator cannot be used
            if (not isinstance(rule.expression, BinaryExpressionNode)) and isinstance(op, BinaryOp):
                continue
            var_name = get_syn_var_name(rule, op)
            ret[var_name] = Symbol(var_name)
    return ret


def get_predicate_choices(rule: RuleNode, variables: Dict, i: int, j: int, syn_prefix: str):
    cases = []
    rhs = rule.expression
    add_all = not (isinstance(rhs, UnaryExpressionNode) or isinstance(rhs, BinaryExpressionNode))

    for op in SYN_OP_CHOICES:
        is_binary = isinstance(rhs, BinaryExpressionNode)
        # noinspection PyUnresolvedReferences
        if add_all or rhs.op != op:  # suppressed due to short circuit
            # if `op` is already added, then there's no need to add the corresponding case,
            # since adding the constraint twice doesn't make sense

            # check if the operator cannot be used
            if (not is_binary) and isinstance(op, BinaryOp):
                continue
            var_name = get_syn_var_name(rule, op)
            cases.append(Implies(variables[var_name],
                                 get_predicate(op, variables, i, j, is_binary, strict=False, syn_prefix=syn_prefix)))
        else:
            cases.append(get_predicate(op, variables, i, j, is_binary, strict=False, syn_prefix=syn_prefix))
    return And(*cases)  # TODO: and/or?
