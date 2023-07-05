import os
from typing import List

import pydot

from ebnf.ast import RuleNode


def debug_rules(rules: List[RuleNode]):
    try:
        os.mkdir('debug/output/')
    except:
        pass
    try:
        for x in os.listdir('debug/output/'):
            os.remove(f'debug/output/{x}')
    except:
        pass

    count = 0
    for x in rules:
        count += 1
        dot = pydot.Dot('ast', graph_type='graph')  # type: ignore
        x.draw_graphviz(dot)
        with open('./debug/1.dot', 'w') as f:
            f.write(dot.to_string())
        dot.write_png(f'debug/output/{x.variable}_{count}.png')  # type: ignore
