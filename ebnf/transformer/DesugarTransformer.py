from copy import deepcopy
from typing import List, Tuple

from ebnf.ast import *


def _get_normal_form_node(e: ExpressionNode, new_rules: List[RuleNode], tree_id: str):
    if e.tree_id: tree_id = e.tree_id
    if isinstance(e, VariableExpressionNode):
        t = deepcopy(e)
        t._tree_id = tree_id
        return t
    else:
        rule = RuleNode.new_rule(e, expr_original_text=e.original_text, tree_id=tree_id)
        new_rules.append(rule)
        return VariableExpressionNode(rule.variable, original_text=e.original_text, tree_id=tree_id)


def desugar_rule_item(rule: RuleNode, tree_id: Optional[str] = None) -> Tuple[ExpressionNode, List[RuleNode]]:
    """Desugar a single rule item.

    - Remove ?, +, *, |+|, |*|
    - Ensure that Binary Expression Nodes only have children of variable nodes
      - '|' nodes don't comply to this
    - Ensure that Unary Expression Nodes only have a single variable node as its child

    Args:
        rule (RuleNode): the rule to desugar
        tree_id (Optional[str]): if specified, set the tree_id of new node; otherwise use existing value

    Returns:
        Tuple[ExpressionNode, List[RuleNode]]: the transformed expression node, along with the generated new rules
    """
    UnaryOp = UnaryExpressionNode.UnaryOp
    BinaryOp = BinaryExpressionNode.BinaryOp
    u = rule.expression
    new_rules: List[RuleNode] = []

    if tree_id is None:
        tree_id = rule.tree_id

    if isinstance(u, UnaryExpressionNode):
        if u.op == UnaryOp.Optional:
            expr_node = _get_normal_form_node(u.expr, new_rules, tree_id)
            expr_rtn = BinaryExpressionNode(expr_node,
                                            EmptyExpressionNode(tree_id=tree_id),
                                            BinaryOp.OrOp,
                                            original_text=u.original_text)
        elif u.op in [UnaryOp.KleenePlus, UnaryOp.AlignedKleenePlus]:
            expr_node = _get_normal_form_node(u.expr, new_rules, tree_id + '/0')  # B
            # A ::= B+; A ::= C, C ::= C<op>B | B
            e = BinaryExpressionNode(
                BinaryExpressionNode(
                    VariableExpressionNode(rule.variable),
                    expr_node,
                    BinaryOp.ConcatOp if u.op == UnaryOp.KleenePlus else BinaryOp.AlignOp,
                    original_text=u.original_text,
                    tree_id=tree_id
                ),
                expr_node,
                BinaryOp.OrOp,
                original_text=u.original_text,
                tree_id=tree_id
            )
            rule = RuleNode.new_rule(e, expr_original_text=e.original_text, tree_id=tree_id)
            (rule.expression.children()[0].children()[0]).variable = rule.variable
            new_rules.append(rule)
            expr_rtn = VariableExpressionNode(rule.variable, original_text=e.original_text, tree_id=tree_id)
        elif u.op in [UnaryOp.KleeneStar, UnaryOp.AlignedKleeneStar]:
            expr_node = _get_normal_form_node(u.expr, new_rules, tree_id + '/0')  # B
            # A ::= B*; A ::= C, C ::= C<op>B | empty
            e = BinaryExpressionNode(
                BinaryExpressionNode(
                    VariableExpressionNode(rule.variable),
                    expr_node,
                    BinaryOp.ConcatOp if u.op == UnaryOp.KleeneStar else BinaryOp.AlignOp,
                    original_text=u.original_text,
                    tree_id=tree_id
                ),
                EmptyExpressionNode(tree_id=tree_id),
                BinaryOp.OrOp,
                original_text=u.original_text,
                tree_id=tree_id
            )
            rule = RuleNode.new_rule(e, expr_original_text=e.original_text, tree_id=tree_id)
            (rule.expression.children()[0].children()[0]).variable = rule.variable
            new_rules.append(rule)
            expr_rtn = VariableExpressionNode(rule.variable, original_text=e.original_text, tree_id=tree_id)
        else:
            expr_node = _get_normal_form_node(u.expr, new_rules, tree_id+'/0')
            expr_rtn = UnaryExpressionNode(expr_node, u.op, original_text=u.original_text, tree_id=tree_id)

        return expr_rtn, new_rules

    elif isinstance(u, BinaryExpressionNode):
        lhs = _get_normal_form_node(u.expr1, new_rules, tree_id=tree_id+'/0')
        rhs = _get_normal_form_node(u.expr2, new_rules, tree_id=tree_id+'/1')
        if u.op == BinaryOp.OrOp:
            lhs._tree_id = rhs._tree_id = tree_id
        expr_rtn = BinaryExpressionNode(lhs, rhs, u.op, original_text=u.original_text, tree_id=tree_id)

        return expr_rtn, new_rules

    else:
        return u, []


def desugar_rules(rules_original: List[RuleNode]) -> List[RuleNode]:
    i = 0
    rules = deepcopy(rules_original)
    original_rule_count = len(rules)
    while i < len(rules):
        if i < original_rule_count:
            rules[i]._tree_id = rules[i].variable
            desugared_expr, new_rules = desugar_rule_item(rules[i], rules[i].variable)
        else:
            desugared_expr, new_rules = desugar_rule_item(rules[i], None)
        rules[i].expression = desugared_expr
        rules.extend(new_rules)
        i += 1
    return rules
