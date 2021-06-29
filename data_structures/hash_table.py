from __future__ import annotations
from collections import deque
from collections.abc import MutableMapping
from enum import Enum
import math
from typing import Iterator, Optional


DEFAULT_CAPACITY_SEPARATE_CHAINING = 3
DEFAULT_CAPACITY_OPEN_ADDRESSING = 8
DEFAULT_LOAD_FACTOR_SEPARATE_CHAINING = 0.75
DEFAULT_LOAD_FACTOR_OPEN_ADDRESSING = 0.45


class TableType(Enum):
    SEPARATE_CHAINING = 1
    OPEN_ADDRESSING = 2


class HashTable(MutableMapping):
    def __init__(
        self,
        capacity: int = None,
        max_load_factor: float = None,
        /,
        *,
        table_type: TableType = TableType.SEPARATE_CHAINING,
    ):
        if table_type == TableType.SEPARATE_CHAINING:
            if capacity is None:
                capacity = DEFAULT_CAPACITY_SEPARATE_CHAINING
            if max_load_factor is None:
                max_load_factor = DEFAULT_LOAD_FACTOR_SEPARATE_CHAINING
            self.table = SeparateChaining(capacity, max_load_factor)
        elif table_type == TableType.OPEN_ADDRESSING:
            if capacity is None:
                capacity = DEFAULT_CAPACITY_OPEN_ADDRESSING
            if max_load_factor is None:
                max_load_factor = DEFAULT_LOAD_FACTOR_OPEN_ADDRESSING
            self.table = OpenAddressing(capacity, max_load_factor)

    def clear(self):
        self.table.clear()

    def __getitem__(self, key):
        return self.table.__getitem__(key)

    def __setitem__(self, key, value):
        return self.table.__setitem__(key, value)

    def __delitem__(self, key):
        return self.table.__delitem__(key)

    def __contains__(self, key):
        return self.table.__contains__(key)

    def __len__(self):
        return len(self.table)

    def __iter__(self):
        return iter(self.table)

    def keys(self):
        return self.table.keys()

    def values(self):
        return self.table.values()

    def items(self):
        return self.table.items()


class Entry:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.hash = hash(key)

    def __eq__(self, other: Entry) -> bool:
        if self.hash != other.hash:
            return False
        return self.key == other.key

    def __hash__(self) -> int:
        return self.hash


class SeparateChaining(MutableMapping):
    def __init__(
        self,
        capacity: int,
        max_load_factor: float,
    ):
        if capacity < 0:
            raise ValueError("Capacity needs to be greater than 0")
        if max_load_factor <= 0 or max_load_factor >= math.inf:
            raise ValueError(
                "Max Load Factor needs to be greater than 0 but a real number"
            )
        self.max_load_factor = max_load_factor
        self.capacity = max(capacity, DEFAULT_CAPACITY_SEPARATE_CHAINING)
        self.threshold = int(self.capacity * self.max_load_factor)
        self.table: list[Optional[deque[Entry]]] = [None] * self.capacity
        self.size = 0

    def clear(self):
        self.table.clear()
        self.size = 0

    def __getitem__(self, key):
        if key is None:
            raise KeyError("Key must not be None")

        bucket_index = self.__normalize_index(hash(key))
        entry = self.__bucket_seek_entry(bucket_index, key)

        if entry is None:
            raise KeyError(f"No such key found: {key}")

        return entry.value

    def __contains__(self, key) -> bool:
        bucket_index = self.__normalize_index(hash(key))
        return self.__bucket_seek_entry(bucket_index, key) is not None

    def __setitem__(self, key, value):
        if key is None:
            raise ValueError("Key must not be None")

        entry = Entry(key, value)
        bucket_index = self.__normalize_index(hash(entry))
        return self.__bucket_insert_entry(bucket_index, entry)

    def __delitem__(self, key):
        if key is None:
            raise KeyError("Key must not be None")
        bucket_index = self.__normalize_index(hash(key))
        return self.__bucket_remove_entry(bucket_index, key)

    def __iter__(self) -> Iterator:
        return self.keys()

    def keys(self) -> Iterator:
        return (entry.key for entry in self.entries())

    def values(self) -> Iterator:
        return (entry.value for entry in self.entries())

    def items(self) -> Iterator:
        return ((entry.key, entry.value) for entry in self.entries())

    def entries(self) -> Iterator:
        for bucket in self.table:
            if bucket is None:
                continue

            for entry in bucket:
                yield entry

    def __len__(self) -> int:
        return self.size

    def __normalize_index(self, key_hash: int) -> int:
        return abs(key_hash) % self.capacity

    def __bucket_remove_entry(self, index, key) -> Optional:
        entry = self.__bucket_seek_entry(index, key)
        if entry is not None:
            bucket: deque = self.table[index]
            bucket.remove(entry)
            self.size -= 1
            return entry.value

        return None

    def __bucket_insert_entry(self, index, entry) -> Optional:
        bucket = self.table[index]
        if bucket is None:
            self.table[index] = bucket = deque()

        existing_entry = self.__bucket_seek_entry(index, entry.key)
        if existing_entry is None:
            bucket.append(entry)
            self.size += 1
            if self.size >= self.threshold:
                self.__resize_table()
            return None
        else:
            old_val = existing_entry.value
            existing_entry.value = entry.value
            return old_val

    def __bucket_seek_entry(self, index, key) -> Optional[Entry]:
        if key is None:
            raise KeyError("Key must not be None")

        bucket = self.table[index]
        if not bucket:
            return None

        for entry in bucket:
            if entry.key == key:
                return entry

        return None

    def __resize_table(self):
        self.capacity *= 2
        self.threshold = int(self.capacity * self.max_load_factor)
        new_table = [None] * self.capacity

        for entry in self.entries():
            bucket_index = self.__normalize_index(hash(entry.key))
            bucket = new_table[bucket_index]
            if bucket is None:
                bucket = deque()
            bucket.append(entry)

        self.table = new_table


