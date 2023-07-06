import json
from lamb.interaction.metric_printer import print_metric
from lamb.utils.SymbolIdMapper import SymbolIdMapper
from lamb.interaction.cmd_args import cmd_args
from typing import Dict
from pysmt.shortcuts import Symbol
from pysmt.typing import INT


def extend_triple_array_by_one(new_len: int, variables: Dict, mapper: SymbolIdMapper):
    variables[f'line${new_len}'] = Symbol(f'line${new_len}', INT)
    variables[f'col${new_len}'] = Symbol(f'col${new_len}', INT)
    variables[f'x${new_len}'] = Symbol(f'x${new_len}', INT)
    for i in range(1, new_len + 1):
        for var in range(mapper._last_literal_id + 1, len(mapper) + 1):
            x_var_name = f'x${i}${new_len}${var}'
            variables[x_var_name] = Symbol(x_var_name)
            q_var_name = f'q${i}${new_len}${var}'
            variables[q_var_name] = Symbol(q_var_name)

    # variables for empty intervals
    # definition: consider an empty interval right located between the i-1 th and the ith element.
    # it is denoted as q${i}${i-1}${A_index}
    for A, A_index in mapper.variable_items():
        q_var_name = f'q${new_len}${new_len - 1}${A_index}'
        variables[q_var_name] = Symbol(q_var_name)

    print_metric({'type': 'var_count', 'data': {'count': len(variables)}})


def generate_triple_array(n: int, mapper: SymbolIdMapper):
    variables = dict() 
    for i in range(1, n + 1):
        extend_triple_array_by_one(i, variables, mapper)
    return variables
