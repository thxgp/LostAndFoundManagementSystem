# 📘 PROJECT OBSERVATION & LAB RECORD REPORT

**Project Title:** Lost and Found Management System  
**Course:** Advanced Database Management Systems (ADBMS) & Data Structures Practical  
**Target CLO:** CLO1 (Linear Data Structures & Relational Database Integration)  
**Database Engine:** MySQL / MariaDB  
**Programming Interface:** Python 3.x (Connector & CLI Integration)  

---

## 1. 📑 Executive Summary
The **Lost and Found Management System** is an integrated database and algorithmic software solution engineered to automate the reporting, custody logging, verification, matching, and return of misplaced items across institutional campuses (e.g., universities, airports, corporate facilities). 

The system couples a **3NF-Normalized MySQL Relational Database** with **fundamental Linear Data Structures** in memory:
1. **Singly Linked List** for dynamic inventory storage and $O(1)$ tail insertions.
2. **FIFO Linked Queue** for processing verification claims in fair arrival order.
3. **LIFO Linked Stack** for multi-level action snapshots and audit rollback/undo.
4. **Stack-based Expression Parser (Shunting-Yard RPN)** for dynamic weighted matching confidence and custody fee evaluation.

---

## 2. 🏛️ Introduction
In large-scale academic institutions and public complexes, thousands of personal belongings (identification cards, laptops, keys, wallets, backpacks, books, and lab equipment) are misplaced annually. 

Traditional lost and found workflows rely heavily on fragmented physical registers, unorganized storage shelves, and manual security desk inquiries. This manual approach results in high rates of unclaimed assets, wrongful claims, and operational overhead. 

The **Lost and Found Management System** transitions this workflow into a centralized, transparent, and auditable digital platform. It guarantees data integrity via MySQL ACID properties while delivering high-speed in-memory data structure operations for real-time administrative workflows.

---

## 3. 🌐 Background
Historically, institutional lost-and-found administration suffers from:
* **Decentralized Custody**: Multiple independent security gates and library help desks maintain isolated paper records with no unified search capability.
* **Absence of Proof Verification**: Security officers rely on informal verbal descriptions, increasing the vulnerability to fraudulent ownership claims.
* **No Queue Fairness**: Inquiries and claims are handled arbitrarily, causing starvation of earlier submitted claims.
* **Lack of Historical Auditability**: Manual registers offer no transactional snapshot tracking, making it impossible to audit custody transitions or revert accidental record updates.

Modern Database Management Systems (DBMS) coupled with custom algorithmic data structures resolve these challenges by providing normalized persistence, indexing, transactional consistency, and predictable algorithmic time complexities.

---

## 4. ⚠️ Problem Statement
To design and implement a robust, normalized, and performant **Lost and Found Management System** that satisfies the following core objectives:
1. **Centralized Data Storage**: Persist items, categories, locations, users, claims, custody lockers, and audit logs using a 3NF-compliant relational database.
2. **Instant Searchability**: Enable multi-attribute searching across titles, categories, descriptions, and recovery locations.
3. **Fair Claim Processing**: Enforce strict First-In, First-Out (FIFO) verification scheduling for claim tickets to prevent inquiry starvation.
4. **Dynamic Match Confidence Evaluation**: Compute objective ownership matching scores using stack-evaluated dynamic weighted formulas rather than arbitrary manual assessments.
5. **State Rollback & Audit Trail**: Maintain a Last-In, First-Out (LIFO) action stack capable of reverting accidental state updates or deletions without data loss.

---

## 5. 🧩 System Modules & Data Dictionary

The system is decomposed into **seven functional modules**, each mapped to a dedicated normalized table.

---

### Module 1: User Management (`users`)
* **Purpose**: Manages authenticated student, faculty, security custodian, and administrative profiles.
* **Table Name**: `users`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `INT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique user identifier |
| `full_name` | `VARCHAR(100)` | `NOT NULL` | Legal name of user |
| `email` | `VARCHAR(120)` | `NOT NULL, UNIQUE` | Institutional email ID |
| `phone` | `VARCHAR(20)` | `NOT NULL` | Active contact telephone |
| `role` | `ENUM` | `DEFAULT 'STUDENT'` | `'STUDENT'`, `'STAFF'`, `'ADMIN'`, `'CUSTODIAN'` |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Account registration timestamp |

---

### Module 2: Category Taxonomy (`categories`)
* **Purpose**: Classifies items into standardized groups and defines storage rates.
* **Table Name**: `categories`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `category_id` | `INT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique category code |
| `category_name` | `VARCHAR(60)` | `NOT NULL, UNIQUE` | E.g., `Electronics`, `Documents/Cards` |
| `description` | `VARCHAR(200)` | `NULL` | Classification criteria |
| `daily_storage_rate`| `DECIMAL(6,2)` | `DEFAULT 20.00` | Standard daily holding rate (₹) |

