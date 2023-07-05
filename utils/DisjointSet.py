class DisjointSet:
    def __init__(self, n: int = 5):
        self._n = n
        self._parent = list(range(n+1))
    
    def _get_parent(self, x):
        if x == self._parent[x]: return x
        else: return self._get_parent(self._parent[x])
    
    def get_representation_element(self, x):
        return self._get_parent(x)

    def union(self, x, y):
        x_pa, y_pa = self._get_parent(x), self._get_parent(y)
        self._parent[x_pa] = y_pa
