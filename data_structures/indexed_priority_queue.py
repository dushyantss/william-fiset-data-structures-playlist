from array import array
from collections.abc import MutableMapping
from typing import Iterator


class MinIndexedDHeap(MutableMapping):
    def __init__(self, degree=2, max_size=16):
        if max_size <= 0:
            raise ValueError("max_size <= 0")

        self.d = max(2, degree)  # 2 is binary heap
        self.n = max(self.d + 1, max_size)  # max heap size
        self.pm = array("l", (-1 for _ in range(self.n)))  # ki to heap node
        self.im = array("l", (-1 for _ in range(self.n)))  # heap node to ki
        self.child = array("l", (0 for _ in range(self.n)))  # child for a parent node
        self.parent = array("l", (0 for _ in range(self.n)))  # parent for a child nodoe
        self.vals = [None] * self.n  # ki to values
        self.sz = 0  # heap size

        for i in range(self.n):
            self.parent[i] = (i - 1) // self.d
            self.child[i] = i * self.d + 1

    def __len__(self) -> int:
        return self.sz

    def add(self, ki: int, value):
        if ki in self:
            raise ValueError("Key Index already exists")
        if value is None:
            raise ValueError("Value should not be None")

        i = self.sz
        self.pm[ki] = i
        self.im[i] = ki
        self.vals[ki] = value
        self.sz += 1
        self.__swim(i)

    def __contains__(self, ki: int) -> bool:
        self.__key_in_bounds_or_raise(ki)
        return self.pm[ki] != -1

    def __delitem__(self, ki: int):
        self.__key_exists_or_throw(ki)
        i = self.pm[ki]
        # do heap deletion
        self.__swap(i, self.sz - 1)
        self.__sink(i)
        self.__swim(i)

        # remove the data
        self.pm[ki] = -1
        self.im[i] = -1
        value, self.vals[ki] = self.vals[ki], None
        self.sz -= 1
        return value

    def __setitem__(self, ki: int, value):
        self.__key_exists_and_value_not_none_or_raise(ki, value)
        i = self.im[ki]
        old_value, self.vals[ki] = self.vals[ki], value

        self.__sink(i)
        self.__swim(i)

        return old_value

    def __getitem__(self, ki: int):
        self.__key_exists_or_throw(ki)
        return self.vals[ki]

    def __iter__(self) -> Iterator:
        return self.keys()

    def keys(self) -> Iterator:
        return (ki for ki in self.im if ki != -1)

    def values(self):
        return (val for val in self.vals if val is not None)

    def items(self) -> Iterator:
        return ((ki, val) for ki, val in enumerate(self.vals) if val is not None)

    def peek_min_key_index(self) -> int:
        self.__is_not_empty_or_raise()
        return self.im[0]

    def poll_min_key_index(self) -> int:
        self.__is_not_empty_or_raise()
        min_key = self.peek_min_key_index()
        del self[min_key]
        return min_key

    def peek_min_value(self):
        min_ki = self.peek_min_key_index()
        return self.vals[min_ki]

    def poll_min_value(self):
        min_val = self.peek_min_value()
        min_ki = self.peek_min_key_index()
        del self[min_ki]
        return min_val

    def value_of(self, ki: int):
        self.__key_exists_or_throw(ki)

        return self.vals[ki]

    def increase(self, ki: int, value):
        self.__key_exists_and_value_not_none_or_raise(ki, value)
        if value > self.vals[ki]:
            self.vals[ki] = value
            self.__sink(self.pm[ki])

    def decrease(self, ki: int, value):
        self.__key_exists_and_value_not_none_or_raise(ki, value)
        if value < self.vals[ki]:
            self.vals[ki] = value
            self.__swim(self.pm[ki])

    def __swap(self, i1: int, i2: int):
        # i1 and i2 are heap node indices, not key indices
        k1, k2 = self.im[i1], self.im[i2]

        self.im[i1], self.im[i2] = k2, k1
        self.pm[k1], self.pm[k2] = i2, i1

    def __sink(self, i: int):
        j = self.__min_child(i)
        while j != -1:
            self.__swap(i, j)
            i, j = j, self.__min_child(j)

    def __swim(self, i: int):
        while (
            self.__value_for_i(i) is not None
            and self.__value_for_i(self.parent[i]) is not None
            and self.__value_for_i(i) < self.__value_for_i(self.parent[i])
        ):
            self.__swap(i, self.parent[i])
            i = self.parent[i]

    def __min_child(self, i: int) -> int:
        start = self.child[i]
        smallest = -1
        for idx in range(start, min(start + self.d, self.sz)):
            if smallest == -1 or self.__value_for_i(idx) < self.__value_for_i(smallest):
                smallest = idx
        return smallest

    def __value_for_i(self, i: int):
        return self.vals[self.im[i]]

    def __key_in_bounds_or_raise(self, ki: int):
        if ki < 0 or ki >= self.n:
            raise ValueError("Invalid key index, must be between 0 and max heap size")

    def __key_exists_or_throw(self, ki: int):
        if ki not in self:
            raise ValueError("Key Index does not exist")

    def __is_not_empty_or_raise(self):
        if not self:
            raise IndexError("Queue is empty")

    def __key_exists_and_value_not_none_or_raise(self, ki, value):
        if ki not in self:
            raise ValueError("Key Index does not exist")
        if value is None:
            raise ValueError("Value should not be None")
