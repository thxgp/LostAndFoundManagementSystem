"""
Pure Node-based Linked Stack (LIFO) for Action Undo & Audit Logging.
Satisfies syllabus requirement: Implementing stack and queue using linked list.
"""

from typing import Optional, List, Generic, TypeVar

T = TypeVar("T")


class StackNode(Generic[T]):
    """A single node in the singly linked stack."""
    def __init__(self, data: T):
        self.data: T = data
        self.next: Optional["StackNode[T]"] = None

    def __repr__(self) -> str:
        return f"StackNode({self.data})"


class LinkedStack(Generic[T]):
    """
    Linked Stack (LIFO: Last-In, First-Out) with top pointer.
    Provides O(1) push, pop, and peek without size limitations.
    """
    def __init__(self):
        self.top: Optional[StackNode[T]] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        """Check if stack is empty. O(1)"""
        return self.top is None

    def push(self, item: T) -> None:
        """
        Push an item onto the top of the stack.
        Time Complexity: O(1)
        """
        new_node = StackNode(item)
        new_node.next = self.top
        self.top = new_node
        self._size += 1

    def pop(self) -> Optional[T]:
        """
        Pop and return the top item from the stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        popped_node = self.top
        self.top = self.top.next
        self._size -= 1
        return popped_node.data

    def peek(self) -> Optional[T]:
        """
        Return the top item without removing it.
        Time Complexity: O(1)
        """
        return self.top.data if self.top is not None else None

    def to_list(self) -> List[T]:
        """
        Traverse the stack from top to bottom as a list.
        Time Complexity: O(N)
        """
        elements: List[T] = []
        current = self.top
        while current is not None:
            elements.append(current.data)
            current = current.next
        return elements

    def clear(self) -> None:
        """
        Reset stack.
        Time Complexity: O(1)
        """
        self.top = None
        self._size = 0
