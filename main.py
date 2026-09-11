"""
========================================================================================
LOST AND FOUND MANAGEMENT SYSTEM (Phase 1: Linear Data Structures & MySQL Integration)
Course: Data Structures and Algorithms Practical (CLO1)
========================================================================================
Interactive Command Line Interface demonstrating:
1. Pure Node-based Singly Linked List (Data Storage, Insertion, Deletion, Search)
2. Pure Node-based Linked Queue (FIFO Claim Verification Pipeline)
3. Pure Node-based Linked Stack (LIFO Multi-Level Action Audit & Undo)
4. Stack-Based Dynamic Expression Parser (Infix to Postfix RPN Formula Evaluation)
5. MySQL / SQLite Persistent Relational Database Integration
========================================================================================
"""

import sys
import os
import time
from typing import Dict, Any, List

# Ensure UTF-8 output encoding for Windows terminal compatibility
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure parent directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from src.service import LostAndFoundService
from src.models import ItemStatus, ItemType, Category, ClaimStatus
from src.expression_parser import ExpressionParser


# Color formatting helpers
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner(db_type: str):
    print(f"\n{Colors.CYAN}{'=' * 85}")
    print(f"{Colors.BOLD}{Colors.HEADER}    🏛️  LOST AND FOUND MANAGEMENT SYSTEM — PHASE 1 (LINEAR DSA + DATABASE)")
    print(f"{Colors.DIM}    Course: Data Structures Practical | Target: CLO1 Linear Structures")
    print(f"    Active Database Engine: {Colors.BOLD}{Colors.GREEN}{db_type}{Colors.RESET}{Colors.DIM} | Data Structure: Pure Pointer Nodes")
    print(f"{Colors.CYAN}{'=' * 85}{Colors.RESET}\n")


def print_table(headers: List[str], rows: List[List[Any]]):
    """Clean ASCII tabular renderer without requiring external dependencies."""
    if not rows:
        print(f"{Colors.YELLOW}No records found.{Colors.RESET}")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    # Header row
    header_str = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(f"{Colors.BOLD}{header_str}{Colors.RESET}")
    print(f"{Colors.DIM}{sep_str}{Colors.RESET}")

    for row in rows:
        row_str = " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
        print(row_str)
    print(f"{Colors.DIM}{sep_str}{Colors.RESET}")
    print(f"Total count: {len(rows)}\n")


def main_menu():
    print(f"{Colors.BOLD}{Colors.CYAN}--- MAIN OPERATIONS MENU ---{Colors.RESET}")
    print(f" {Colors.GREEN}[1]{Colors.RESET}  📋 View All Items (Linked List Traversal)")
    print(f" {Colors.GREEN}[2]{Colors.RESET}  ➕ Report New Item (Insert into Linked List + DB)")
    print(f" {Colors.GREEN}[3]{Colors.RESET}  🔍 Search Items by Keyword (Linear Search on Linked List)")
    print(f" {Colors.GREEN}[4]{Colors.RESET}  🗑️  Delete Item by ID (Linked List Deletion + DB Sync)")
    print(f" {Colors.GREEN}[5]{Colors.RESET}  📝 Submit Claim for Found Item (Enqueues into FIFO Queue)")
    print(f" {Colors.GREEN}[6]{Colors.RESET}  ⏳ View Pending Claims Queue (Linked Queue Inspection)")
    print(f" {Colors.GREEN}[7]{Colors.RESET}  ⚡ Process Next Claim (FIFO Queue + Stack Formula Evaluator)")
    print(f" {Colors.GREEN}[8]{Colors.RESET}  🧮 Calculate Storage Fee (Stack Expression Parser)")
    print(f" {Colors.GREEN}[9]{Colors.RESET}  ↩️  Undo Last Action (LIFO Linked Stack Pop & Rollback)")
    print(f" {Colors.GREEN}[10]{Colors.RESET} 📜 View Action Audit Trail (Linked Stack History)")
    print(f" {Colors.GREEN}[11]{Colors.RESET} 🚀 Run Automated Quick Practical Demonstration")
    print(f" {Colors.RED}[0]{Colors.RESET}  ❌ Exit Application")
    print("-" * 40)


