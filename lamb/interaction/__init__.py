from functools import reduce

import pysmt
import z3
from pysmt.shortcuts import Solver, And, Equals, TRUE, Not, Int, Symbol, Or, FALSE, Iff
from pysmt.typing import INT

from lamb.verification import extend_triple_array_by_one
from lamb.verification.condition.deductive import extend_deductive_condition_by_one

original_print = print
import json
from ctypes import ArgumentError
from typing import Dict, List, Tuple, Optional, Set, Any

import open_python
import pydot
from lamb.ebnf.ast import ASTNode, ExpressionNode, RuleNode, LiteralExpressionNode, EmptyExpressionNode, \
    UnaryExpressionNode, BinaryExpressionNode, VariableExpressionNode
from prettytable import PrettyTable
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.formatted_text.html import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts.prompt import PromptSession
from lamb.utils.SymbolIdMapper import SymbolIdMapper
from lamb.utils.TempFile import make_tempfile

from lamb.interaction.cmd_args import get_cmd_args
from lamb.interaction.metric_printer import print_metric
from lamb.interaction.nested import NestedCompleter
from lamb.interaction.parse_tree import search_all_ambiguous_trees


def error(msg):
    if get_cmd_args().serialize:
        original_print(json.dumps({
            "type": "error", "data": msg
        }))
    else:
        print(HTML(f'<ansired>{msg}</ansired>'))


