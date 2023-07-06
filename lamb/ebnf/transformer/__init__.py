from lamb.ebnf.transformer.EquivalentVarTransformer import SCCSolver, canonicalize_variables
from lamb.ebnf.ast import RuleNode
from lamb.ebnf.transformer.DesugarTransformer import *
from lamb.ebnf.transformer.ExpansionTransformer import *
from lamb.ebnf.transformer.ReduceTransformer import *
from lamb.ebnf.transformer.Nullable import *

from typing import List


def convert_into_reduced_acyclic_2nf(rules: List[RuleNode]) -> Tuple[List[RuleNode], Tuple[Set[str], Set[str]], SCCSolver]:
    # debug_rules(rules)
    rules = desugar_rules(rules)
    # debug_rules(rules)
    rules = expand_rules(rules)
    # debug_rules(rules)
    rules = reduce_rules(rules)
    # debug_rules(rules)

    nullable, _ = get_nullable_variables(rules)
    rules, scc = canonicalize_variables(rules, nullable)
    nullable, ambig_nullable = get_nullable_variables(rules) # calculate again, because some vars are removed

    return rules, (nullable, ambig_nullable), scc
