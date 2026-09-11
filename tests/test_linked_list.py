"""
Unit Tests for Singly Linked List (ItemLinkedList).
Tests insertion, deletion, searching, sorting, and edge cases.
"""

import unittest
from src.models import ItemRecord, ItemStatus, ItemType, Category
from src.linked_list import ItemLinkedList, ListNode


class TestItemLinkedList(unittest.TestCase):
    def setUp(self):
        self.ll = ItemLinkedList()
        self.item1 = ItemRecord(
            item_id=1,
            title="Dell XPS 13",
            category=Category.ELECTRONICS.value,
            description="Silver laptop with charger",
            item_type=ItemType.FOUND.value,
            location="Room 201",
            reporter_name="Alice",
            reporter_contact="alice@test.com",
            reward_or_value=1200.0
        )
        self.item2 = ItemRecord(
            item_id=2,
            title="House Keys with Blue Lanyard",
            category=Category.KEYS_WALLETS.value,
            description="Set of 3 brass keys",
            item_type=ItemType.FOUND.value,
            location="Gym Lobby",
            reporter_name="Bob",
            reporter_contact="bob@test.com",
            reward_or_value=20.0
        )
        self.item3 = ItemRecord(
            item_id=3,
            title="Calculus Textbook",
            category=Category.OTHERS.value,
            description="Stewart Calculus 8th Edition",
            item_type=ItemType.LOST.value,
            location="Math Hall",
            reporter_name="Charlie",
            reporter_contact="charlie@test.com",
            reward_or_value=85.0
        )

    def test_initial_state(self):
        self.assertTrue(self.ll.is_empty())
        self.assertEqual(len(self.ll), 0)
        self.assertIsNone(self.ll.head)
        self.assertIsNone(self.ll.tail)

    def test_insert_head(self):
        self.ll.insert_head(self.item1)
        self.assertFalse(self.ll.is_empty())
        self.assertEqual(len(self.ll), 1)
        self.assertEqual(self.ll.head.data.item_id, 1)
        self.assertEqual(self.ll.tail.data.item_id, 1)

        self.ll.insert_head(self.item2)
        self.assertEqual(len(self.ll), 2)
        self.assertEqual(self.ll.head.data.item_id, 2)
        self.assertEqual(self.ll.tail.data.item_id, 1)

    def test_insert_tail(self):
        self.ll.insert_tail(self.item1)
        self.ll.insert_tail(self.item2)
        self.assertEqual(len(self.ll), 2)
        self.assertEqual(self.ll.head.data.item_id, 1)
        self.assertEqual(self.ll.tail.data.item_id, 2)

    def test_insert_sorted(self):
        # Insert out of order
        self.ll.insert_sorted(self.item2, key="item_id")  # ID 2
        self.ll.insert_sorted(self.item3, key="item_id")  # ID 3
        self.ll.insert_sorted(self.item1, key="item_id")  # ID 1

        items = self.ll.to_list()
        ids = [item.item_id for item in items]
        self.assertEqual(ids, [1, 2, 3])

    def test_delete_by_id(self):
        self.ll.insert_tail(self.item1)
        self.ll.insert_tail(self.item2)
        self.ll.insert_tail(self.item3)

        # Delete middle node (ID 2)
        deleted = self.ll.delete_by_id(2)
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted.item_id, 2)
        self.assertEqual(len(self.ll), 2)

        # Verify remaining items
        ids = [item.item_id for item in self.ll.to_list()]
        self.assertEqual(ids, [1, 3])

        # Delete head node (ID 1)
        deleted_head = self.ll.delete_by_id(1)
        self.assertEqual(deleted_head.item_id, 1)
        self.assertEqual(self.ll.head.data.item_id, 3)
        self.assertEqual(self.ll.tail.data.item_id, 3)

        # Delete remaining single node (ID 3)
        deleted_tail = self.ll.delete_by_id(3)
        self.assertEqual(deleted_tail.item_id, 3)
        self.assertTrue(self.ll.is_empty())
        self.assertIsNone(self.ll.head)
        self.assertIsNone(self.ll.tail)

        # Delete non-existent
        self.assertIsNone(self.ll.delete_by_id(999))

    def test_search_by_id(self):
        self.ll.insert_tail(self.item1)
        self.ll.insert_tail(self.item2)

        res = self.ll.search_by_id(2)
        self.assertIsNotNone(res)
        self.assertEqual(res.title, "House Keys with Blue Lanyard")

        self.assertIsNone(self.ll.search_by_id(99))

    def test_search_by_keyword(self):
        self.ll.insert_tail(self.item1)
        self.ll.insert_tail(self.item2)
        self.ll.insert_tail(self.item3)

        # Search by category keyword
        res1 = self.ll.search_by_keyword("Electronics")
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].item_id, 1)

        # Search by description keyword
        res2 = self.ll.search_by_keyword("keys")
        self.assertEqual(len(res2), 1)
        self.assertEqual(res2[0].item_id, 2)

    def test_update_status(self):
        self.ll.insert_tail(self.item1)
        self.assertTrue(self.ll.update_status(1, ItemStatus.CLAIM_PENDING.value))
        self.assertEqual(self.ll.head.data.status, ItemStatus.CLAIM_PENDING.value)
        self.assertFalse(self.ll.update_status(999, "NONE"))


if __name__ == "__main__":
    unittest.main()