---

### Module 3: Campus Locations (`locations`)
* **Purpose**: Tracks discovery points and associated physical recovery/security desks.
* **Table Name**: `locations`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `location_id` | `INT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique location identifier |
| `building_name` | `VARCHAR(100)` | `NOT NULL` | Facility (e.g., Central Library) |
| `room_area` | `VARCHAR(100)` | `NOT NULL` | Specific area (e.g., Lab 304) |
| `recovery_desk` | `VARCHAR(80)` | `NOT NULL` | Custody desk holding items found here |

---

### Module 4: Lost & Found Inventory (`items`)
* **Purpose**: Core inventory table tracking reported lost and found items and their lifecycle states.
* **Table Name**: `items`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `item_id` | `INT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique asset tracking number |
| `reported_by_user_id`| `INT` | `FOREIGN KEY -> users(user_id)` | Reporter identity reference |
| `category_id` | `INT` | `FOREIGN KEY -> categories(category_id)`| Category taxonomy reference |
| `location_id` | `INT` | `FOREIGN KEY -> locations(location_id)` | Location reference |
| `title` | `VARCHAR(150)` | `NOT NULL` | Brief item title/name |
| `description` | `TEXT` | `NOT NULL` | Distinguishing details, marks, serials |
| `item_type` | `ENUM` | `NOT NULL` | `'LOST'` or `'FOUND'` |
| `status` | `ENUM` | `DEFAULT 'REPORTED'` | `'REPORTED'`, `'IN_CUSTODY'`, `'CLAIM_PENDING'`, `'VERIFIED_RETURNED'`, `'DISPOSED'` |
| `reporter_name` | `VARCHAR(100)` | `NOT NULL` | Reporter display name |
| `reporter_contact`| `VARCHAR(50)` | `NOT NULL` | Reporter email/phone |
| `reward_or_value`| `DECIMAL(10,2)`| `DEFAULT 0.00` | Estimated value or reward (₹) |
| `reported_date` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Report submission timestamp |
| `updated_at` | `DATETIME` | `ON UPDATE CURRENT_TIMESTAMP` | Last status modification timestamp |

---

### Module 5: Claim Verification Pipeline (`claims`)
* **Purpose**: Records ownership claims submitted by users for found items (FIFO Queue).
* **Table Name**: `claims`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `claim_id` | `BIGINT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique claim verification ticket |
| `item_id` | `INT` | `FOREIGN KEY -> items(item_id)` | Target found item |
| `claimant_user_id`| `INT` | `FOREIGN KEY -> users(user_id)` | Claimant user reference |
| `claimant_name` | `VARCHAR(100)` | `NOT NULL` | Claimant full name |
| `claimant_contact`| `VARCHAR(50)` | `NOT NULL` | Claimant contact info |
| `proof_description`| `TEXT` | `NOT NULL` | Ownership proof, passwords, receipts |
| `confidence_score`| `DECIMAL(5,2)` | `DEFAULT 0.00` | Stack-evaluated match score (0-100%) |
| `claim_status` | `ENUM` | `DEFAULT 'PENDING'` | `'PENDING'`, `'APPROVED'`, `'REJECTED'` |
| `submitted_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Submission timestamp (Queue ordering) |
| `verified_by_user_id`| `INT` | `FOREIGN KEY -> users(user_id)` | Custodian who verified the claim |

---

