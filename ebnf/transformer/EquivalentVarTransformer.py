from collections import defaultdict
from typing import DefaultDict, List, Set, Tuple
from copy import deepcopy
from utils.SymbolIdMapper import SymbolIdMapper
from ebnf.ast import BinaryExpressionNode, EmptyExpressionNode, LiteralExpressionNode, RuleNode, UnaryExpressionNode, VariableExpressionNode

class SCCSolver:
    """Use Tarjan algorithm to solve all SCCs in the given graph
    """

    @staticmethod
    def get_unit_edges(rules: List[RuleNode], nullable: Set[str]) -> DefaultDict[str, List[str]]:
        edges: DefaultDict[str, List[str]] = defaultdict(list)
        for rule in rules:
            if isinstance(rule.expression, (LiteralExpressionNode, EmptyExpressionNode)):
                pass # Omit Literal / Empty Nodes
            elif isinstance(rule.expression, VariableExpressionNode):
                edges[rule.variable].append(rule.expression.variable)
            elif isinstance(rule.expression, UnaryExpressionNode):
                edges[rule.variable].append(rule.expression.expr.variable)
            elif isinstance(rule.expression, BinaryExpressionNode):
                if rule.expression.expr2.variable in nullable:
                    edges[rule.variable].append(rule.expression.expr1.variable)
                if rule.expression.expr1.variable in nullable:
                    edges[rule.variable].append(rule.expression.expr2.variable)
        
        return edges


    def __init__(self, rules: List[RuleNode], nullable: Set[str]):
        edges = SCCSolver.get_unit_edges(rules, nullable)
        self._edges = defaultdict(list)

        self._var_id_mapper = SymbolIdMapper(rules)
        self._start_variable_id = self._var_id_mapper.get_id_for_variable(rules[0].variable)
        

        for k, v in edges.items():
            idx = self._var_id_mapper.get_id_for_variable(k)
            self._edges[idx] = [self._var_id_mapper.get_id_for_variable(x) for x in v]
        self._n = len(self._var_id_mapper)


        self._dfn = [0] * (self._n + 1)
        self._low = [0] * (self._n + 1)

        self._stk = []
        self._scc_root = [0] * (self._n + 1)
        self._sccno = [0] * (self._n + 1)
        self._dfs_clock = 0
        self.scc_cnt = 0

        self.solve()


    def dfs(self, u: int):
        self._dfs_clock += 1
        self._dfn[u] = self._low[u] = self._dfs_clock
        self._stk.append(u)

        for v in self._edges[u]:
            if not self._dfn[v]:
                self.dfs(v)
                self._low[u] = min(self._low[u], self._low[v])
            elif not self._sccno[v]:
                self._low[u] = min(self._low[u], self._dfn[v])
        
        if self._low[u] == self._dfn[u]:
            self.scc_cnt += 1

            v = self._stk.pop()
            self._sccno[v] = self.scc_cnt
            while u != v:
                v = self._stk.pop()
                self._sccno[v] = self.scc_cnt
    

    def solve(self):
        for i in range(1, self._n + 1):
            if not self._dfn[i]: self.dfs(i)
        self._scc_children_list = [list() for i in range(self.scc_cnt + 1)]
        for i in range(1, self._n + 1):
            self._scc_children_list[self._sccno[i]].append(i)
        for scc in self._scc_children_list:
            if not scc: continue
            if self._sccno[scc[0]] != self._sccno[self._start_variable_id]:
                for u in scc: self._scc_root[u] = scc[0]
            else: # ensure that for the SCC containing start var, the start var itself is used as root
                for u in scc: self._scc_root[u] = self._start_variable_id
            if len(scc) > 1:
                cycle_variables = ','.join(map(lambda x: self._var_id_mapper.get_symbol(x), scc))
                raise ValueError(f'Cycle detected in 2NF; variables are: {cycle_variables}')


    def get_scc_root_variable(self, node: str) -> str:
        return self._var_id_mapper.get_symbol(self._scc_root[self._var_id_mapper.get_id_for_variable(node)])
    
    def get_variables_in_scc(self, scc_number: int) -> List[str]:
        """Get all variables in a specific SCC.
        The literals are never in an SCC, so feel free to use `get_id_for_variable`.
        """
        return [self._var_id_mapper.get_id_for_variable(v) for v in self._scc_children_list[scc_number]]


def canonicalize_variables(rules: List[RuleNode], nullable: Set[str]) -> Tuple[List[RuleNode], SCCSolver]:
    solver = SCCSolver(rules, nullable)
    ret = []
    for x in rules:
        rule = deepcopy(x)
        rule.variable = solver.get_scc_root_variable(rule.variable)
        if isinstance(rule.expression, VariableExpressionNode):
            rule.expression.variable = solver.get_scc_root_variable(rule.expression.variable)
        else:
            for child in rule.expression.children():
                assert isinstance(child, VariableExpressionNode)
                child.variable = solver.get_scc_root_variable(child.variable)
        ret.append(rule)
    return ret, solver
