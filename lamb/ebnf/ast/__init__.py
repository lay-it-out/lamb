import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Sequence, Set, Type
import textwrap
import uuid

import pydot

rd = random.Random()
rd.seed(0)


def uuid4() -> uuid.UUID:
    return uuid.UUID(int=rd.getrandbits(128), version=4)


class ASTNode(ABC):
    """Base class for abstract syntax tree nodes.
    """

    def __init__(self, *, original_text='', tree_id: Optional[str] = None):
        self.uuid = uuid4()
        self._graphviz_node = None
        self._rule: Optional[RuleNode] = None
        self._graphviz_children = []
        self._original_text = original_text
        self._tree_id = tree_id

    def get_name(self):
        return self.__class__.__name__ + f'<{self.uuid.hex[:8]}>'

    @property
    def original_text(self):
        return self._original_text

    @property
    def tree_id(self):
        return self._tree_id

    @abstractmethod
    def children(self) -> Sequence['ASTNode']:
        pass

    def omit_property(self, key: str):
        return key.startswith('_') or key == 'uuid' or key == 'op'

    def to_sexpr(self, root_name: Optional[str] = None, show_root: bool = False,
                 compress: bool = False, colored: bool = False) -> List[str]:
        quote_parens = lambda x: x.replace('(', '\\(').replace(')', '\\)')

        if show_root:
            root_name = self._rule.tree_id if self._rule else self._tree_id
        children = []
        for prop in vars(self):
            if self.omit_property(prop): continue
            value = vars(self)[prop]
            if isinstance(value, ASTNode):
                children.extend(value.to_sexpr(compress=compress, colored=colored))
            elif isinstance(value, list):
                for x in value:
                    if isinstance(x, ASTNode):
                        children.extend(x.to_sexpr(compress=compress, colored=colored))
            else:
                token = str(value)
                if colored: token = f'<ansiblue><u>{token}</u></ansiblue>'
                child_node = quote_parens(token)
                children.append(child_node)
        if (not compress) or ((self._rule and not self._rule.variable.startswith('new-var-')) or root_name is not None):
            node_label = quote_parens(self._tree_id or '')
            node_extra_label = ''

            if self._rule is not None:
                node_label = quote_parens(root_name or self._rule.variable or "NOLABEL")
            if getattr(self, 'op', None) is not None and len(self.op.value):
                node_extra_label = f":op {quote_parens(self.op.value)}"
                if colored: node_extra_label = f'<grey>{node_extra_label}</grey>'
            if colored: node_label = f'<ansired>{node_label}</ansired>'
            node = '(' + node_label + '\n'
            indent_spaces = 4*' '
            if node_extra_label:
                node += indent_spaces + node_extra_label + '\n'
            if len(children):
                children_raw = []
                for ch in children:
                    children_raw.extend(ch.split('\n'))
                if len(children_raw) == 1:
                    node += indent_spaces + f'({children_raw[0]}))'
                else:
                    node += indent_spaces + f'({children_raw[0]}\n'
                    node += indent_spaces + ' ' + ('\n' + indent_spaces + ' ').join(children_raw[1:])
                    node += '))'
            else:
                node += indent_spaces + '())'

            return [node]
        else:
            return children

    def draw_graphviz(self, graph: pydot.Dot, root_name: Optional[str] = None,
                      show_root: bool = False, compress: bool = False) -> List[pydot.Node]:
        if show_root:
            root_name = self._rule.tree_id if self._rule else self._tree_id
        self._graphviz_children = []
        for prop in vars(self):
            if self.omit_property(prop):
                continue
            value = vars(self)[prop]
            if isinstance(value, ASTNode):
                self._graphviz_children.extend(value.draw_graphviz(graph, compress=compress))
            elif isinstance(value, list):
                for x in value:
                    if isinstance(x, ASTNode):
                        self._graphviz_children.extend(x.draw_graphviz(graph, compress=compress))
            else:
                child_node = pydot.Node(name=str(uuid4()), label='"' + str(value).replace('"', '\\"') + '"',
                                        forcelabels=True, shape='box', fontcolor='blue')
                self._graphviz_children.append(child_node)
                graph.add_node(child_node)
        if (not compress) or ((self._rule and not self._rule.variable.startswith('new-var-')) or root_name is not None):
            node_kwargs = dict(
                name=str(uuid4()),
                label='"' + (self._tree_id or '').replace('"', '\\"') + '"',
                forcelabels=True,
                shape='plain',
                fontcolor='red'
            )
            # print(self.__dict__)

            if self._rule is not None:
                v = (root_name or self._rule.variable or "NOLABEL")
                v = v.replace('"', '\\"')
                node_kwargs['label'] = f'"{v}"'
            if getattr(self, 'op', None) is not None:
                node_kwargs['xlabel'] = '"' + self.op.value.replace('"', '\\"') + '"'
            self._graphviz_node = pydot.Node(**node_kwargs)  # type: ignore
            graph.add_node(self._graphviz_node)  # type: ignore
            for child in self._graphviz_children:
                graph.add_edge(pydot.Edge(self._graphviz_node, child))  # type: ignore
            return [self._graphviz_node]
        else:
            return self._graphviz_children

    @property
    def rule(self):
        return self._rule