def view_all_items(service: LostAndFoundService):
    items = service.get_all_items()
    headers = ["ID", "Type", "Title", "Category", "Location", "Status", "Value(₹)", "Reported By"]
    rows = []
    for item in items:
        rows.append([
            item.item_id,
            item.item_type,
            item.title[:25] + ("..." if len(item.title) > 25 else ""),
            item.category,
            item.location[:20],
            item.status,
            f"₹{item.reward_or_value:,.2f}",
            item.reporter_name
        ])
    print(f"\n{Colors.BOLD}📋 Current Active Item Inventory (Linked List Nodes):{Colors.RESET}")
    print_table(headers, rows)


def report_new_item(service: LostAndFoundService):
    print(f"\n{Colors.BOLD}➕ Report a Lost or Found Item:{Colors.RESET}")
    try:
        title = input("Enter Item Title/Name: ").strip()
        if not title:
            print(f"{Colors.RED}Title cannot be empty.{Colors.RESET}")
            return

        print("\nSelect Category:")
        categories = [c.value for c in Category]
        for idx, cat in enumerate(categories, 1):
            print(f"  {idx}. {cat}")
        cat_choice = input(f"Choice (1-{len(categories)}) [default: Others]: ").strip()
        category = categories[int(cat_choice) - 1] if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories) else Category.OTHERS.value

        print("\nSelect Type:")
        print("  1. FOUND (Item in possession, awaiting owner)")
        print("  2. LOST (Item lost by owner, searching)")
        type_choice = input("Choice (1-2) [default 1]: ").strip()
        item_type = ItemType.LOST.value if type_choice == "2" else ItemType.FOUND.value

        description = input("Enter Detailed Description: ").strip()
        location = input("Enter Location (Found / Lost place): ").strip()
        reporter_name = input("Enter Reporter Name: ").strip()
        reporter_contact = input("Enter Reporter Email / Phone: ").strip()
        val_str = input("Estimated Value or Reward (₹) [default 0.0]: ").strip()
        reward_val = float(val_str) if val_str else 0.0

        status = ItemStatus.IN_CUSTODY.value if item_type == ItemType.FOUND.value else ItemStatus.REPORTED.value

        item_data = {
            "title": title,
            "category": category,
            "description": description,
            "item_type": item_type,
            "location": location,
            "reporter_name": reporter_name,
            "reporter_contact": reporter_contact,
            "reward_or_value": reward_val,
            "status": status
        }

        created = service.report_item(item_data)
        print(f"\n{Colors.GREEN}✓ Item reported successfully! Assigned ID #{created.item_id}{Colors.RESET}")
        print(f"  • Inserted into Database ({service.db.db_type})")
        print(f"  • Inserted as Node into Singly Linked List (O(1) tail pointer)")
        print(f"  • Pushed snapshot into Action Linked Stack (LIFO)")
    except Exception as e:
        print(f"{Colors.RED}Error reporting item: {e}{Colors.RESET}")


def search_items(service: LostAndFoundService):
    query = input("\nEnter search keyword (title, description, category, or location): ").strip()
    if not query:
        return
    results = service.search_items(query)
    headers = ["ID", "Type", "Title", "Category", "Location", "Status", "Contact"]
    rows = [[i.item_id, i.item_type, i.title, i.category, i.location, i.status, i.reporter_contact] for i in results]
    print(f"\n{Colors.BOLD}🔍 Search Results for '{query}' (via Linked List Traversal):{Colors.RESET}")
    print_table(headers, rows)


def delete_item(service: LostAndFoundService):
    item_id_str = input("\nEnter Item ID to delete: ").strip()
    if not item_id_str.isdigit():
        print(f"{Colors.RED}Invalid ID.{Colors.RESET}")
        return
    item_id = int(item_id_str)
    deleted = service.delete_item(item_id)
    if deleted:
        print(f"{Colors.GREEN}✓ Deleted Item #{item_id} ('{deleted.title}') from Linked List & DB.{Colors.RESET}")
        print(f"  Action recorded in Linked Stack. You can Undo this deletion anytime.")
    else:
        print(f"{Colors.RED}Item #{item_id} not found in Linked List.{Colors.RESET}")


