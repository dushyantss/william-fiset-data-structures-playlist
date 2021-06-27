from __future__ import annotations
from collections import deque
from collections.abc import MutableMapping
import math
from typing import Iterator, Optional


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


DEFAULT_CAPACITY = 3
DEFAULT_LOAD_FACTOR = 0.75


class HashTable(MutableMapping):
    def __init__(
        self,
        capacity: int = DEFAULT_CAPACITY,
        max_load_factor: float = DEFAULT_LOAD_FACTOR,
    ):
        if capacity < 0:
            raise ValueError("Capacity needs to be greater than 0")
        if max_load_factor <= 0 or max_load_factor >= math.inf:
            raise ValueError(
                "Max Load Factor needs to be greater than 0 but a real number"
            )
        self.max_load_factor = max_load_factor
        self.capacity = max(capacity, DEFAULT_CAPACITY)
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
