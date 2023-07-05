from typing import Dict

from utils.SymbolIdMapper import SymbolIdMapper
from pysmt.solvers.solver import Solver

def extend_symbol_bound_by_one(new_len: int, variables: Dict, mapper: SymbolIdMapper, s: Solver):
    s.add_assertion(mapper.limit_var_to_literal(variables[f'x${new_len}']))
