from __future__ import annotations
from typing import Optional


class Node:
    bf = 0
    height = 0
    left: Optional[Node] = None
    right: Optional[Node] = None

    def __init__(self, value):
        self.value = value


class AVLTree:
    root: Optional[Node] = None
    node_count = 0

    def height(self) -> int:
        if self.root is not None:
            return self.root.height

        return 0

    def __len__(self) -> int:
        return self.node_count

    def __contains__(self, value) -> bool:
        return self.__contains(self.root, value)

    def append(self, value) -> bool:
        if value is None or value in self:
            return False

        self.root = self.__append(self.root, value)
        self.node_count += 1
        return True

    def remove(self, value) -> bool:
        if value is None or value not in self:
            return False

        self.root = self.__remove(self.root, value)
        self.node_count -= 1
        return True

    def __contains(self, node: Optional[Node], value) -> bool:
        if node is None:
            return False

        if value > node.value:
            return self.__contains(node.right, value)
        if value < node.value:
            return self.__contains(node.left, value)

        return True

    def __append(self, node: Optional[Node], value) -> Node:
        if node is None:
            return Node(value)

        if value > node.value:
            node.right = self.__append(node.right, value)
        elif value < node.value:
            node.left = self.__append(node.left, value)

        self.__update(node)

        return self.__balance(node)

    def __remove(self, node: Optional[Node], value) -> Node:
        if node is None:
            return None

        if value > node.value:
            node.right = self.__remove(node.right, value)
        elif value < node.value:
            node.left = self.__remove(node.left, value)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                if node.left.height > node.right.height:
                    successor_value = self.__find_max(node.left)
                    node.value = successor_value
                    node.left = self.__remove(node.left, successor_value)
                else:
                    successor_value = self.__find_min(node.right)
                    node.value = successor_value
                    node.right = self.__remove(node.right, successor_value)

        self.__update(node)
        return self.__balance(node)

    def __update(self, node: Node):
        left_height = -1 if node.left is None else node.left.height
        right_height = -1 if node.right is None else node.right.height

        node.height = 1 + max(left_height, right_height)

        node.bf = right_height - left_height

    def __balance(self, node: Node) -> Node:
        if node.bf == -2:
            if node.left.bf <= 0:
                return self.__left_left_case(node)
            else:
                return self.__left_right_case(node)
        elif node.bf == 2:
            if node.right.bf >= 0:
                return self.__right_right_case(node)
            else:
                return self.__right_left_case(node)

        return node

    def __left_left_case(self, node: Node) -> Node:
        return self.__right_rotate(node)

    def __left_right_case(self, node: Node) -> Node:
        node.left = self.__left_rotate(node.left)
        return self.__left_left_case(node)

    def __right_right_case(self, node: Node) -> Node:
        return self.__left_rotate(node)

    def __right_left_case(self, node: Node) -> Node:
        node.right = self.__right_rotate(node.right)
        return self.__right_right_case(node)

    def __left_rotate(self, node: Node) -> Node:
        new_parent = node.right
        node.right = new_parent.left
        new_parent.left = node

        self.__update(node)
        self.__update(new_parent)

        return new_parent

    def __right_rotate(self, node: Node) -> Node:
        new_parent = node.left
        node.left = new_parent.right
        new_parent.right = node

        self.__update(node)
        self.__update(new_parent)

        return new_parent

    def __find_max(self, node: Node):
        while node.right is not None:
            node = node.right

        return node.value

    def __find_min(self, node: Node):
        while node.left is not None:
            node = node.left

        return node.value
