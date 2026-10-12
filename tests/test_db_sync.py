"""
Integration tests for LostAndFoundService and Database Synchronization.
Tests CRUD, FIFO Claim Verification Pipeline, and LIFO Action Undo.
"""

import unittest
import os
import shutil
from src.service import LostAndFoundService
from src.models import ItemStatus, ClaimStatus, Category, ItemType


class TestServiceIntegration(unittest.TestCase):
    def setUp(self):
        # Initialize service with SQLite fallback for deterministic testing
        self.service = LostAndFoundService(prefer_mysql=False)
        # Drain any existing claims in queue for clean FIFO test state
        while not self.service.claim_queue.is_empty():
            self.service.claim_queue.dequeue()

    def test_report_item_and_traversal(self):
        initial_count = len(self.service.get_all_items())

        new_item = {
            "title": "Titan Chronograph Watch",
            "category": Category.OTHERS.value,
            "description": "Silver mesh strap watch found near football field",
            "item_type": ItemType.FOUND.value,
            "location": "Football Ground Pavilion",
            "reporter_name": "Coach Rao",
            "reporter_contact": "coach.rao@campus.edu",
            "reward_or_value": 110.0,
            "status": ItemStatus.IN_CUSTODY.value
        }

        created = self.service.report_item(new_item)
        self.assertGreater(created.item_id, 0)
        self.assertEqual(len(self.service.get_all_items()), initial_count + 1)

        # Search verification
        found = self.service.search_items("Titan")
        self.assertTrue(any(i.item_id == created.item_id for i in found))

    def test_submit_and_process_claim_fifo(self):
        # Report a sample item
        item = self.service.report_item({
            "title": "Kindle Paperwhite",
            "category": Category.ELECTRONICS.value,
            "description": "Green leather cover",
            "item_type": ItemType.FOUND.value,
            "location": "Reading Hall",
            "reporter_name": "Librarian",
            "reporter_contact": "lib@campus.edu",
            "reward_or_value": 130.0,
            "status": ItemStatus.IN_CUSTODY.value
        })

        # Submit claim (Enters FIFO Queue)
        claim = self.service.submit_claim(
            item_id=item.item_id,
            claimant_name="Nitin Kumar",
            claimant_contact="nitin.k@campus.edu",
            proof_description="Password is 6 digits and contains sticker on back"
        )
        self.assertEqual(claim.item_id, item.item_id)
        self.assertEqual(claim.claim_status, ClaimStatus.PENDING.value)

        # Verify claim is in queue
        pending = self.service.get_pending_claims()
        self.assertTrue(any(c.claim_id == claim.claim_id for c in pending))

        # Process claim with scoring formula
        formula = "(desc_match * 0.60) + (serial_match * 0.40)"
        variables = {"desc_match": 90.0, "serial_match": 85.0}  # Expected: 54 + 34 = 88.0%

        processed_claim, score, decision = self.service.process_next_claim(formula, variables, approve_threshold=70.0)
        self.assertIsNotNone(processed_claim)
        self.assertEqual(processed_claim.claim_status, ClaimStatus.APPROVED.value)
        self.assertGreaterEqual(score, 70.0)

        # Verify item status changed to VERIFIED_RETURNED
        updated_item = self.service.find_item_by_id(item.item_id)
        self.assertEqual(updated_item.status, ItemStatus.VERIFIED_RETURNED.value)

    def test_undo_stack_functionality(self):
        item = self.service.report_item({
            "title": "Scientific Calculator FX-991EX",
            "category": Category.ELECTRONICS.value,
            "description": "Black Casio calculator",
            "item_type": ItemType.LOST.value,
            "location": "Exam Hall 1",
            "reporter_name": "Student A",
            "reporter_contact": "sa@campus.edu",
            "reward_or_value": 25.0,
            "status": ItemStatus.REPORTED.value
        })

        # Change status
        self.service.update_item_status(item.item_id, ItemStatus.IN_CUSTODY.value)
        curr = self.service.find_item_by_id(item.item_id)
        self.assertEqual(curr.status, ItemStatus.IN_CUSTODY.value)

        # Undo status change via LIFO stack
        undo_msg = self.service.undo_last_action()
        self.assertIn("Undid STATUS_CHANGE", undo_msg)

        reverted = self.service.find_item_by_id(item.item_id)
        self.assertEqual(reverted.status, ItemStatus.REPORTED.value)


if __name__ == "__main__":
    unittest.main()
