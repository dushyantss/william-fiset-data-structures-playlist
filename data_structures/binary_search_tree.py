from typing import Optional


class Node:
    def __init__(self, value, /, *, left: Node = None, right: Node = None):
        self.value = value
        self.left = left
        self.right = right


class BinarySearchTree:
    def __init__(self):
        self.root: Optional[Node] = None
        self.node_count = 0

    def __len__(self):
        return self.node_count

    def add(self, value) -> bool:
        if self.contains(value):
            return False

        self.root = self.__do_add(self.root, value)
        self.node_count += 1
        return True

    def remove(self, value) -> bool:
        if self.contains(value):
            self.root = self.__do_remove(self.root, value)
            self.node_count -= 1
            return True

        return False

    def contains(self, value) -> bool:
        return self.__do_contains(self.root, value)

    def __do_add(self, node: Optional[Node], value) -> Node:
        if not node:
            node = Node(value)
        elif value < node.value:
            node.left = self.__do_add(node.left, value)
        else:
            node.right = self.__do_add(node.right, value)

        return node

    def __do_remove(self, node: Optional[Node], value) -> Optional[Node]:
        if node is None:
            return None

        if value < node.value:
            node.left = self.__do_remove(node.left, value)
        elif value > node.value:
            node.right = self.__do_remove(node.right, value)
        elif node.left is None:
            node = node.right
        elif node.right is None:
            node = node.left
        else:
            successor = self.__dig_left(node.right)
            node.value = successor.value
            node.right = self.__do_remove(node.right, successor.value)

        return node

    def __dig_left(self, node: Node) -> Node:
        while node.left is not None:
            node = node.left

        return node

    def __do_contains(self, node: Optional[Node], value) -> bool:
        if node is None:
            return False

        if value < node.value:
            return self.__do_contains(node.left, value)
        elif value > node.value:
            return self.__do_contains(node.right, value)
        else:
            return True