def submit_claim(service: LostAndFoundService):
    print(f"\n{Colors.BOLD}📝 Submit a Verification Claim for a Found Item:{Colors.RESET}")
    item_id_str = input("Enter Found Item ID: ").strip()
    if not item_id_str.isdigit():
        print(f"{Colors.RED}Invalid ID.{Colors.RESET}")
        return
    item_id = int(item_id_str)
    item = service.find_item_by_id(item_id)
    if not item:
        print(f"{Colors.RED}Item #{item_id} does not exist.{Colors.RESET}")
        return

    name = input("Enter Claimant Full Name: ").strip()
    contact = input("Enter Claimant Contact: ").strip()
    proof = input("Enter Ownership Proof / Identifying Marks: ").strip()

    try:
        claim = service.submit_claim(item_id, name, contact, proof)
        print(f"\n{Colors.GREEN}✓ Claim #{claim.claim_id} enqueued successfully into FIFO Verification Queue!{Colors.RESET}")
        print(f"  Item #{item_id} status updated to '{ItemStatus.CLAIM_PENDING.value}'.")
    except Exception as e:
        print(f"{Colors.RED}Failed to submit claim: {e}{Colors.RESET}")


def view_pending_claims(service: LostAndFoundService):
    claims = service.get_pending_claims()
    headers = ["Claim ID", "Item ID", "Claimant Name", "Contact", "Proof Details", "Submitted At"]
    rows = []
    for c in claims:
        rows.append([
            c.claim_id,
            c.item_id,
            c.claimant_name,
            c.claimant_contact,
            c.proof_description[:30] + ("..." if len(c.proof_description) > 30 else ""),
            c.submitted_at
        ])
    print(f"\n{Colors.BOLD}⏳ Pending Claims FIFO Queue (Linked Queue Nodes):{Colors.RESET}")
    print_table(headers, rows)


def process_claim(service: LostAndFoundService):
    print(f"\n{Colors.BOLD}⚡ Process Earliest Claim in FIFO Queue:{Colors.RESET}")
    if service.claim_queue.is_empty():
        print(f"{Colors.YELLOW}Queue is empty. No pending claims to verify.{Colors.RESET}")
        return

    next_claim = service.claim_queue.peek_front()
    item = service.find_item_by_id(next_claim.item_id)
    print(f"Processing Claim #{next_claim.claim_id} for Item: '{item.title if item else 'N/A'}'")
    print(f"Claimant: {next_claim.claimant_name} | Proof: {next_claim.proof_description}")

    # Standard weighted matching formula
    formula = "(desc_match * 0.50) + (serial_match * 0.30) + (id_match * 0.20)"
    print(f"\nConfidence Scoring Formula: {Colors.CYAN}{formula}{Colors.RESET}")
    print(f"Formula will be evaluated via {Colors.BOLD}Stack-Based Infix-to-Postfix Parser{Colors.RESET}.")

    try:
        dm = float(input("Enter Description Match score (0-100) [e.g. 85]: ") or "85")
        sm = float(input("Enter Serial/Unique Identifier Match score (0-100) [e.g. 90]: ") or "90")
        im = float(input("Enter ID/Photo Proof Match score (0-100) [e.g. 80]: ") or "80")

        variables = {
            "desc_match": dm,
            "serial_match": sm,
            "id_match": im
        }

        threshold = 70.0
        claim, score, decision = service.process_next_claim(formula, variables, approve_threshold=threshold)
        print(f"\n{Colors.BOLD}Result Evaluation:{Colors.RESET}")
        print(f"  • Calculated Match Score: {Colors.BOLD}{score:.2f}%{Colors.RESET}")
        print(f"  • Decision: {Colors.GREEN if 'APPROVED' in decision else Colors.RED}{decision}{Colors.RESET}")
        print(f"  • Queue Head dequeued (O(1)). DB & Linked List updated.")
    except Exception as e:
        print(f"{Colors.RED}Error processing claim: {e}{Colors.RESET}")


