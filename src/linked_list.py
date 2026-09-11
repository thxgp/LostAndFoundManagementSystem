"""
Pure Node-based Singly Linked List Implementation for Lost and Found Item Records.
Satisfies syllabus requirement: Linear Data Structures Implementation (Linked List Storage).
"""

from typing import Optional, List, Callable, Any
from src.models import ItemRecord


class ListNode:
    """A single node in the Singly Linked List."""
    def __init__(self, data: ItemRecord):
        self.data: ItemRecord = data
        self.next: Optional["ListNode"] = None

    def __repr__(self) -> str:
        return f"ListNode(ID={self.data.item_id}, Title='{self.data.title}')"


class ItemLinkedList:
    """
    Singly Linked List with head and tail pointers.
    Provides fundamental linear data structure operations for item records.
    """
    def __init__(self):
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.head is None

    def insert_head(self, item: ItemRecord) -> None:
        """
        Insert an item record at the beginning (head) of the linked list.
        Time Complexity: O(1)
        """
        new_node = ListNode(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self._size += 1

    def insert_tail(self, item: ItemRecord) -> None:
        """
        Insert an item record at the end (tail) of the linked list.
        Time Complexity: O(1) with tail pointer
        """
        new_node = ListNode(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def insert_sorted(self, item: ItemRecord, key: str = "item_id") -> None:
        """
        Insert an item record in ascending sorted order by a specified key.
        Supported keys: 'item_id', 'reward_or_value', 'reported_date'
        Time Complexity: O(N)
        """
        new_node = ListNode(item)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
            self._size += 1
            return

        def get_val(obj: ItemRecord):
            return getattr(obj, key, obj.item_id)

        # If it belongs at the head
        if get_val(item) <= get_val(self.head.data):
            new_node.next = self.head
            self.head = new_node
            self._size += 1
            return

        # Traverse to find the correct position
        current = self.head
        while current.next is not None and get_val(current.next.data) < get_val(item):
            current = current.next

        new_node.next = current.next
        current.next = new_node
        if new_node.next is None:
            self.tail = new_node
        self._size += 1

    def delete_by_id(self, item_id: int) -> Optional[ItemRecord]:
        """
        Delete an item record matching item_id.
        Time Complexity: O(N)
        """
        if self.is_empty():
            return None

        # If target is at head
        if self.head.data.item_id == item_id:
            deleted_item = self.head.data
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self._size -= 1
            return deleted_item

        current = self.head
        while current.next is not None and current.next.data.item_id != item_id:
            current = current.next

        if current.next is not None:
            deleted_item = current.next.data
            current.next = current.next.next
            if current.next is None:
                self.tail = current
            self._size -= 1
            return deleted_item

        return None

    def search_by_id(self, item_id: int) -> Optional[ItemRecord]:
        """
        Linear search by unique item_id.
        Time Complexity: O(N)
        """
        current = self.head
        while current is not None:
            if current.data.item_id == item_id:
                return current.data
            current = current.next
        return None

    def search_by_keyword(self, keyword: str) -> List[ItemRecord]:
        """
        Search for items whose title, description, category, or location matches keyword.
        Time Complexity: O(N)
        """
        keyword_lower = keyword.strip().lower()
        results: List[ItemRecord] = []
        current = self.head
        while current is not None:
            item = current.data
            if (keyword_lower in item.title.lower() or
                keyword_lower in item.description.lower() or
                keyword_lower in item.category.lower() or
                keyword_lower in item.location.lower()):
                results.append(item)
            current = current.next
        return results

    def filter_by_predicate(self, predicate: Callable[[ItemRecord], bool]) -> List[ItemRecord]:
        """
        Filter items matching a given custom condition predicate.
        Time Complexity: O(N)
        """
        results: List[ItemRecord] = []
        current = self.head
        while current is not None:
            if predicate(current.data):
                results.append(current.data)
            current = current.next
        return results

    def update_item(self, item_id: int, updated_item: ItemRecord) -> bool:
        """
        Update the data of an existing item record.
        Time Complexity: O(N)
        """
        current = self.head
        while current is not None:
            if current.data.item_id == item_id:
                current.data = updated_item
                return True
            current = current.next
        return False

    def update_status(self, item_id: int, new_status: str) -> bool:
        """
        Update status for a specific item.
        Time Complexity: O(N)
        """
        current = self.head
        while current is not None:
            if current.data.item_id == item_id:
                current.data.status = new_status
                return True
            current = current.next
        return False

    def to_list(self) -> List[ItemRecord]:
        """
        Convert linked list elements into a standard list.
        Time Complexity: O(N)
        """
        items: List[ItemRecord] = []
        current = self.head
        while current is not None:
            items.append(current.data)
            current = current.next
        return items

    def clear(self) -> None:
        """
        Reset the linked list to an empty state.
        Time Complexity: O(1)
        """
        self.head = None
        self.tail = None
        self._size = 0
