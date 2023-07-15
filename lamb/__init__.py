#!/usr/bin/env python
import json

from pysmt.logics import QF_UFIDL
from pysmt.shortcuts import Or, Solver, Bool

from lamb.ebnf.ast.loader import load_file_into_ast
from lamb.ebnf.transformer import *
from lamb.ebnf.transformer.Ambiguous import get_nonempty_ambiguous_symbols
from lamb.interaction.cmd_args import get_cmd_args
from lamb.interaction.metric_printer import print_metric
from lamb.utils.DebugOutput import debug_rules
from lamb.utils.RuleDictBuilder import build_rule_dict
from lamb.utils.SymbolIdMapper import SymbolIdMapper
from lamb.utils.TimedExecution import run_with_time
from lamb.verification import extend_triple_array_by_one
from lamb.verification.condition.ambiguity import build_ambiguity_condition
from lamb.verification.condition.deductive import extend_deductive_condition_by_one
from lamb.verification.condition.linecol import extend_increasing_condition_by_one
from lamb.verification.condition.sentence_reachable import build_reachable_condition
from lamb.verification.condition.symbol_bound import extend_symbol_bound_by_one


def main(kwargs):
    ast = load_file_into_ast(kwargs.filename)
    if ast is None: return
    rules, (nullable, ambig_nullable), scc = convert_into_reduced_acyclic_2nf(ast.rules)
    # now rules only contain concat and layout constraints
    if kwargs.debug:
        debug_rules(rules)
    ambig: Set[str] = get_nonempty_ambiguous_symbols(rules)
    ambig.update(ambig_nullable)

    word_len = 0
    variables = {}
    with Solver(name='z3', logic=QF_UFIDL) as solver:
        mapper = SymbolIdMapper(rules, terminal=True)
        rule_dict = build_rule_dict(rules)
        start_var = kwargs.start_var or rules[0].variable

        if kwargs.verbose:
            print('Start Variable:', start_var)
            print('Nullable', nullable)
            print('Ambiguous N:', ambig_nullable)
            print('Ambiguous M:', ambig)
            # noinspection PyProtectedMember
            print('Mapping:', mapper._sym_to_id)
            for rule in rules:
                print(rule.original_text)

        if kwargs.serialize and kwargs.check_bound:
            # print ls2nf rule details
            rule_data = [
                {'uuid': x.uuid.hex, 'variable': x.variable, 'type': type(x.expression).__name__,
                 'description': x.original_text}
                for x in rules
            ]
            print(json.dumps({
                'type': 'list',
                'data': {
                    'name': 'rule',
                    'rule': rule_data
                }
            }))

        loop_running = True
        while loop_running:
            word_len += 1

            if kwargs.check_bound is not None and kwargs.check_bound < word_len:
                exit(0)

            print_metric({'type': 'word_len', 'data': {'length': word_len}})
            run_with_time(extend_triple_array_by_one, word_len, variables, mapper)
            run_with_time(extend_increasing_condition_by_one, word_len, solver, variables)
            run_with_time(extend_symbol_bound_by_one, word_len, variables, mapper, solver)
            run_with_time(extend_deductive_condition_by_one,
                          word_len, solver, variables,
                          mapper, rule_dict, nullable
                          )

            if word_len < kwargs.len:
                continue
            solver.push()

            amb = run_with_time(build_ambiguity_condition,
                                rule_dict, word_len, variables, mapper,
                                nullable, ambig_nullable)
            amb_cond = Bool(False)
            for cond, _ in amb:
                amb_cond = Or(amb_cond, cond)
            solver.add_assertion(amb_cond)

            result = run_with_time(solver.solve)

            if result:
                print_metric({'type': 'check_false_positive'})
                run_with_time(build_reachable_condition, start_var,
                              rule_dict, variables, mapper, word_len, solver, nullable)
                result = run_with_time(solver.solve)
                if result:
                    print_metric({'type': 'found', 'data': {'length': word_len}})
                    model = solver.get_model()

                    from lamb.interaction import Interactor
                    interact_delegate = Interactor(word_len, model, variables, mapper, amb, rules, nullable,
                                                   tabstop=kwargs.tabstop)
                    parse_tree_dict, reformatted = interact_delegate.exec_()
                    loop_running = False
            solver.pop()

def entrypoint():    
    try:
        main(get_cmd_args())
    except KeyboardInterrupt:
        print('Interrupted. Exiting...')
        exit(1)
