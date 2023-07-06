from functools import reduce

import pysmt
import z3
from pysmt.shortcuts import Solver, And, Equals, TRUE, Not, Int, Symbol, Or, FALSE, Iff
from pysmt.typing import INT

from lamb.interaction.synthesis import get_predicate_vars, get_predicate_choices
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

from lamb.interaction.cmd_args import cmd_args
from lamb.interaction.metric_printer import print_metric
from lamb.interaction.nested import NestedCompleter
from lamb.interaction.parse_tree import search_all_ambiguous_trees
from lamb.interaction.refine import generate_all_constraint_op, refine


def error(msg):
    if cmd_args.serialize:
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
            if cmd_args.serialize:
                original_print(json.dumps({'type': 'image', 'data': fp.name}))
            else:
                open_python.start(fp.name)
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

    def convert_ast_to_deductive_vars(self, node: ASTNode, variables: dict,
                                      interval: Tuple[int, int], syn_prefix: str) -> list:
        if isinstance(node, EmptyExpressionNode) or isinstance(node, LiteralExpressionNode):
            return []  # leaf-level condition already generated
        elif isinstance(node, UnaryExpressionNode) or isinstance(node, BinaryExpressionNode):
            assert node.rule is not None
            # choices = get_predicate_choices(node.rule, variables, interval[0], interval[1], syn_prefix=syn_prefix)
            A_index = self.mapper.get_id_for_variable(node.rule.variable)
            deductive = variables[f'{syn_prefix}x${interval[0]}${interval[1]}${A_index}']
            # new_rule = And(deductive, choices)
            new_rule = deductive
            if isinstance(node, UnaryExpressionNode):
                return [new_rule] + self.convert_ast_to_deductive_vars(node.children()[0], variables, interval,
                                                                       syn_prefix)
            else:
                assert isinstance(node, BinaryExpressionNode)
                assert len(node.children()) == 2
                lhs = node.children()[0]
                rhs = node.children()[1]
                lhs_size = self.count_tokens(lhs)
                interval_left = (interval[0], interval[0] + lhs_size - 1)
                interval_right = (interval[0] + lhs_size, interval[1])

                return [new_rule] + self.convert_ast_to_deductive_vars(lhs, variables, interval_left, syn_prefix) \
                    + self.convert_ast_to_deductive_vars(rhs, variables, interval_right, syn_prefix)
        else:
            raise TypeError("unexpected node type")

    def get_ast_root_deductive_var(self, node: ASTNode, variables: dict, interval: Tuple[int, int], syn_prefix: str):
        assert node.rule is not None
        rule: RuleNode = node.rule
        A = rule.variable
        A_index = self.mapper.get_id_for_variable(rule.variable)
        return variables[f'{syn_prefix}x${interval[0]}${interval[1]}${A_index}']

    def convert_ast_to_rules(self, node: ASTNode, variables: dict,
                             interval: Tuple[int, int], syn_prefix: str) -> list:

        if cmd_args.verbose:
            print(f'recurse {interval}')
        assert node.rule is not None
        rule: RuleNode = node.rule
        A = rule.variable
        A_index = self.mapper.get_id_for_variable(rule.variable)
        premise = variables[f'{syn_prefix}x${interval[0]}${interval[1]}${A_index}']

        if isinstance(rule.expression, LiteralExpressionNode):
            assert interval[0] == interval[1]
            index_literal = self.mapper.get_id_for_literal(rule.expression.content)
            implied = Equals(variables[f'{syn_prefix}x${interval[0]}'], Int(index_literal))
            new_rule = Iff(premise, implied)
            return [new_rule]
        elif isinstance(rule.expression, VariableExpressionNode):
            B = rule.expression.variable
            index_B = self.mapper.get_id_for_variable(B)
            assert A != B
            implied = variables[f'{syn_prefix}x${interval[0]}${interval[1]}${index_B}']
            new_rule = Iff(premise, implied)
            return [new_rule] + self.convert_ast_to_rules(node.children()[0], variables, interval, syn_prefix)
        elif isinstance(rule.expression, UnaryExpressionNode):
            assert isinstance(rule.expression.expr, VariableExpressionNode)
            assert rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideOp \
                   or rule.expression.op == UnaryExpressionNode.UnaryOp.SameLineOp \
                   or rule.expression.op == UnaryExpressionNode.UnaryOp.OffsideEquOp

            B = rule.expression.expr.variable
            index_B = self.mapper.get_id_for_variable(B)
            assert A != B

            cond1 = (variables[f'{syn_prefix}x${interval[0]}${interval[1]}${index_B}'])
            cond2 = get_predicate_choices(rule, variables, interval[0], interval[1], syn_prefix=syn_prefix)

            implied = And(cond1, cond2)
            new_rule = Iff(premise, implied)
            return [new_rule] + self.convert_ast_to_rules(node.children()[0], variables, interval, syn_prefix)
        elif isinstance(rule.expression, BinaryExpressionNode):
            assert isinstance(rule.expression.expr1, VariableExpressionNode)
            assert isinstance(rule.expression.expr2, VariableExpressionNode)
            B, C = rule.expression.expr1.variable, rule.expression.expr2.variable
            index_B = self.mapper.get_id_for_variable(B)
            index_C = self.mapper.get_id_for_variable(C)

            i, j = interval[0], interval[1]

            children = node.children()
            if len(children) == 2:
                lhs, rhs = children[0], children[1]
                lhs_size = self.count_tokens(lhs)
                interval_left = (interval[0], interval[0] + lhs_size - 1)
                interval_right = (interval[0] + lhs_size, interval[1])

                h = interval_left[1]
                cond1 = (variables[f'{syn_prefix}x${i}${h}${index_B}'])
                cond2 = (variables[f'{syn_prefix}x${h + 1}${j}${index_C}'])
                cond3 = get_predicate_choices(rule, variables, i, h + 1, syn_prefix=syn_prefix)
                implied = And(cond1, cond2, cond3)
            else:
                assert len(children) == 1
                # check: which side is null?
                child_var = children[0].rule.variable
                if child_var == B:
                    lhs, rhs = children[0], None
                    interval_left, interval_right = interval, None
                    assert A != B
                    implied = variables[f'{syn_prefix}x${i}${j}${index_B}']
                else:
                    assert child_var == C
                    lhs, rhs = None, children[0]
                    interval_left, interval_right = None, interval
                    assert A != C
                    implied = variables[f'{syn_prefix}x${i}${j}${index_C}']

            new_rule = Iff(premise, implied)
            ret = [new_rule]
            if lhs is not None:
                ret.extend(self.convert_ast_to_rules(lhs, variables, interval_left, syn_prefix))
            if rhs is not None:
                ret.extend(self.convert_ast_to_rules(rhs, variables, interval_right, syn_prefix))
            return ret
        else:
            raise NotImplementedError()

    def get_token_info(self, i):
        return self.get_tok(i), self.get_line(i), self.get_col(i)

    def show_ambiguous_sentence(self):
        max_line = max(self.model.get_py_value(self.variables[f'line${i}']) for i in range(1, self.word_len + 1))
        max_col = max(self.model.get_py_value(self.variables[f'col${i}']) for i in range(1, self.word_len + 1))
        if cmd_args.serialize:
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
        if cmd_args.serialize:
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
            if cmd_args.serialize:
                rule_data = [
                    {'index': x._index, 'uuid': x.uuid.hex, 'variable': x.variable, 'type': type(x.expression).__name__, 'description': x.original_text}
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
            if cmd_args.serialize:
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

    def refine_variable(self, A, all=False):
        if A not in self.parse_tree_dict:
            error(f'{A} do not have an ambiguous derivation on 1st level.')
            return

        res = refine(self.parse_tree_dict[A], self.reformatted[A], self.rules, *self.amb_intervals[A])
        rule_uuid_dict = {x.uuid: x for x in self.rules}

        table = PrettyTable()
        table.field_names = ('rule index', 'tree_id', 'variable', 'type', 'refining suggestion')
        table.add_rows(
            (rule_uuid_dict[rule_uuid]._index, rule_uuid_dict[rule_uuid]._tree_id, rule_uuid_dict[rule_uuid].variable,
             type(rule_uuid_dict[rule_uuid].expression).__name__, ','.join(map(str, available_ops)))
            for rule_uuid, available_ops in res.items() if
            all or available_ops != generate_all_constraint_op(rule_uuid_dict[rule_uuid])
        )
        table_json = json.loads(table.get_json_string())

        if cmd_args.serialize:
            original_print(json.dumps({'type': 'refine', 'data': {'refine': table_json[1:]}}))
        else:
            print('Possible refinement:')
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
                if not cmd_args.serialize:
                    print(A, f':: Hole starting with {A} on [{hl}, {hr}]')
                else:
                    original_print(json.dumps({
                        "type": "deriv",
                        "data": {
                            "variable": A,
                            "interval": [hl, hr]
                        }
                    }))

    def list_parse_trees(self, nonterminal=None):
        def show_parse_trees_of_A(A):
            if not cmd_args.serialize:
                table = PrettyTable()
                table.field_names = ('index', 'type')
                table.add_rows((i, type(x).__name__) for i, x in enumerate(self.parse_tree_dict[A]))
                print(f'Parse trees of nonterminal: {A}')
                if A not in self.parse_tree_dict or not len(self.parse_tree_dict[A]):
                    print(HTML('<ansigray>Not found</ansigray>'))
                else:
                    print(table)
                print()
            else:
                if A not in self.parse_tree_dict or not len(self.parse_tree_dict[A]):
                    original_print(json.dumps({
                        "type": "parse_tree_list",
                        "data": []
                    }))
                else:
                    data = [{"index": i, "type": type(x).__name__} for i, x in enumerate(self.parse_tree_dict[A])]
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

    def reformat_token_of_parse_tree(self, A, tree_index, word_index, position):
        if self.parse_tree_dict.get(A) is None:
            error(f'{A} do not have an ambiguous derivation on 1st level.')
            return
        d = self.parse_tree_dict[A]
        if not 0 <= tree_index < len(d):
            error(f'Index #{tree_index} out of range; should be in 0 ~ {len(d) - 1}')
            return
        if not 1 <= word_index <= self.word_len:
            error(f'Word index ${word_index} out of range; should be in 1 ~ {self.word_len}')

        x = self.reformatted[A][tree_index]
        line, col = x[word_index]
        new_line, new_col = position
        if new_line > 0:
            if not cmd_args.serialize: print(f'Setting line = {new_line}')
            line = new_line
        if new_col > 0:
            if not cmd_args.serialize: print(f'Setting col = {new_col}')
            col = new_col
        x[word_index] = (line, col)

    def verify_reformatted(self, A) -> Dict[Tuple[int, int], bool]:
        d = self.parse_tree_dict[A]
        predicate_vars, variables = self.generate_synthesis_vars(d)
        predicate_all_false = And(*[Not(x) for x in predicate_vars.values()])

        parsable = dict()
        hl, hr = 1, self.word_len
        for (A2, (hl, hr)) in self.amb_intervals.items():
            if A2 == A:
                break
        for sentence_index in range(len(d)):
            for tree_index in range(len(d)):
                syn_prefix = f's{sentence_index}$t{tree_index}$'
                sentence_cond = self.generate_synthesis_sentence_assignment(A, sentence_index, tree_index,
                                                                            variables)
                ast_rules = self.convert_ast_to_rules(d[tree_index], variables, (hl, hr), syn_prefix)
                root_deductive_var = self.get_ast_root_deductive_var(d[tree_index], variables, (hl, hr),
                                                                     syn_prefix)
                with Solver(name='z3') as solver:
                    solver.add_assertion(predicate_all_false)
                    solver.add_assertion(sentence_cond)
                    for x in ast_rules:
                        solver.add_assertion(x)
                    solver.add_assertion(root_deductive_var)

                    res = solver.solve()
                    parsable[(sentence_index, tree_index)] = res

        return parsable

    def synthesize_constraints(self, A, *, refuse=False) -> Optional[List[tuple[BinaryExpressionNode.BinaryOp | UnaryExpressionNode.UnaryOp, str, str]]]:
        if self.parse_tree_dict.get(A) is None:
            error(f'{A} do not have an ambiguous derivation on 1st level.')
            return
        d = self.parse_tree_dict[A]
        hl, hr = 1, self.word_len
        for (A2, (hl, hr)) in self.amb_intervals.items():
            if A2 == A:
                break

        sentence_tree_parsable = self.verify_reformatted(A)
        has_reject = (sum([int(x) for x in sentence_tree_parsable.values()]) != len(sentence_tree_parsable))
        if has_reject and not refuse:
            error(f'warning: some reformatted sentences of {A} are not equivalent to the counterexample')
            error('pairs: ' + str([k for k, v in sentence_tree_parsable.items() if not v]))

        # Generate Vars for Z3
        predicate_vars, variables = self.generate_synthesis_vars(d)

        with Solver(name='z3') as s:
            main_clause_parts = []

            for sentence_index in range(len(d) + refuse):
                for tree_index in range(len(d)):
                    syn_prefix = f's{sentence_index}$t{tree_index}$'

                    sentence_cond = self.generate_synthesis_sentence_assignment(A, sentence_index, tree_index, variables,
                                                                                is_reject_term=(sentence_index == len(d)))
                    main_clause_parts.append(sentence_cond)

                    if cmd_args.verbose:
                        print('sentence, tree =', (sentence_index, tree_index))

                    ast_rules = self.convert_ast_to_rules(d[tree_index], variables, (hl, hr), syn_prefix)
                    main_clause_parts.extend(ast_rules)
                    root_deductive_var = self.get_ast_root_deductive_var(d[tree_index], variables, (hl, hr), syn_prefix)
                    if sentence_index == tree_index:
                        main_clause_parts.append(root_deductive_var)
                    else:
                        main_clause_parts.append(Not(root_deductive_var))

                if cmd_args.verbose:
                    print('parts len', len(main_clause_parts))

            o = z3.Optimize()
            for c in main_clause_parts:
                o.add(s.converter.convert(c))
            for rej in self.rejected_constraint:
                o.add(s.converter.convert(Not(variables[rej])))
            for _, v in enumerate(predicate_vars.values()):
                o.add_soft(s.converter.convert(Not(v)))
            result = o.check()
            if cmd_args.verbose:
                print('Synthesizer result:', result)

            if result != z3.sat:
                print("[ERROR] synthesizer returned UNSAT!")
                unsat_s = z3.Solver()
                unsat_s.set(unsat_core=True)
                for index, ex in enumerate(main_clause_parts):
                    unsat_s.assert_and_track(s.converter.convert(ex), f'm${index}')
                print(unsat_s.check())
                core = unsat_s.unsat_core()
                core_index = map(lambda x: int(x.sexpr()[2:]), core)
                print("---")
                for k in core_index:
                    print(k, pysmt.shortcuts.serialize(pysmt.shortcuts.simplify(main_clause_parts[k])))
                return None
            else:
                model = o.model()

                if cmd_args.verbose:
                    for index, c in enumerate(main_clause_parts):
                        print(pysmt.shortcuts.serialize(pysmt.shortcuts.simplify(c)))
                        print(f'eval{index}:', model.eval(s.converter.convert(c), model_completion=True))
                    print()
                    print('predicates:')
                new_predicate_vars = []
                for k, v in predicate_vars.items():
                    v = model.eval(s.converter.convert(v), model_completion=True)
                    if v:
                        if cmd_args.verbose:
                            print(k)
                        new_predicate_vars.append(k)

                uuid_rule_dict = {x.uuid.hex: x for x in self.rules}
                new_predicates = []
                for k in new_predicate_vars:
                    k: str
                    pred_var_pars = k.split('$')
                    pred_typename, rule_uuid = pred_var_pars[1], pred_var_pars[2]
                    rule = uuid_rule_dict[rule_uuid]
                    try:
                        op = BinaryExpressionNode.BinaryOp[pred_typename]
                    except KeyError:
                        op = UnaryExpressionNode.UnaryOp[pred_typename]
                    new_predicates.append((op, rule.tree_id, k))
                return new_predicates

    def reject_constraint_var(self, var_name):
        self.rejected_constraint.add(var_name)

    def generate_synthesis_sentence_assignment(self, A, sentence_index, tree_index, variables, is_reject_term=False):
        syn_prefix = f's{sentence_index}$t{tree_index}$'
        # assignment to x, line, col
        x_cond = And(Equals(variables[f'{syn_prefix}x${i}'], Int(self.get_var(f'x${i}')))
                     for i in range(1, self.word_len + 1))
        pos_seq = None if is_reject_term else self.reformatted[A][sentence_index]
        line_cond = And(Equals(variables[f'{syn_prefix}line${i}'], Int(self.get_line(i) if is_reject_term else pos_seq[i][0]))
                        for i in range(1, self.word_len + 1))
        col_cond = And(Equals(variables[f'{syn_prefix}col${i}'], Int(self.get_col(i) if is_reject_term else pos_seq[i][1]))
                       for i in range(1, self.word_len + 1))
        sentence_cond = And(x_cond, line_cond, col_cond)
        return sentence_cond

    def generate_synthesis_vars(self, d):
        predicate_vars = get_predicate_vars(self.rules)
        variables = {}
        for sentence_index in range(len(d) + 1):
            for tree_index in range(len(d)):
                syn_prefix = f's{sentence_index}$t{tree_index}$'
                for new_len in range(1, self.word_len + 1):
                    variables[f'{syn_prefix}line${new_len}'] = Symbol(f'{syn_prefix}line${new_len}', INT)
                    variables[f'{syn_prefix}col${new_len}'] = Symbol(f'{syn_prefix}col${new_len}', INT)
                    variables[f'{syn_prefix}x${new_len}'] = Symbol(f'{syn_prefix}x${new_len}', INT)
                    for i in range(1, new_len + 1):
                        for var in range(self.mapper._last_literal_id + 1, len(self.mapper) + 1):
                            x_var_name = f'{syn_prefix}x${i}${new_len}${var}'
                            variables[x_var_name] = Symbol(x_var_name)
        variables.update(predicate_vars)
        return predicate_vars, variables

    def exec_(self):
        """
        The following commands are provided:

        <b>list <i>rule [A]</i></b>
            List the specified rule. If <i>A</i> is not specified, all rules are listed.
        <b>list <i>tree [A]</i></b>
            List all parse trees, or those starting from variable <i>A</i>.
        <b>show <i>sentence [A tree-index]</i></b>
            Show all sentences, or the (refined) sentence of tree <i>(A, tree-index)</i>
        <b>show <i>tree A tree-index</i></b>
            Show the parse tree of <i>(A, tree-index)</i>
        <b>show <i>rule rule-index</i></b>
            Show the rule of <i>rule-index</i>
        <b>show <i>deriv</i></b>
            Show all ambiguous derivations
        <b>reformat <i>A tree-index word-index line col [word-index line col]*</i></b>, or:
        <b>reformat <i>A tree-index word-index, line, col [word-index, line, col]*</i></b>
            Relocate the specified token at <i>word-index</i> corresponding to the parse tree
            <i>(A, tree-index)</i> to <i>line, col</i>. If <i>line</i> / <i>col</i> is -1, the
            corresponding original value is kept.
        <b>refine <i>A</i> [-a]</b>
            Apply the refine algorithm on all rules starting with <i>A</i>, then output
            refinement suggestions. Use -a to output all suggestions.
        <b>syn <i>A</i></b>
            Use MaxSMT to synthesize minimum set of layout predicates that can be added.
        <b>exit</b>
            Exit the REPL loop.
        <b>help</b>
            Show this help text.
        """
        completer_dict = {
            'list': {
                'rule': set(x[0] for x in self.mapper.variable_items()),
                'tree': set(x[0] for x in self.mapper.variable_items())
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
            'reformat': {
                A: None
                for A in self.parse_tree_dict.keys()
            },
            'refine': {
                A: None
                for A in self.parse_tree_dict.keys()
            },
            'help': None,
            'exit': None,
            'syn': {
                A: None
                for A in self.parse_tree_dict.keys()
                },
            'refuse': {
                A: None
                for A in self.parse_tree_dict.keys()
            },
            'rej': None
        }
        completer = NestedCompleter.from_nested_dict(completer_dict)
        history = FileHistory(".smt_disambig_history")
        session = PromptSession(history=history)

        def fail_unknown(cmd):
            error(f'Invalid command: <i>{" ".join(cmd)}</i>. Type help and press enter to get help.')
            raise ArgumentError()

        print_metric({'type': 'repl'})
        while True:
            try:
                if cmd_args.batch:
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
                        if not (len(cmd) == 2 or len(cmd) == 4):
                            fail_unknown(cmd)
                        if len(cmd) == 2:
                            self.show_ambiguous_sentence()
                        else:
                            A, tree_index = cmd[2:]
                            self.show_reformatted_sentence(A, int(tree_index))
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

                elif cmd[0] == 'reformat':
                    if len(cmd) < 3:
                        fail_unknown(cmd)
                    A, tree_index = cmd[1:3]
                    rest = ' '.join(cmd[3:]).replace(',', ' ').split(' ')
                    rest = filter(lambda x: len(x), rest)
                    rest = list(map(int, rest))
                    if len(rest) % 3 != 0: fail_unknown(cmd)
                    tuple_cnt = len(rest) // 3
                    for i in range(tuple_cnt):
                        word_index, line, col = rest[3 * i:3 * i + 3]
                        self.reformat_token_of_parse_tree(A, int(tree_index), int(word_index), (int(line), int(col)))
                    self.show_reformatted_sentence(A, int(tree_index))
                elif cmd[0] == 'refine':
                    if len(cmd) != 2 and len(cmd) != 3:
                        fail_unknown(cmd)
                    A = cmd[1]
                    all = False
                    if len(cmd) == 3:
                        if cmd[2] == '-a':
                            all = True
                        else:
                            fail_unknown(cmd)
                    self.refine_variable(A, all)
                elif cmd[0] == 'syn':
                    if len(cmd) != 2:
                        fail_unknown(cmd)
                    res = self.synthesize_constraints(cmd[1])
                    print(res)
                elif cmd[0] == 'refuse':
                    if len(cmd) != 2:
                        fail_unknown(cmd)
                    res = self.synthesize_constraints(cmd[1], refuse=True)
                    print(res)
                elif cmd[0] == 'rej':
                    if len(cmd) != 2:
                        fail_unknown(cmd)
                    self.reject_constraint_var(cmd[1])
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