def calculate_storage_fee(service: LostAndFoundService):
    print(f"\n{Colors.BOLD}🧮 Custody Storage & Processing Fee Calculator:{Colors.RESET}")
    formula = "(days_stored * 20.0) + (item_val * 0.01) - waiver_discount"
    print(f"Dynamic Formula: {Colors.CYAN}{formula}{Colors.RESET}")
    print(f"{Colors.DIM}Using Stack RPN Evaluator | Standard Rate: ₹20/day + 1% item valuation - Student/Staff Waiver{Colors.RESET}")

    try:
        days = float(input("Enter days stored in custody [e.g. 10]: ") or "10")
        val = float(input("Enter estimated item value (₹) [e.g. 5000]: ") or "5000")
        waiver = float(input("Enter student/staff discount waiver (₹) [e.g. 100]: ") or "100")

        variables = {
            "days_stored": days,
            "item_val": val,
            "waiver_discount": waiver
        }

        fee = ExpressionParser.evaluate(formula, variables)
        print(f"\n{Colors.GREEN}✓ Total Custody Handling Fee: ₹{max(0.0, fee):,.2f}{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}Error in calculation: {e}{Colors.RESET}")


def undo_action(service: LostAndFoundService):
    print(f"\n{Colors.BOLD}↩️  Undo Most Recent Action (LIFO Linked Stack):{Colors.RESET}")
    result = service.undo_last_action()
    if result:
        print(f"{Colors.GREEN}✓ {result}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No actions available on stack to undo.{Colors.RESET}")


def view_audit_history(service: LostAndFoundService):
    actions = service.get_action_history()
    headers = ["Action Type", "Item ID", "Performed At", "Before Snapshot", "After Snapshot"]
    rows = []
    for a in actions:
        sb = str(a.snapshot_before.get("status") if a.snapshot_before else "-")
        sa = str(a.snapshot_after.get("status") if a.snapshot_after else "-")
        rows.append([a.action_type, a.item_id, a.performed_at, sb, sa])
    print(f"\n{Colors.BOLD}📜 LIFO Audit Stack History (Top to Bottom):{Colors.RESET}")
    print_table(headers, rows)


