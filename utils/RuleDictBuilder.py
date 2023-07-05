from collections import defaultdict
from typing import DefaultDict, List
from ebnf.ast import RuleNode

def build_rule_dict(rules: List[RuleNode]) -> DefaultDict[str, List[RuleNode]]:
    rule_dict = defaultdict(list)
    for y in rules: rule_dict[y.variable].append(y)
    return rule_dict