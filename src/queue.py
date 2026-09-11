"""
Pure Node-based Linked Queue (FIFO) for Lost & Found Verification Requests.
Satisfies syllabus requirement: Implementing stack and queue using linked list.
"""

from typing import Optional, List, Generic, TypeVar

T = TypeVar("T")


class QueueNode(Generic[T]):
    """A node in the singly linked queue."""
    def __init__(self, data: T):
        self.data: T = data
        self.next: Optional["QueueNode[T]"] = None

    def __repr__(self) -> str:
        return f"QueueNode({self.data})"


class LinkedQueue(Generic[T]):
    """
    Linked Queue (FIFO: First-In, First-Out) with front and rear pointers.
    Maintains O(1) enqueue and dequeue operations without array reallocation.
    """
    def __init__(self):
        self.front: Optional[QueueNode[T]] = None
        self.rear: Optional[QueueNode[T]] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        """Check if queue is empty. O(1)"""
        return self.front is None

    def enqueue(self, item: T) -> None:
        """
        Add an element to the rear of the queue.
        Time Complexity: O(1)
        """
        new_node = QueueNode(item)
        if self.is_empty():
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self) -> Optional[T]:
        """
        Remove and return the element at the front of the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None

        removed_node = self.front
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return removed_node.data

    def peek_front(self) -> Optional[T]:
        """
        Return the element at the front without removing it.
        Time Complexity: O(1)
        """
        return self.front.data if self.front is not None else None

    def peek_rear(self) -> Optional[T]:
        """
        Return the element at the rear without removing it.
        Time Complexity: O(1)
        """
        return self.rear.data if self.rear is not None else None

    def to_list(self) -> List[T]:
        """
        Traverse queue from front to rear as a list.
        Time Complexity: O(N)
        """
        elements: List[T] = []
        current = self.front
        while current is not None:
            elements.append(current.data)
            current = current.next
        return elements

    def clear(self) -> None:
        """
        Reset queue.
        Time Complexity: O(1)
        """
        self.front = None
        self.rear = None
        self._size = 0
