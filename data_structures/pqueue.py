class PQueue:
    def __init__(self, size=1, elems=None):
        self.map = {}
        if elems:
            self.heap_size = len(elems)
            self.heap = [e for e in elems]
            for i, e in enumerate(elems):
                self.__map_add(e, i)

            sink_start = max(0, self.heap_size / 2 - 1)
            for i in range(sink_start, -1, -1):
                self.__sink(i)

            return

        if not isinstance(size, int):
            raise TypeError("Size must be an int")
        if size <= 0:
            raise ValueError("Size must be greater than 0")

        self.heap_size = 0
        self.heap = [None] * size

    def __len__(self):
        return self.heap_size

    def clear(self):
        for i in range(len(self.heap)):
            self.heap[i] = None
        self.heap_size = 0
        self.map.clear()

    def peek(self):
        if self.heap:
            return self.heap[0]

        return None

    def poll(self):
        return self.__remove_at(0)

    def contains(self, elem):
        return elem in self.map

    def append(self, elem):
        if elem is None:
            raise ValueError("elem should not be None")

        if self.heap_size < len(self.heap):
            self.heap[self.heap_size] = elem
        else:
            self.heap.append(elem)

        self.__map_add(elem, self.heap_size)

        self.__swim(self.heap_size)
        self.heap_size += 1

    def remove(self, elem):
        if elem is None:
            return False

        i = self.__map_get(elem)
        if i is not None:
            self.__remove_at(i)

        return i is not None

    def is_min_heap(self, k=0):
        if not isinstance(k, int):
            return TypeError("k must be int")
        if k < 0:
            return ValueError("k must be a positive integer")

        if k >= self.heap_size:
            return True

        left = 2 * k + 1
        right = 2 * k + 2

        if left < self.heap_size and self.__less(k, left):
            return False
        if right < self.heap_size and self.__less(k, right):
            return False

        return self.is_min_heap(left) and self.is_min_heap(right)

    def __less(self, i, j):
        node_i = self.heap[i]
        node_j = self.heap[j]
        return node_i <= node_j

    def __swim(self, k):
        parent = (k - 1) // 2

        while k > 0 and self.__less(k, parent):
            self.__swap(parent, k)
            k = parent
            parent = (k - 1) // 2

    def __sink(self, k):
        while True:
            left = 2 * k + 1
            right = 2 * k + 2
            smallest = left

            if right < self.heap_size and self.__less(right, left):
                smallest = left

            if left >= self.heap_size or self.__less(k, smallest):
                break

            self.__swap(smallest, k)
            k = smallest

    def __swap(self, i, j):
        i_elem, j_elem = self.heap[i], self.heap[j]
        self.heap[i], self.heap[j] = j_elem, i_elem
        self.__map_swap(i_elem, j_elem, i, j)

    def __remove_at(self, i):
        if not self.heap:
            return None

        self.heap_size -= 1
        removed_data = self.heap[i]
        self.__swap(i, self.heap_size)

        self.heap[self.heap_size] = None
        self.__map_remove(removed_data, self.heap_size)

        if i is self.heap_size:
            return removed_data

        elem = self.heap[i]

        self.__sink(i)

        if self.heap[i] is elem:
            self.__swim(i)

        return removed_data

    def __map_add(self, value, index):
        indices = self.map.get(value, set())
        indices.add(index)
        self.map[value] = indices

    def __map_remove(self, value, index):
        indices = self.map[value]
        indices.remove(index)
        if not indices:
            del self.map[value]

    def __map_get(self, value):
        if value in self.map:
            return self.map[value][-1]

        return None

    def __map_swap(self, i_elem, j_elem, i, j):
        self.map[i_elem].remove(i)
        self.map[i_elem].remove(j)

        self.map[j_elem].remove(j)
        self.map[j_elem].remove(i)
