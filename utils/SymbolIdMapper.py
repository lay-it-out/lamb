from collections import deque
from typing import Deque, Dict, List
from ebnf.ast import *
from pysmt.shortcuts import And

class SymbolIdMapper:
    
    def scan_symbols(self, rules: List[RuleNode], *, terminal=False):
        self.symbols: List[str] = []
        found: Set[str] = set()
        for rule in rules:
            q: Deque[ExpressionNode] = deque()
            q.append(rule.expression)
            found.add(rule.variable)

            while len(q):
                u = q.popleft()
                if isinstance(u, VariableExpressionNode):
                    found.add(u.variable)
                elif terminal and isinstance(u, LiteralExpressionNode):
                    found.add('"' + u.content + '"')
                for v in u.children():
                    q.append(v)
        self.symbols = list(found)
        self.symbols.sort()

        for i in range(len(self.symbols)):
            self._sym_to_id[self.symbols[i]] = i+1
            self._id_to_sym[i+1] = self.symbols[i]
            if self.symbols[i][0] == '"' and self.symbols[i][-1] == '"':
                self._last_literal_id = i+1
    
    def limit_var_to_literal(self, x):
        return And(1 <= x, x <= self._last_literal_id)

    def limit_var_to_variable(self, x):
        return And(self._last_literal_id < x, x <= len(self.symbols))

    def limit_var_to_existing(self, x):
        return 0 <= x and x < len(self.symbols)

    def __init__(self, rules: List[RuleNode], terminal=False):
        self._index = 0
        self._sym_to_id: Dict[str, int] = {}
        self._id_to_sym: Dict[int, str] = dict()

        self._last_literal_id = 0
        self.scan_symbols(rules, terminal=terminal)
    
    def get_id_for_variable(self, variable: str):
        assert variable[0] != '"' and variable[-1] != '"'
        return self._sym_to_id[variable]
    
    def get_id_for_literal(self, literal: str):
        return self._sym_to_id['"' + literal + '"']

    def get_symbol(self, index: int):
        return self._id_to_sym[index]
    
    def symbol_items(self, predict=lambda x: True):
        for i in range(1, len(self._id_to_sym) + 1):
            if not predict(self._id_to_sym[i]):
                continue
            assert self._id_to_sym[i] is not None
            yield (self._id_to_sym[i], i)
    
    def variable_items(self):
        yield from self.symbol_items(predict=lambda x: x[0] != '"' and x[-1] != '"')
    
    def literal_items(self):
        yield from self.symbol_items(predict=lambda x: x[0] == '"' and x[-1] == '"')

    def __len__(self):
        return len(self.symbols)
