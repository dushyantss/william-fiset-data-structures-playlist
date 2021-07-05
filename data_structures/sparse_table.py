import math
from array import array


class MinSparseTable:
    def __init__(self, values):
        self.n = len(values)
        self.p = int(math.log2(self.n))

        self.dp = [array("l", (0 for i in range(self.n)))] * (self.p + 1)
        self.it = [array("l", (0 for i in range(self.n)))] * (self.p + 1)

        for i in range(self.n):
            self.dp[0][i] = values[i]
            self.it[0][i] = i

        self.log2 = array("l", (0 for _ in range(self.n + 1)))

        for i in range(2, self.n + 1):
            self.log2[i] = self.log2[i // 2] + 1

        for p in range(1, self.p + 1):
            for i in range(self.n + 1 - (1 << p)):
                left_interval = self.dp[p - 1][i]
                right_idx = i + (1 << (p - 1))
                right_interval = self.dp[p - 1][right_idx]
                self.dp[p][i] = min(left_interval, right_interval)

                if left_interval <= right_interval:
                    self.it[p][i] = self.it[p - 1][i]
                else:
                    self.it[p][i] = self.it[p - 1][right_idx]

    def query_min(self, l: int, r: int):
        length = r - l + 1
        p = self.log2[length]
        k = 1 << p
        return min(self.dp[p][l], self.dp[p][r - k + 1])

    def query_min_idx(self, l: int, r: int) -> int:
        length = r - l + 1
        p = self.log2[length]
        k = 1 << p
        if self.dp[p][l] <= self.dp[p][r - k + 1]:
            return self.it[p][l]
        else:
            return self.it[p][r - k + 1]
