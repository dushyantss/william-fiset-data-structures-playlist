class UnionFind:
    def __init__(self, size: int):
        if size <= 0:
            raise ValueError("Size must be greater than 0")

        self.size = size
        self.sz = [1 for _ in range(size)]
        self.id = [i for i in range(size)]
        self.num_components = size

    def find(self, p: int) -> int:
        root = p
        while root != self.id[root]:
            root = self.id[root]

        # Now we compress
        while p != root:
            p, self.id[p] = self.id[p], root

        return root

    def connected(self: UnionFind, p: int, q: int) -> bool:
        return self.find(p) is self.find(q)

    def component_size(self, p: int) -> int:
        return self.sz[self.find(p)]

    def __len__(self) -> int:
        return self.num_components

    def unify(self, p: int, q: int):
        root_p = self.find(p)
        root_q = self.find(q)

        if root_p is root_q:
            return

        if self.sz[root_p] < self.sz[root_q]:
            self.sz[root_q] += self.sz[root_p]
            self.id[root_p] = root_q
        else:
            self.sz[root_p] += self.sz[root_q]
            self.id[root_q] = root_p

        self.num_components -= 1