### Module 6: Action Audit Trail & Undo History (`audit_actions`)
* **Purpose**: Stores immutable chronological snapshots of record transitions (LIFO Stack).
* **Table Name**: `audit_actions`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `action_id` | `BIGINT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique audit entry identifier |
| `item_id` | `INT` | `FOREIGN KEY -> items(item_id)` | Associated item |
| `performed_by_user_id`| `INT` | `FOREIGN KEY -> users(user_id)` | User who executed the action |
| `action_type` | `VARCHAR(50)` | `NOT NULL` | `'INSERT'`, `'STATUS_CHANGE'`, `'DELETE'` |
| `snapshot_before`| `JSON` | `NULL` | Prior record state (for LIFO Undo) |
| `snapshot_after` | `JSON` | `NULL` | Post-action record state |
| `performed_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Action execution timestamp |

---

### Module 7: Custody Storage & Locker Allocation (`storage_lockers`)
* **Purpose**: Manages physical locker assignments and calculates custody holding fees.
* **Table Name**: `storage_lockers`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `locker_id` | `INT` | `PRIMARY KEY, AUTO_INCREMENT` | Unique locker allocation record |
| `item_id` | `INT` | `FOREIGN KEY -> items(item_id)` | Stored item reference |
| `locker_code` | `VARCHAR(20)` | `NOT NULL` | Physical locker box ID (e.g., `L-104`) |
| `custody_start_date`| `DATE` | `NOT NULL` | Date item entered storage |
| `release_date` | `DATE` | `NULL` | Date item was returned / released |
| `total_custody_fee`| `DECIMAL(8,2)` | `DEFAULT 0.00` | Calculated custody handling fee (₹) |

---

## 6. 💻 Data Manipulation Language (DML) Commands Used

### 1. `INSERT` Operations

```sql
-- DML 1.1: Register a new user
INSERT INTO users (full_name, email, phone, role) 
VALUES ('Aarav Sharma', 'aarav.sharma@campus.edu', '+91 9876543210', 'STUDENT');

-- DML 1.2: Add a new item category
INSERT INTO categories (category_name, description, daily_storage_rate) 
VALUES ('Electronics', 'Laptops, smartphones, headphones, chargers', 25.00);

-- DML 1.3: Add a campus location
INSERT INTO locations (building_name, room_area, recovery_desk) 
VALUES ('Central Library', '2nd Floor Quiet Zone', 'Library Helpdesk Floor 1');

-- DML 1.4: Log a newly reported found item
INSERT INTO items (
    reported_by_user_id, category_id, location_id, title, category, description,
    item_type, location, status, reporter_name, reporter_contact, reward_or_value, reported_date
) VALUES (
    1, 1, 1, 'MacBook Pro 14 M2 Space Gray', 'Electronics',
    'Left in Library 2nd floor silent study area, has sticker "Code is Poetry"',
    'FOUND', 'Central Library 2nd Floor', 'IN_CUSTODY',
    'Aarav Sharma', 'aarav.sharma@campus.edu', 125000.00, NOW()
);

-- DML 1.5: Enqueue a verification claim for an item
INSERT INTO claims (
    item_id, claimant_user_id, claimant_name, claimant_contact,
    proof_description, confidence_score, claim_status, submitted_at
) VALUES (
    1, 2, 'Priya Patel', 'priya.patel@campus.edu',
    'Password lock screen photo of pet dog, serial ending in 4829', 0.00, 'PENDING', NOW()
);

-- DML 1.6: Push an audit action snapshot to the audit table (LIFO Stack)
INSERT INTO audit_actions (
    item_id, performed_by_user_id, action_type, snapshot_before, snapshot_after, performed_at
) VALUES (
    1, 3, 'STATUS_CHANGE', 
    JSON_OBJECT('status', 'IN_CUSTODY'), 
    JSON_OBJECT('status', 'CLAIM_PENDING'), 
    NOW()
);
```

---

### 2. `UPDATE` Operations

```sql
-- DML 2.1: Update item status when a claim is processed
UPDATE items 
SET status = 'VERIFIED_RETURNED', updated_at = NOW() 
WHERE item_id = 1;

-- DML 2.2: Update claim verification outcome and confidence score
UPDATE claims 
SET claim_status = 'APPROVED', confidence_score = 96.00, verified_by_user_id = 3 
WHERE claim_id = 1;

-- DML 2.3: Modify item reward value
UPDATE items 
SET reward_or_value = 500.00, updated_at = NOW() 
WHERE item_id = 3;

-- DML 2.4: Rollback item status during LIFO Undo execution
UPDATE items 
SET status = 'IN_CUSTODY', updated_at = NOW() 
WHERE item_id = 1;
```