class Interactor:
    def __init__(self, word_len, model, variables, mapper: SymbolIdMapper, ambiguous_condition, rules: List[RuleNode],
                 nullable, tabstop):
        self.model = model
        self.word_len = word_len
        self.variables = variables
        self.mapper = mapper
        self.amb = ambiguous_condition
        self.rules = rules
        self.nullable = nullable
        self.tabstop = tabstop
        self.rejected_constraint = set()

        self.reformatted: Dict[str, List[Dict[int, Tuple[int, int]]]] = dict()
        self.amb_intervals: Dict[str, Tuple[int, int]] = dict()

        self.append_id_to_rules()
        self.calc_parse_tree_dict()

    def append_id_to_rules(self):
        for i in range(len(self.rules)):
            self.rules[i]._index = i
        from lamb.utils.RuleDictBuilder import build_rule_dict
        self.rule_dict = build_rule_dict(self.rules)

    def get_var(self, varname):
        return self.model.get_py_value(self.variables[varname], model_completion=True)

    def get_line(self, i):
        return self.get_var(f'line${i}')

    def get_col(self, i):
        return self.get_var(f'col${i}')

    def get_tok(self, i):
        tok_index = self.get_var(f'x${i}')
        return self.mapper.get_symbol(tok_index)[1:-1]

    def calc_parse_tree_dict(self):
        self.parse_tree_dict: Dict[str, List[ExpressionNode]] = dict()
        for cond, (A, (hl, hr)) in self.amb:
            # YES, there can be a case that multiple (hl, hr) exists for a single A
            # and in that case we simply discard all intervals but the last,
            # since it's all about interaction, and one more round would (possibly)
            # bring in the discarded intervals.
            if not self.model.get_py_value(cond, model_completion=True): continue
            trees = search_all_ambiguous_trees(
                self.model, self.rule_dict, hl, hr,
                self.variables, self.mapper, self.nullable, A)
            self.parse_tree_dict[A] = trees
            self.amb_intervals[A] = (hl, hr)
            self.reformatted[A] = list()
            for i in range(len(trees)):
                self.reformatted[A].append({
                    index: (self.get_line(index), self.get_col(index)) for index in range(1, self.word_len + 1)
                })

    @staticmethod
    def show_node(node: ASTNode, description: str, compress: bool = False):
        dot = pydot.Dot(description)
        node.draw_graphviz(dot, show_root=True, compress=compress)
        png = dot.create_png()
        try:
            fp = make_tempfile('wb', '.png')
            fp.write(png)
            fp.close()
            if get_cmd_args().serialize:
                original_print(json.dumps({'type': 'image', 'data': fp.name}))
            else:
                try:
                    open_python.start(fp.name)
                except:
                    print('Exception thrown when trying to show the picture of parse tree:')
                    print(f'The file path for parse tree is {fp.name}')
                    print('S-expression for the parse tree:',
                          node.to_sexpr(show_root=True, compress=compress)[0], sep='\n')
        except KeyboardInterrupt:
            pass



    @staticmethod
    def count_tokens(node: ASTNode) -> int:
        if isinstance(node, LiteralExpressionNode):
            return 1
        elif isinstance(node, EmptyExpressionNode):
            return 0
        else:
            return sum(map(Interactor.count_tokens, node.children()))

    def get_token_info(self, i):
        return self.get_tok(i), self.get_line(i), self.get_col(i)

    def show_ambiguous_sentence(self):
        max_line = max(self.model.get_py_value(self.variables[f'line${i}']) for i in range(1, self.word_len + 1))
        max_col = max(self.model.get_py_value(self.variables[f'col${i}']) for i in range(1, self.word_len + 1))
        if get_cmd_args().serialize:
            sentence = []
            for i in range(1, self.word_len + 1):
                sentence.append(self.get_token_info(i))
            original_print(json.dumps({'type': 'sentence', 'data': {'sentence': sentence}}))
            return
        else:
            buf = [
                ['␣' * self.tabstop for j in range(max_col)]
                for i in range(max_line)
            ]
            for i in range(1, self.word_len + 1):
                tok, line, col = self.get_token_info(i)
                buf[line - 1][col - 1] = tok.ljust(self.tabstop)
            for i in range(max_line):
                for j in range(max_col):
                    print(buf[i][j], end='')
                print()

    def show_reformatted_sentence(self, A, index):
        if A not in self.parse_tree_dict:
            error(f'{A} do not have an ambiguous derivation on 1st level.')
            return
        r = self.reformatted[A][index]
        if get_cmd_args().serialize:
            sentence = []
            for i in range(1, self.word_len + 1):
                tok = self.get_tok(i)
                line, col = r[i]
                sentence.append((tok, line, col))
            original_print(json.dumps({'type': 'sentence', 'data': {'sentence': sentence}}))
            return
        else:
            max_line = max(x[0] for x in r.values())
            max_col = max(x[1] for x in r.values())
            buf = [
                ['␣' * self.tabstop for j in range(max_col)]
                for i in range(max_line)
            ]
            for i in range(1, self.word_len + 1):
                tok = self.get_tok(i)
                line, col = r[i]
                buf[line - 1][col - 1] = tok.ljust(self.tabstop)
            for i in range(max_line):
                for j in range(max_col):
                    print(buf[i][j], end='')
                print()

    def list_rules(self, A=None):
        table = PrettyTable()
        if A is None:
            table.field_names = ('index', 'uuid', 'variable', 'type', 'description')
            table.add_rows(
                (x._index, x.uuid.hex, x.variable, type(x.expression).__name__, x.original_text) for x in self.rules)
            if get_cmd_args().serialize:
                rule_data = [
                    {'index': x._index, 'uuid': x.uuid.hex, 'variable': x.variable, 'type': type(x.expression).__name__,
                     'description': x.original_text}
                    for x in self.rules
                ]
                original_print(json.dumps({
                    'type': 'list',
                    'data': {
                        'name': 'rule',
                        'rule': rule_data
                    }
                }))
            else:
                print(table)
        else:
            table.field_names = ('index', 'type', 'description')
            table.add_rows((x._index, type(x.expression).__name__, x.original_text) for x in self.rule_dict[A])
            if get_cmd_args().serialize:
                rule_data = [
                    {'index': x._index, 'type': type(x.expression).__name__, 'description': x.original_text}
                    for x in self.rule_dict[A]
                ]
                original_print(json.dumps({
                    'type': 'list',
                    'data': {
                        'name': 'rule',
                        'rule': rule_data
                    }
                }))
            else:
                print(table)

    def show_rule(self, index):
        if not 0 <= index < len(self.rules):
            error(f'Index #{index} out of range; should be in 0 ~ {len(self.rules) - 1}')
            return
        print(self.rules[index].__dict__)
        print([x.__dict__ for x in self.rules[index].children])

    def show_ambiguous_derivations(self):
        for cond, (A, (hl, hr)) in self.amb:
            if self.model.get_py_value(cond, model_completion=True):
                print_metric({
                    "type": "deriv",
                    "data": {
                        "variable": A,
                        "interval": [hl, hr]
                    }
                })

    def list_parse_trees(self, nonterminal=None):
        def show_parse_trees_of_A(A):
            if not get_cmd_args().serialize:
                if A not in self.parse_tree_dict or not len(self.parse_tree_dict[A]):
                    print(HTML('<ansigray>Not found</ansigray>'))
                else:
                    table = PrettyTable()
                    table.field_names = ('index', 'sexpr')
                    table.add_rows((i, x.to_sexpr(show_root=True)[0]) for i, x in enumerate(self.parse_tree_dict[A]))
                    print(f'Parse trees of nonterminal: {A}')
                    print(table)
                print()
            else:
                if A not in self.parse_tree_dict or not len(self.parse_tree_dict[A]):
                    original_print(json.dumps({
                        "type": "parse_tree_list",
                        "data": []
                    }))
                else:
                    data = [{"index": i, "sexpr": x.to_sexpr(show_root=True)[0]} for i, x in enumerate(self.parse_tree_dict[A])]
                    original_print(json.dumps({
                        "type": "parse_tree_list",
                        "data": data
                    }))

        if nonterminal is None:
            for A in self.parse_tree_dict.keys():
                show_parse_trees_of_A(A)
        else:
            show_parse_trees_of_A(nonterminal)

    def show_parse_tree(self, A, index):
        if self.parse_tree_dict.get(A) is None:
            error(f'{A} do not have an ambiguous derivation on 1st level.')
            return
        d = self.parse_tree_dict[A]
        if not 0 <= index < len(d):
            error(f'Index #{index} out of range; should be in 0 ~ {len(d) - 1}')
            return
        Interactor.show_node(d[index], f"Parse tree #{index} of nonterminal {A}", compress=True)

    def print_variable_and_sentence(self):
        if get_cmd_args().serialize:
            return
        self.show_ambiguous_sentence()
        self.show_ambiguous_derivations()
        if not get_cmd_args().serialize:
            print(HTML('<b>NOTE</b>: indexing for tokens in the sentence starts at <ansired><b>1</b></ansired>. ' +
                       'Spaces in the sentence are denoted as `␣\'.'))
            print(HTML('<b>NEXT STEP</b>: List and review all parse trees. '
                       'Type <ansigreen>help</ansigreen> for available commands. '
                       'Command completion available with TAB key.'))

    def exec_(self):
        """
        The following commands are provided:

        <b>list <i>rule [A]</i></b>
            List the specified rule. If <i>A</i> is not specified, all rules are listed.
        <b>list <i>tree [A]</i></b>
            List all parse trees, or those starting from variable <i>A</i>.
        <b>show <i>sentence</i></b>
            Show the ambiguous sentence
        <b>show <i>tree A tree-index</i></b>
            Show the parse tree of <i>(A, tree-index)</i>
        <b>show <i>rule rule-index</i></b>
            Show the rule of <i>rule-index</i>
        <b>show <i>deriv</i></b>
            Show all ambiguous derivations
        <b>exit</b>
            Exit the REPL loop.
        <b>help</b>
            Show this help text.
        """
        completer_dict = {
            'list': {
                'rule': set(x[0] for x in self.mapper.variable_items()),
                'tree': {A: None for A in self.parse_tree_dict.keys()}
            },
            'show': {
                'sentence': {
                    A: None
                    for A in self.parse_tree_dict.keys()
                },
                'tree': {
                    A: None
                    for A in self.parse_tree_dict.keys()
                },
                'rule': None,
                'deriv': None
            },
            'help': None,
            'exit': None,
        }
        completer = NestedCompleter.from_nested_dict(completer_dict)
        history = FileHistory(".smt_disambig_history")
        session = PromptSession(history=history)

        def fail_unknown(cmd):
            error(f'Invalid command: <i>{" ".join(cmd)}</i>. Type help and press enter to get help.')
            raise ArgumentError()

        self.print_variable_and_sentence()
        print_metric({'type': 'repl'})
        while True:
            try:
                if get_cmd_args().batch:
                    cmd = input()
                else:
                    cmd = session.prompt('smt-ambig> ', completer=completer)
            except EOFError:
                break

            cmd = cmd.split()
            if not len(cmd):
                continue

            try:
                if cmd[0] == 'help':
                    from textwrap import dedent
                    print(HTML(dedent(self.exec_.__doc__ or '')))
                elif cmd[0] == 'list':
                    if not 2 <= len(cmd) <= 3:
                        fail_unknown(cmd)

                    A = None if len(cmd) == 2 else cmd[2]
                    if cmd[1] == 'rule':
                        self.list_rules(A)
                    elif cmd[1] == 'tree':
                        self.list_parse_trees(A)
                    else:
                        fail_unknown(cmd)

                elif cmd[0] == 'show':
                    if not 2 <= len(cmd):
                        fail_unknown(cmd)

                    if cmd[1] == 'sentence':
                        if len(cmd) == 2:
                            self.show_ambiguous_sentence()
                        else:
                            fail_unknown(cmd)
                    elif cmd[1] == 'tree':
                        if not len(cmd) == 4:
                            fail_unknown(cmd)
                        A, tree_index = cmd[2:]
                        self.show_parse_tree(A, int(tree_index))
                    elif cmd[1] == 'rule':
                        if not len(cmd) == 3:
                            fail_unknown(cmd)
                        self.show_rule(int(cmd[2]))
                    elif cmd[1] == 'deriv':
                        if not len(cmd) == 2:
                            fail_unknown(cmd)
                        self.show_ambiguous_derivations()
                elif cmd[0] == 'exit':
                    break
                else:
                    fail_unknown(cmd)
            except ArgumentError:
                continue
            except ValueError as e:
                error(e)
                continue

        return self.parse_tree_dict, self.reformatted
