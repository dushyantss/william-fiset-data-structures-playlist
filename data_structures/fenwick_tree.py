from array import array


def lsb(num: int) -> int:
    # -num is the 2's complement of num
    # Which is basically (~num) + 1
    # When we do ~num, we flip all 0's to 1's and vice-versa
    # Now, when we add 1, it starts a cascade, turning all 1's into 0's till it
    # encounters a 0
    # e.g. for num = 110010, ~num = 001101, ~num + 1 = 001110
    # e.g. for num = 111000, ~num = 000111, ~num + 1 = 001000
    # e.g. for num = 110101, ~num = 001010, ~num + 1 = 001011
    # Thus, adding 1 reverses the effect of `~` till it hits the first 0.
    # Now, the first 0 for ~num is the first 1 for num, which is the lsb.
    # Thus when we do num & -num, the only place where & would return 1 would be
    # the first 1 for num.
    return num & -num


class FenwickTree:
    # values array should be 1 based. Thus, values[0] should not get used
    def __init__(self, values=None, /, *, size=1):
        if not values:
            if size <= 0:
                raise ValueError("Size cannot be less than 1")
            self.tree = array("l", (0 for _ in range(size + 1)))
        else:
            self.tree = array("l", (val for val in values))
            for i in range(1, len(self.tree)):
                j = i + lsb(i)
                if j < len(self.tree):
                    self.tree[j] += self.tree[i]

    def prefix_sum(self, i: int) -> int:
        result = 0
        while i != 0:
            result += self.tree[i]
            i &= ~lsb(i)  # Equivalent to i -= lsb(i)

        return result

    def interval_sum(self, i: int, j: int) -> int:
        if j < i:
            raise ValueError("Bad interval, ensure i >= j")
        return self.prefix_sum(j) - self.prefix_sum(i - 1)

    def add(self, i: int, k: int):
        """
        Add 'k' to index 'i', one based
        """
        while i < len(self.tree):
            self.tree[i] += k
            i += lsb(i)

    def set(self, i: int, k: int):
        """
        Set index 'i' to be equal to k, one based
        """
        value = self.interval_sum(i, i)
        self.add(i, k - value)