---

### 3. `DELETE` Operations

```sql
-- DML 3.1: Delete an item by ID
DELETE FROM items 
WHERE item_id = 5;

-- DML 3.2: Remove rejected claims older than 90 days
DELETE FROM claims 
WHERE claim_status = 'REJECTED' AND submitted_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

---

## 7. 🔍 Key `SELECT` Queries Used

### Query 1: Inventory Listing with Category and Location (Multi-Table `INNER JOIN`)
```sql
SELECT 
    i.item_id AS "ID",
    i.item_type AS "Type",
    i.title AS "Item Title",
    c.category_name AS "Category",
    l.building_name AS "Building",
    l.room_area AS "Specific Area",
    i.status AS "Status",
    CONCAT('₹', FORMAT(i.reward_or_value, 2)) AS "Value / Reward",
    i.reporter_name AS "Reported By"
FROM items i
LEFT JOIN categories c ON i.category_id = c.category_id
LEFT JOIN locations l ON i.location_id = l.location_id
ORDER BY i.item_id ASC;
```

---

### Query 2: Pending Claim Verification Queue (FIFO Order)
```sql
SELECT 
    c.claim_id AS "Claim ID",
    c.item_id AS "Item ID",
    i.title AS "Item Claimed",
    c.claimant_name AS "Claimant Name",
    c.claimant_contact AS "Contact",
    c.proof_description AS "Proof Details",
    c.submitted_at AS "Queued At"
FROM claims c
JOIN items i ON c.item_id = i.item_id
WHERE c.claim_status = 'PENDING'
ORDER BY c.submitted_at ASC;
```

---

### Query 3: Multi-Keyword Search (Matching Title, Description, or Category)
```sql
SELECT 
    item_id, item_type, title, category, location, status, reporter_contact
FROM items
WHERE LOWER(title) LIKE '%calculator%'
   OR LOWER(description) LIKE '%calculator%'
   OR LOWER(category) LIKE '%calculator%'
   OR LOWER(location) LIKE '%calculator%'
ORDER BY reported_date DESC;
```

---

### Query 4: Aggregate Summary of Items by Status and Category
```sql
SELECT 
    category,
    COUNT(*) AS total_items,
    SUM(CASE WHEN item_type = 'FOUND' THEN 1 ELSE 0 END) AS total_found,
    SUM(CASE WHEN item_type = 'LOST' THEN 1 ELSE 0 END) AS total_lost,
    SUM(CASE WHEN status = 'VERIFIED_RETURNED' THEN 1 ELSE 0 END) AS total_returned,
    CONCAT('₹', FORMAT(SUM(reward_or_value), 2)) AS total_inventory_value
FROM items
GROUP BY category
ORDER BY total_items DESC;
```

---

### Query 5: Full Audit Log History (LIFO Snapshot Inspection)
```sql
SELECT 
    a.action_id AS "Log ID",
    a.action_type AS "Operation",
    a.item_id AS "Item ID",
    i.title AS "Item Title",
    u.full_name AS "Initiated By",
    a.snapshot_before AS "State Before",
    a.snapshot_after AS "State After",
    a.performed_at AS "Timestamp"
