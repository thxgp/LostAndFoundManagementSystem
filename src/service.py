"""
Central Service Coordinator for Lost and Found Management System.
Bridges MySQL Persistence with Linear Data Structures:
- ItemLinkedList (Node-based storage)
- LinkedQueue (FIFO Claim Verification Pipeline)
- LinkedStack (LIFO Multi-Level Action Undo & Audit)
- ExpressionParser (Stack-based confidence & fee formulas)
"""

import os
import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from src.models import ItemRecord, ClaimRecord, AuditAction, ItemStatus, ClaimStatus, ItemType
from src.linked_list import ItemLinkedList
from src.queue import LinkedQueue
from src.stack import LinkedStack
from src.expression_parser import ExpressionParser
from database.db_manager import DatabaseManager
from config.db_config import SEED_DATA_PATH


class LostAndFoundService:
    """
    Coordinates linear data structures with persistent database storage.
    """
    def __init__(self, prefer_mysql: bool = True):
        self.db = DatabaseManager(prefer_mysql=prefer_mysql)
        self.item_list = ItemLinkedList()
        self.claim_queue: LinkedQueue[ClaimRecord] = LinkedQueue()
        self.undo_stack: LinkedStack[AuditAction] = LinkedStack()
        self._hydrate_data()

    def _hydrate_data(self) -> None:
        """Hydrate Linked List and Queue from database or seed file."""
        db_items = self.db.fetch_all_items()

        # If DB is empty, load seed data
        if not db_items and os.path.exists(SEED_DATA_PATH):
            with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
                seed_data = json.load(f)
                for item_dict in seed_data:
                    record = ItemRecord.from_dict(item_dict)
                    item_id = self.db.insert_item(record)
                    record.item_id = item_id
                    db_items.append(record)

        # Hydrate Linked List
        for item in db_items:
            self.item_list.insert_tail(item)

        # Hydrate Pending Claims into Queue
        claims = self.db.fetch_all_claims()
        for claim in claims:
            if claim.claim_status == ClaimStatus.PENDING.value:
                self.claim_queue.enqueue(claim)

    # --- Item Management Operations ---

    def report_item(self, item_dict: Dict[str, Any]) -> ItemRecord:
        """
        Report a new Lost or Found item.
        1. Persists to Database
        2. Inserts into ItemLinkedList (O(1) tail insertion)
        3. Pushes snapshot to AuditUndoStack for LIFO history
        """
        record = ItemRecord.from_dict(item_dict)
        record.validate()

        # Insert into DB to get primary key
        assigned_id = self.db.insert_item(record)
        record.item_id = assigned_id

        # Insert into Linked List
        self.item_list.insert_tail(record)

        # Push to Undo Stack
        action = AuditAction(
            action_type="INSERT",
            item_id=record.item_id,
            snapshot_before=None,
            snapshot_after=record.to_dict()
        )
        action_id = self.db.insert_audit(action)
        action.action_id = action_id
        self.undo_stack.push(action)

        return record

    def update_item_status(self, item_id: int, new_status: str) -> bool:
        """Update status of an item with snapshot recording."""
        item = self.item_list.search_by_id(item_id)
        if not item:
            return False

        snapshot_before = item.to_dict()
        item.status = new_status
        item.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update in DB
        self.db.update_item(item)

        # Push to Undo Stack
        action = AuditAction(
            action_type="STATUS_CHANGE",
            item_id=item_id,
            snapshot_before=snapshot_before,
            snapshot_after=item.to_dict()
        )
        action_id = self.db.insert_audit(action)
        action.action_id = action_id
        self.undo_stack.push(action)

        return True

    def delete_item(self, item_id: int) -> Optional[ItemRecord]:
        """
        Delete an item from both Linked List and Database.
        Pushes action to Undo Stack.
        """
        deleted_record = self.item_list.delete_by_id(item_id)
        if not deleted_record:
            return None

        self.db.delete_item(item_id)

        action = AuditAction(
            action_type="DELETE",
            item_id=item_id,
            snapshot_before=deleted_record.to_dict(),
            snapshot_after=None
        )
        action_id = self.db.insert_audit(action)
        action.action_id = action_id
        self.undo_stack.push(action)

        return deleted_record

    def get_all_items(self) -> List[ItemRecord]:
        """Traverse Linked List to return all items. Time Complexity: O(N)"""
        return self.item_list.to_list()

    def search_items(self, query: str) -> List[ItemRecord]:
        """Search items in the Linked List matching keyword."""
        return self.item_list.search_by_keyword(query)

    def find_item_by_id(self, item_id: int) -> Optional[ItemRecord]:
        """Find a specific item by ID via Linked List traversal."""
        return self.item_list.search_by_id(item_id)

    # --- FIFO Claim Processing Queue Operations ---

    def submit_claim(self, item_id: int, claimant_name: str, claimant_contact: str, proof_description: str) -> ClaimRecord:
        """
        Submit a verification claim for a found item.
        Enqueues into FIFO LinkedQueue and persists in DB.
        """
        item = self.item_list.search_by_id(item_id)
        if not item:
            raise ValueError(f"Item with ID {item_id} does not exist.")

        claim = ClaimRecord(
            claim_id=0,
            item_id=item_id,
            claimant_name=claimant_name,
            claimant_contact=claimant_contact,
            proof_description=proof_description,
            claim_status=ClaimStatus.PENDING.value
        )
        claim.validate()

        # Persist claim
        claim_id = self.db.insert_claim(claim)
        claim.claim_id = claim_id

        # Enqueue into FIFO LinkedQueue
        self.claim_queue.enqueue(claim)

        # Mark item status as CLAIM_PENDING
        self.update_item_status(item_id, ItemStatus.CLAIM_PENDING.value)

        return claim

    def process_next_claim(self, formula: str, variables: Dict[str, float], approve_threshold: float = 70.0) -> Tuple[Optional[ClaimRecord], float, str]:
        """
        Processes the earliest submitted claim in FIFO order using LinkedQueue.
        Evaluates matching confidence dynamically using Stack Expression Parser.
        """
        if self.claim_queue.is_empty():
            return None, 0.0, "No pending claims in queue."

        # Dequeue the first claim in line (O(1))
        claim = self.claim_queue.dequeue()
        if not claim:
            return None, 0.0, "Queue empty."

        # Evaluate score using Stack Expression Parser
        confidence_score = ExpressionParser.evaluate(formula, variables)
        claim.confidence_score = confidence_score

        if confidence_score >= approve_threshold:
            claim.claim_status = ClaimStatus.APPROVED.value
            decision = f"APPROVED (Confidence: {confidence_score:.2f}% >= {approve_threshold}%)"
            # Update item to VERIFIED_RETURNED
            self.update_item_status(claim.item_id, ItemStatus.VERIFIED_RETURNED.value)
        else:
            claim.claim_status = ClaimStatus.REJECTED.value
            decision = f"REJECTED (Confidence: {confidence_score:.2f}% < {approve_threshold}%)"
            # Revert item status back to IN_CUSTODY
            self.update_item_status(claim.item_id, ItemStatus.IN_CUSTODY.value)

        # Update in DB
        self.db.update_claim_status(claim.claim_id, claim.claim_status, claim.confidence_score)

        return claim, confidence_score, decision

    def get_pending_claims(self) -> List[ClaimRecord]:
        """Get all pending claims currently waiting in FIFO queue."""
        return self.claim_queue.to_list()

    # --- LIFO Action Stack & Multi-Level Undo ---

    def undo_last_action(self) -> Optional[str]:
        """
        Pops the most recent action from LinkedStack and reverts system state.
        Time Complexity: O(N) for rollback reconciliation.
        """
        if self.undo_stack.is_empty():
            return None

        action = self.undo_stack.pop()
        if not action:
            return None

        action_type = action.action_type

        if action_type == "INSERT":
            # Revert insertion -> delete item
            self.item_list.delete_by_id(action.item_id)
            self.db.delete_item(action.item_id)
            return f"Undid INSERT for Item ID #{action.item_id} (Item removed)."

        elif action_type == "STATUS_CHANGE" or action_type == "UPDATE":
            # Revert to snapshot_before
            if action.snapshot_before:
                prev_item = ItemRecord.from_dict(action.snapshot_before)
                self.item_list.update_item(action.item_id, prev_item)
                self.db.update_item(prev_item)
                return f"Undid {action_type} for Item ID #{action.item_id} (Reverted to '{prev_item.status}')."

        elif action_type == "DELETE":
            # Revert deletion -> re-insert item
            if action.snapshot_before:
                restored_item = ItemRecord.from_dict(action.snapshot_before)
                self.item_list.insert_tail(restored_item)
                self.db.insert_item(restored_item)
                return f"Undid DELETE for Item ID #{action.item_id} (Restored '{restored_item.title}')."

        return f"Undid action: {action_type}"

    def get_action_history(self) -> List[AuditAction]:
        """Traverse the LIFO stack to view all recent actions."""
        return self.undo_stack.to_list()

    # --- Custody / Storage Fee Calculation with Dynamic Formula ---

    def calculate_custody_fee(self, formula: str, variables: Dict[str, float]) -> float:
        """
        Evaluates dynamic fee/penalty formula via Stack Expression Evaluator.
        """
        return ExpressionParser.evaluate(formula, variables)
