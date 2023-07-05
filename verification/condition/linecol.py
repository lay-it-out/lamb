from pysmt.shortcuts import And, Or, GT, GE, Equals, Int
from pysmt.solvers.solver import Solver


def extend_increasing_condition_by_one(new_len: int, s: Solver, variables):
    if new_len > 1:
        s.add_assertion(Or(
            GT(variables[f'line${new_len}'], variables[f'line${new_len-1}']),
            And(
                Equals(variables[f'line${new_len}'], variables[f'line${new_len-1}']),
                GT(variables[f'col${new_len}'], variables[f'col${new_len-1}'])
            )
        ))
    s.add_assertion(GE(variables[f'line${new_len}'], Int(1)))
    s.add_assertion(GE(variables[f'col${new_len}'], Int(1)))

def generate_increasing_condition(n: int, s: Solver, variables):
    for i in range(1, n + 1):
        extend_increasing_condition_by_one(i, s, variables)