FROM audit_actions a
LEFT JOIN items i ON a.item_id = i.item_id
LEFT JOIN users u ON a.performed_by_user_id = u.user_id
ORDER BY a.action_id DESC;
```

---

## 8. 📐 Database Normalization (Step-by-Step Walkthrough)

To eliminate update anomalies, deletion anomalies, and insertion anomalies, the schema was normalized from an unnormalized monolithic flat structure to **Third Normal Form (3NF)**.

---

### Step 1: Unnormalized Form (UNF)
A monolithic single table storing all student, location, category, item, claim, and locker details together:

$$\text{UNF\_RECORDS}(\underline{\text{item\_id}}, \text{title}, \text{category\_name}, \text{cat\_desc}, \text{storage\_rate}, \text{building}, \text{room}, \text{desk}, \text{user\_name}, \text{user\_email}, \text{user\_phone}, \text{claimant\_names}, \text{proof\_texts}, \text{locker\_code})$$

* **Anomalies Present**:
  * Multi-valued attributes (`claimant_names`, `proof_texts` contain repeating groups for an item).
  * Massive redundancy of category descriptions and building names repeated across thousands of item rows.

---

### Step 2: First Normal Form (1NF)
* **Rule**: Each column must contain atomic (indivisible) values, and every table must possess a unique Primary Key.
* **Action**: Multi-valued claim records are segregated into a separate entity (`CLAIMS`) with singular atomic fields.

$$\text{ITEMS\_1NF}(\underline{\text{item\_id}}, \text{title}, \text{category\_name}, \text{cat\_desc}, \text{daily\_rate}, \text{building}, \text{room}, \text{desk}, \text{reporter\_name}, \text{reporter\_email}, \text{status}, \text{value})$$

$$\text{CLAIMS\_1NF}(\underline{\text{claim\_id}}, \text{item\_id}, \text{claimant\_name}, \text{claimant\_email}, \text{proof\_desc}, \text{status}, \text{submitted\_at})$$

---

### Step 3: Second Normal Form (2NF)
* **Rule**: Must be in 1NF, and **no partial functional dependencies** must exist on any composite key (all non-prime attributes must be fully functionally dependent on the Primary Key).
* **Action**: In our schema, all tables possess single-attribute primary keys (`item_id`, `claim_id`), satisfying 2NF inherently. However, reporter and category attributes are decoupled into independent relations to remove dependency on the item key.

---

### Step 4: Third Normal Form (3NF)
* **Rule**: Must be in 2NF, and **no transitive dependencies** ($X \to Y \to Z$) must exist (non-prime attributes must not depend on other non-prime attributes).
* **Transitive Dependencies Identified in 2NF**:
  1. $\text{item\_id} \to \text{category\_id} \to \{\text{category\_name}, \text{description}, \text{daily\_storage\_rate}\}$
  2. $\text{item\_id} \to \text{location\_id} \to \{\text{building\_name}, \text{room\_area}, \text{recovery\_desk}\}$
  3. $\text{item\_id} \to \text{reported\_by\_user\_id} \to \{\text{full\_name}, \text{email}, \text{phone}, \text{role}\}$
  4. $\text{claim\_id} \to \text{claimant\_user\_id} \to \{\text{full\_name}, \text{email}, \text{phone}\}$

* **Resolution to 3NF**: Decompose into independent normalized relations with Foreign Key constraints:
  * `USERS` ($\underline{\text{user\_id}}$, full_name, email, phone, role)
  * `CATEGORIES` ($\underline{\text{category\_id}}$, category_name, description, daily_storage_rate)
  * `LOCATIONS` ($\underline{\text{location\_id}}$, building_name, room_area, recovery_desk)
  * `ITEMS` ($\underline{\text{item\_id}}$, $\text{reported\_by\_user\_id}^*$, $\text{category\_id}^*$, $\text{location\_id}^*$, title, description, item_type, status, reward_or_value, reported_date)
  * `CLAIMS` ($\underline{\text{claim\_id}}$, $\text{item\_id}^*$, $\text{claimant\_user\_id}^*$, proof_description, confidence_score, claim_status, submitted_at)
  * `AUDIT_LOGS` ($\underline{\text{log\_id}}$, $\text{item\_id}^*$, $\text{performed\_by\_user\_id}^*$, action_type, snapshot_before, snapshot_after, timestamp)
  * `STORAGE_LOCKERS` ($\underline{\text{locker\_id}}$, $\text{item\_id}^*$, locker_code, custody_start_date, release_date, total_custody_fee)

$$\text{Final Schema is strictly in \textbf{3NF / BCNF} with zero transitive redundancy.}$$

---

## 9. 🏁 Conclusion
The **Lost and Found Management System** successfully addresses the operational and data management bottlenecks of conventional lost property tracking. 

By unifying a **3NF-normalized relational MySQL schema** with **algorithmic linear data structures** (Singly Linked List, FIFO Queue, LIFO Stack, and Shunting-Yard Expression Evaluator), the application achieves:
* **ACID Data Durability** for persistent storage.
* **$O(1)$ and $O(N)$ In-Memory Operations** for real-time responsiveness.
* **Deterministic Verification & Auditability** via mathematical match scoring and multi-level action rollback.

The resulting system establishes a scalable foundation for subsequent practical phases (Hierarchical Category Trees, Graph-based Campus Route Traversals, and Dynamic Programming Fuzzy Matching).
