"""
Unit Tests for Linked Stack (LIFO) and Linked Queue (FIFO).
Verifies pointer manipulation, order enforcement, and boundary conditions.
"""

import unittest
from src.stack import LinkedStack
from src.queue import LinkedQueue
from src.models import ClaimRecord, AuditAction


class TestLinkedStackAndQueue(unittest.TestCase):
    def test_linked_stack_lifo_order(self):
        stack: LinkedStack[str] = LinkedStack()
        self.assertTrue(stack.is_empty())
        self.assertEqual(len(stack), 0)
        self.assertIsNone(stack.pop())
        self.assertIsNone(stack.peek())

        # Push items
        stack.push("Action_A")
        stack.push("Action_B")
        stack.push("Action_C")

        self.assertEqual(len(stack), 3)
        self.assertEqual(stack.peek(), "Action_C")

        # Pop items and verify LIFO order
        self.assertEqual(stack.pop(), "Action_C")
        self.assertEqual(stack.pop(), "Action_B")
        self.assertEqual(stack.pop(), "Action_A")
        self.assertTrue(stack.is_empty())
        self.assertEqual(len(stack), 0)

    def test_linked_queue_fifo_order(self):
        queue: LinkedQueue[str] = LinkedQueue()
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(queue), 0)
        self.assertIsNone(queue.dequeue())
        self.assertIsNone(queue.peek_front())
        self.assertIsNone(queue.peek_rear())

        # Enqueue items
        queue.enqueue("Claim_1")
        queue.enqueue("Claim_2")
        queue.enqueue("Claim_3")

        self.assertEqual(len(queue), 3)
        self.assertEqual(queue.peek_front(), "Claim_1")
        self.assertEqual(queue.peek_rear(), "Claim_3")

        # Dequeue items and verify FIFO order
        self.assertEqual(queue.dequeue(), "Claim_1")
        self.assertEqual(queue.dequeue(), "Claim_2")
        self.assertEqual(queue.dequeue(), "Claim_3")
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(queue), 0)

    def test_audit_action_stack(self):
        stack: LinkedStack[AuditAction] = LinkedStack()
        act1 = AuditAction(action_type="INSERT", item_id=101)
        act2 = AuditAction(action_type="STATUS_CHANGE", item_id=101)

        stack.push(act1)
        stack.push(act2)

        popped = stack.pop()
        self.assertEqual(popped.action_type, "STATUS_CHANGE")
        self.assertEqual(popped.item_id, 101)


if __name__ == "__main__":
    unittest.main()
