# 🏛️ Lost and Found Management System (Phase 1)
**Course**: Data Structures and Algorithms Practical  
**Topic**: Linear Data Structures Implementation (CLO1) with MySQL Integration

---

## 📌 Project Overview
The **Lost and Found Management System** is a data structure-centric and database-backed application engineered to streamline the logging, custody management, verification, matching, and retrieval of lost and found items in institutional environments (universities, corporate campuses, airports, transit hubs).

### Phase 1 Focus (CLO1):
1. **Singly Linked List (`ItemLinkedList`)**: Pure pointer-based node structure for item records, supporting $O(1)$ head/tail operations, sorted insertions, deletions, and linear keyword searches.
2. **Linked Queue (`ClaimVerificationQueue`)**: Pure pointer-based FIFO queue with `front` and `rear` pointers to ensure claims are verified in strict first-come, first-served order.
3. **Linked Stack (`AuditUndoStack`)**: Pure pointer-based LIFO stack with `top` pointer for multi-level action snapshots, enabling seamless undo and rollback capabilities.
4. **Stack-Based Expression Evaluator (`ExpressionParser`)**: Delimiter balancing checker, Dijkstra's Shunting-Yard Infix-to-Postfix (RPN) converter, and operand stack evaluator for dynamic matching confidence and storage fee formulas.
5. **Relational Database (`MySQL` / `SQLite`)**: Persistent relational storage layer for items, claims, and audit logs with bidirectional synchronization.

---

## 🗂️ Practical Syllabus Requirements & Data Structure Mapping

| Syllabus Requirement | Implemented Component | Source File | Operations Supported | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Project Input Data Definition** | `ItemRecord`, `ClaimRecord`, `AuditAction` | [`src/models.py`](src/models.py) | Schema validation, type conversion, serialization | $O(1)$ | $O(1)$ |
| **Linked List Data Storage** | `ItemLinkedList`, `ListNode` | [`src/linked_list.py`](src/linked_list.py) | `insert_head`, `insert_tail`, `insert_sorted`, `delete_by_id`, `search_by_id`, `search_by_keyword`, `update_status`, `to_list` | Insert Head/Tail: $O(1)$<br>Search/Delete/Sorted: $O(N)$ | $O(N)$ |
| **Linked Queue (FIFO)** | `LinkedQueue`, `QueueNode` | [`src/queue.py`](src/queue.py) | `enqueue`, `dequeue`, `peek_front`, `peek_rear`, `is_empty`, `to_list` | Enqueue: $O(1)$<br>Dequeue: $O(1)$<br>Peek: $O(1)$ | $O(N)$ |
| **Linked Stack (LIFO)** | `LinkedStack`, `StackNode` | [`src/stack.py`](src/stack.py) | `push`, `pop`, `peek`, `is_empty`, `to_list`, `clear` | Push: $O(1)$<br>Pop: $O(1)$<br>Peek: $O(1)$ | $O(N)$ |
| **Stack for Expression Handling** | `ExpressionParser` | [`src/expression_parser.py`](src/expression_parser.py) | Delimiter balancing (`()`, `[]`, `{}`), Infix $\to$ Postfix (Shunting-Yard), Postfix RPN evaluation with variables | Validation: $O(N)$<br>Conversion: $O(N)$<br>Evaluation: $O(N)$ | $O(N)$ |
| **Relational DB Persistence** | `DatabaseManager` | [`database/db_manager.py`](database/db_manager.py) | MySQL connection pool, DDL migration, CRUD sync, SQLite fallback | DB Operations: $O(1)$ / $O(N)$ | $O(N)$ |

---

## 📁 Directory Structure

```
lost_found_system_phase1/
├── config/
│   └── db_config.py          # MySQL and database configuration parameters
├── database/
│   ├── schema.sql            # MySQL DDL script (tables, foreign keys, indexes)
│   └── db_manager.py         # Persistent database layer (MySQL + SQLite fallback)
├── src/
│   ├── __init__.py
│   ├── models.py             # ItemRecord, ClaimRecord, AuditAction dataclasses
│   ├── linked_list.py        # Node-based Singly Linked List (pure pointers)
│   ├── stack.py              # Node-based Linked Stack (LIFO)
│   ├── queue.py              # Node-based Linked Queue (FIFO)
│   ├── expression_parser.py  # Stack-based Formula Evaluator & Delimiter checker
│   └── service.py            # Business orchestrator connecting DSA with DB
├── data/
│   └── seed_items.json       # Initial seed records for testing
├── tests/
│   ├── test_linked_list.py   # Unit tests for Singly Linked List
│   ├── test_stack_queue.py   # Unit tests for Stack and Queue
│   ├── test_expression.py    # Unit tests for Expression Parser & Formulas
│   └── test_db_sync.py       # Integration tests for DB synchronization
├── main.py                   # Interactive Menu-driven CLI Dashboard & Demo
├── requirements.txt          # Dependencies
└── README.md                 # Project & Practical documentation
```

---

## 🗄️ MySQL Database Setup

### 1. Configure MySQL Credentials (Optional)
By default, the application connects to MySQL with `localhost:3306`, user `root`, password `password`, database `lost_found_db`. You can set environment variables:
```bash
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=your_mysql_password
set DB_NAME=lost_found_db
```

### 2. Auto-Fallback Mechanism
If MySQL is not running on the host machine, the system automatically and seamlessly falls back to a local SQLite database (`data/lost_found_local.db`) so development, testing, and grading work out-of-the-box!

---

## 🚀 How to Run

### 1. Launch Modern Web UI & REST Server (Recommended)
You can launch the web interface directly using Python (zero extra packages required):
```powershell
python web_server.py
```
Then open your browser at **`http://localhost:8080`**.
Alternatively, select Option `16` from `main.py`!

### 2. Launch Interactive CLI
```powershell
python main.py
```

### 3. Run Automated End-to-End Demonstration
Select Option `11` from the main menu inside `main.py`, or run:
```powershell
python -c "from src.service import LostAndFoundService; from main import run_automated_demo; run_automated_demo(LostAndFoundService(prefer_mysql=False))"
```

### 4. Run Automated Practical Suites
```powershell
python phase2_demo.py    # Phase 2: DDL, DML, Aggregates
python phase3_demo.py    # Phase 3: Joins, Subqueries, Views & EXPLAIN
python phase4_demo.py    # Phase 4: Transactions, ACID Commit/Rollback, Audit
```

---

## 💡 Practical Scenarios Covered

### 1. FIFO Claim Verification Pipeline
- When a user submits an ownership claim for a found item, the claim is enqueued into the `LinkedQueue`.
- The custodian verifies claims in first-come, first-served order (`dequeue()`), preventing starvation and prioritizing earlier submissions.

### 2. Stack-Based Dynamic Confidence & Fee Evaluation
- Verification confidence formula:
  $$\text{Confidence} = (\text{desc\_match} \times 0.50) + (\text{serial\_match} \times 0.30) + (\text{id\_match} \times 0.20)$$
- Custody storage fee formula:
  $$\text{Fee} = (\text{days\_stored} \times 3.50) + (\text{item\_val} \times 0.02) - \text{waiver\_discount}$$
- The `ExpressionParser` uses `LinkedStack` to check delimiter balance, convert Infix to Postfix RPN, and evaluate expressions dynamically.

### 3. Multi-Level LIFO Undo System
- Any item insertion, status transition, or deletion pushes a state snapshot onto the `LinkedStack`.
- When an admin triggers "Undo Last Action", the system pops the most recent action from the stack and restores the prior state in both the Linked List and the database.