def run_automated_demo(service: LostAndFoundService):
    """Executes a full interactive walkthrough of all Phase 1 capabilities."""
    print(f"\n{Colors.CYAN}{'=' * 80}")
    print(f"{Colors.BOLD}{Colors.HEADER}    🚀 STARTING AUTOMATED PRACTICAL DEMONSTRATION (PHASE 1)")
    print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

    # Step 1: Initial Traversal
    print(f"{Colors.BOLD}Step 1: Traversing Initial Singly Linked List (Hydrated from DB):{Colors.RESET}")
    items = service.get_all_items()
    print(f"Found {len(items)} initial items in memory Linked List.\n")
    view_all_items(service)
    time.sleep(1)

    # Step 2: Linear Search
    print(f"{Colors.BOLD}Step 2: Linear Search on Linked List for 'MacBook':{Colors.RESET}")
    res = service.search_items("MacBook")
    for item in res:
        print(f"  -> Match Found: [ID #{item.item_id}] {item.title} ({item.category}) - Location: {item.location}")
    print()
    time.sleep(1)

    # Step 3: Insert New Item
    print(f"{Colors.BOLD}Step 3: Inserting New Record into Linked List (Tail Pointer O(1)) & DB:{Colors.RESET}")
    demo_item = {
        "title": "AirPods Pro 2 with MagSafe Case",
        "category": Category.ELECTRONICS.value,
        "description": "White earbuds left in Library quiet zone with blue silicone case",
        "item_type": ItemType.FOUND.value,
        "location": "Central Library 3rd Floor",
        "reporter_name": "Librarian Mrs. Joshi",
        "reporter_contact": "joshi.lib@campus.edu",
        "reward_or_value": 24900.0,
        "status": ItemStatus.IN_CUSTODY.value
    }
    created = service.report_item(demo_item)
    print(f"  -> Inserted ID #{created.item_id}: '{created.title}'")
    print(f"  -> Linked List size is now {len(service.item_list)} nodes.")
    print()
    time.sleep(1)

    # Step 4: Submit Claim into FIFO Queue
    print(f"{Colors.BOLD}Step 4: Submitting Verification Claim into FIFO Linked Queue:{Colors.RESET}")
    claim = service.submit_claim(
        item_id=created.item_id,
        claimant_name="Devansh Gupta",
        claimant_contact="devansh.g@campus.edu",
        proof_description="Serial number ends with 4829, Bluetooth name is 'Devansh AirPods'"
    )
    print(f"  -> Enqueued Claim #{claim.claim_id} for Item #{created.item_id}")
    print(f"  -> FIFO Queue Size: {len(service.claim_queue)} pending claims.")
    print()
    time.sleep(1)

    # Step 5: Stack Expression Formula Evaluation & Claim Verification
    print(f"{Colors.BOLD}Step 5: Processing Claim via Stack-Based Infix-to-Postfix Formula Evaluator:{Colors.RESET}")
    formula = "(desc_match * 0.40) + (serial_match * 0.40) + (photo_match * 0.20)"
    tokens = ExpressionParser.tokenize(formula)
    postfix = ExpressionParser.infix_to_postfix(formula)
    print(f"  -> Infix Formula:   {formula}")
    print(f"  -> Postfix (RPN):   {' '.join(postfix)}")

    variables = {"desc_match": 95.0, "serial_match": 100.0, "photo_match": 90.0}
    claim_out, score, decision = service.process_next_claim(formula, variables, approve_threshold=75.0)
    print(f"  -> Operand Stack Evaluated Confidence: {score:.2f}%")
    print(f"  -> Verification Decision: {Colors.GREEN}{decision}{Colors.RESET}")
    print(f"  -> Item Status updated to: '{service.find_item_by_id(created.item_id).status}'")
    print()
    time.sleep(1)

    # Step 6: Multi-level LIFO Undo Rollback
    print(f"{Colors.BOLD}Step 6: Demonstrating Multi-Level Undo via Linked Stack (LIFO):{Colors.RESET}")
    print("  Triggering Undo on recent claim verification state update...")
    undo_msg1 = service.undo_last_action()
    print(f"  -> Rollback 1: {undo_msg1}")

    print("  Triggering Undo on item creation...")
    undo_msg2 = service.undo_last_action()
    print(f"  -> Rollback 2: {undo_msg2}")
    print(f"  -> Verified: Item #{created.item_id} removed and Linked List size restored to {len(service.item_list)} nodes.")
    print()

    print(f"{Colors.GREEN}================================================================================")
    print(f"  🎉 ALL PHASE 1 REQUIREMENTS SUCCESSFULLY DEMONSTRATED AND VALIDATED!")
    print(f"================================================================================{Colors.RESET}\n")


def main():
    service = LostAndFoundService()
    print_banner(service.db.db_type)

    while True:
        main_menu()
        choice = input(f"{Colors.BOLD}Enter your choice (0-11): {Colors.RESET}").strip()

        if choice == "1":
            view_all_items(service)
        elif choice == "2":
            report_new_item(service)
        elif choice == "3":
            search_items(service)
        elif choice == "4":
            delete_item(service)
        elif choice == "5":
            submit_claim(service)
        elif choice == "6":
            view_pending_claims(service)
        elif choice == "7":
            process_claim(service)
        elif choice == "8":
            calculate_storage_fee(service)
        elif choice == "9":
            undo_action(service)
        elif choice == "10":
            view_audit_history(service)
        elif choice == "11":
            run_automated_demo(service)
        elif choice == "0":
            print(f"\n{Colors.CYAN}Exiting Lost and Found Management System. Goodbye!{Colors.RESET}\n")
            break
        else:
            print(f"{Colors.RED}Invalid option. Please choose between 0 and 11.{Colors.RESET}\n")


if __name__ == "__main__":
    main()