class ExpressionNode(ASTNode, ABC):
    pass


class RuleNode(ASTNode):
    rule_names: Set[str] = set()
    rule_rename_count = 0

    def __init__(self, variable: str, expr: ExpressionNode, *, original_text='', tree_id: Optional[str] = None):
        super().__init__(original_text=original_text, tree_id=tree_id)
        RuleNode.rule_names.add(variable)
        self.variable = variable
        self.expression = expr

    @classmethod
    def get_rule_name(cls: Type['RuleNode']) -> str:
        while f'new-var-{cls.rule_rename_count}' in cls.rule_names:
            cls.rule_rename_count += 1
        new_name = f'new-var-{cls.rule_rename_count}'
        cls.rule_names.add(new_name)
        return new_name

    @classmethod
    def new_rule(cls: Type['RuleNode'], expr: ExpressionNode, *, expr_original_text='',
                 tree_id: Optional[str] = None) -> 'RuleNode':
        rule_name = cls.get_rule_name()
        return RuleNode(rule_name, expr, original_text=f'{rule_name} ::= {expr_original_text}', tree_id=tree_id)

    @property
    def children(self) -> Sequence['ASTNode']:
        return [self.expression]


class DocumentNode(ASTNode):
    def __init__(self, tree_id: Optional[str] = None):
        super().__init__(tree_id=tree_id)
        self.rules: List[RuleNode] = []

    def append_rule(self, rule: RuleNode):
        self.rules.append(rule)

    def children(self) -> Sequence['ASTNode']:
        return self.rules


class UnaryExpressionNode(ExpressionNode):
    class UnaryOp(Enum):
        KleenePlus = '+'
        KleeneStar = '*'
        Optional = '?'
        OffsideOp = '|>'
        OffsideEquOp = '>>'
        SameLineOp = '~'
        AlignedKleenePlus = '|+|'
        AlignedKleeneStar = '|*|'
        NoOp = ''

    def __init__(self, expr: ExpressionNode, op: UnaryOp, *, original_text: str = '', tree_id: Optional[str] = None):
        super().__init__(original_text=original_text, tree_id=tree_id)
        self.expr = expr
        self.op = op

    def children(self) -> Sequence['ASTNode']:
        return [self.expr]


class BinaryExpressionNode(ExpressionNode):
    class BinaryOp(Enum):
        IndentOp = '->'
        AlignOp = '||'
        OrOp = '|'
        StartSameLineOp = '|~'  # 1st token of each side is on the same line
        ConcatOp = ''

    def __init__(self, expr1: ExpressionNode, expr2: ExpressionNode, op: BinaryOp, *, original_text: str = '',
                 tree_id: Optional[str] = None):
        super().__init__(original_text=original_text, tree_id=tree_id)
        self.expr1 = expr1
        self.expr2 = expr2
        self.op = op

    def children(self) -> Sequence['ASTNode']:
        return [self.expr1, self.expr2]


class LeafNode(ExpressionNode):
    def children(self) -> Sequence['ASTNode']:
        return []


class VariableExpressionNode(LeafNode):
    def __init__(self, variable: str, *, original_text=None, tree_id: Optional[str] = None):
        super().__init__(original_text=original_text or variable, tree_id=tree_id)
        self.variable = variable


class LiteralExpressionNode(LeafNode):
    def __init__(self, content: str, tree_id: Optional[str] = None):
        super().__init__(original_text=f'"{content}"', tree_id=tree_id)
        self.content = content  # with no quotes


class EmptyExpressionNode(LeafNode):
    pass