TOMBSTONE = object()


class OpenAddressing(MutableMapping):
    modification_count = 0
    used_buckets = 0
    key_count = 0
    contains_flag = False

    def __init__(self, capacity: int, load_factor: float):
        if capacity < 0:
            raise ValueError("Capacity needs to be greater than 0")
        if load_factor <= 0 or load_factor >= math.inf:
            raise ValueError("Load Factor needs to be greater than 0 but a real number")

        self.load_factor = load_factor
        self.capacity = max(DEFAULT_CAPACITY_OPEN_ADDRESSING, next_2_power(capacity))
        self.threshold = int(self.capacity * self.load_factor)

        self.key_table = [None] * self.capacity
        self.value_table = [None] * self.capacity

    def clear(self):
        for i in range(self.capacity):
            self.key_table[i] = None
            self.value_table[i] = None
        self.key_count = self.used_buckets = 0
        self.modification_count += 1

    def __getitem__(self, key):
        if key is None:
            raise ValueError("Key must not be None")

        item_hash = self.__normalize_index(hash(key))
        i, j, x = item_hash, -1, 1

        while True:
            if self.key_table[i] is TOMBSTONE:
                if j == -1:
                    j = i
            elif self.key_table[i] is not None:
                if self.key_table[i] == key:
                    self.contains_flag = True

                    if j != -1:
                        self.key_table[j] = self.key_table[i]
                        self.value_table[j] = self.value_table[i]

                        self.key_table[i] = TOMBSTONE
                        self.value_table[i] = None

                        return self.value_table[j]
                    else:
                        return self.value_table[i]
            else:
                self.contains_flag = False
                return None

            x += 1
            i = self.__normalize_index(item_hash + self.P(x))

    def __setitem__(self, key, value):
        if key is None:
            raise ValueError("Key must not be None")

        if self.used_buckets >= self.threshold:
            self.__resize_table()

        item_hash = self.__normalize_index(hash(key))
        i, j, x = item_hash, -1, 1

        while True:
            if self.key_table[i] is TOMBSTONE:
                if j == -1:
                    j = i
            elif self.key_table[i] is not None:
                if self.key_table[i] == key:
                    old_value = self.value_table[i]
                    if j == -1:
                        self.value_table[i] = value
                    else:
                        self.key_table[i] = TOMBSTONE
                        self.value_table[i] = None
                        self.key_table[j] = key
                        self.value_table[j] = value

                    self.modification_count += 1
                    return old_value
            else:
                if j == -1:
                    self.used_buckets += 1
                    self.key_count += 1
                    self.key_table[i] = key
                    self.value_table[i] = value
                else:
                    self.key_count += 1
                    self.key_table[i] = key
                    self.value_table[i] = value

                self.modification_count += 1
                return None

            x += 1
            i = self.__normalize_index(item_hash + self.P(x))

    def __delitem__(self, key):
        if key is None:
            raise ValueError("Key must not be None")

        item_hash = self.__normalize_index(hash(key))
        i, x = item_hash, 1

        while True:
            if self.key_table[i] is None:
                return None

            if self.key_table[i] == key:
                self.key_count -= 1
                self.modification_count += 1
                old_value = self.value_table[i]
                self.key_table[i] = TOMBSTONE
                self.value_table[i] = None
                return old_value

            x += 1
            i = self.__normalize_index(item_hash + self.P(x))

    def __contains__(self, key):
        self.__getitem__(key)
        return self.contains_flag

    def __len__(self):
        return self.key_count

    def __iter__(self):
        return self.keys()

    def keys(self):
        return (
            key for key in self.key_table if key is not None and key is not TOMBSTONE
        )

    def values(self):
        return (value for value in self.value_table if value is not None)

    def items(self):
        return (
            (key, self.value_table[i])
            for i, key in enumerate(self.key_table)
            if key is not None and key is not TOMBSTONE
        )

    @classmethod
    def P(cls, x: int) -> int:
        return (x * x + x) >> 1

    def __normalize_index(self, key_hash: int) -> int:
        return abs(key_hash) % self.capacity

    def __resize_table(self):
        self.capacity *= 2
        self.threshold = int(self.capacity * self.load_factor)

        self.key_table, old_key_table = [None] * self.capacity, self.key_table
        self.value_table, old_value_table = [None] * self.capacity, self.value_table

        self.key_count = self.used_buckets = 0

        for i in range(old_key_table):
            key = old_key_table[i]
            if key is None or key is TOMBSTONE:
                continue
            value = old_value_table[i]

            self[key] = value
            old_key_table[i] = None
            old_key_table[i] = None


def next_2_power(num: int) -> int:
    return math.pow(2, num.bit_length())
