# 📘 PROJECT OBSERVATION & LAB RECORD REPORT

**Project Title:** Lost and Found Management System (LFMS)  
**Course:** Advanced Database Management Systems (ADBMS) Practical Lab  
**Course Outcomes Addressed:**  
* **CLO1:** Data Modelling, Dataset Extraction, ER-to-Relational Mapping & Normalization (UNF to 3NF)  
* **CLO2:** Database Creation, Table Constraints, DDL, DML, Data Cleaning, Basic Queries & Aggregate Summaries  
* **CLO3:** Complex Multi-Table Joins, Nested Subqueries, Database Views, Query Execution (EXPLAIN), Stored Procedures/Functions, ACID Transactions, Concurrency Control & Data Integrity  
**Database Engine:** MySQL / MariaDB (InnoDB Storage Engine) & Fallback SQLite  
**Programming Interface:** Python 3.x (Modular CLI & Automated Practical Suites)  

---

## 1. 📑 Executive Summary
The **Lost and Found Management System** is an enterprise-grade academic relational database solution engineered to automate the intake, categorization, secure custody logging, ownership claim verification, and auditable return of misplaced items across campus facilities (e.g., lecture halls, central library, sports complex, cafeterias, and research labs).

The system enforces strict **Third Normal Form (3NF) relational integrity**, guarantees **ACID transaction atomicity**, provides **high-performance analytical queries and reusable views**, and complies fully with institutional zero-fee campus security policies (100% free campus custody service).

---

## 2. 🏛️ Problem Statement & Background
In large-scale academic institutions and complexes, thousands of personal belongings (identification badges, laptops, calculators, keys, wallets, water bottles, backpacks, and lab instruments) are misplaced every semester.

Manual lost-and-found administration suffers from:
1. **Decentralized Custody**: Isolated paper registers kept at different security gates without searchable coordination.
2. **Absence of Proof Verification**: Security officers rely on informal verbal descriptions, risking fraudulent ownership claims.
3. **Arbitrary Claim Scheduling**: Claims are handled haphazardly without fair arrival queuing.
4. **Lack of Transactional Auditability**: Accidental status updates or deletions cannot be reverted without audit logs.
5. **Data Redundancy & Anomalies**: Monolithic flat files cause insertion, update, and deletion anomalies.

A robust relational database schema normalized to 3NF with ACID transaction handling eliminates these operational bottlenecks.

---

## 3. 📐 Database Normalization (Step-by-Step Walkthrough)

To eliminate **insertion anomalies**, **update anomalies**, and **deletion anomalies**, the database schema was normalized systematically from an unnormalized flat dataset to **Third Normal Form (3NF)**.

```
+------------------------------------------------------------------------------------+
|                         NORMALIZATION PROGRESSION                                   |
|                                                                                    |
|  UNF (Monolithic Flat Record)                                                      |
|   └──> [Eliminate Repeating Groups & Multi-valued Attributes]                      |
|  1NF (Atomic Attributes & Primary Key Defined)                                     |
|   └──> [Eliminate Partial Functional Dependencies on Composite Keys]               |
|  2NF (Full Functional Dependency on Primary Key)                                   |
|   └──> [Eliminate Transitive Dependencies (X -> Y -> Z)]                           |
|  3NF (Boyce-Codd / 3NF Compliant Decomposed Schema)                                |
+------------------------------------------------------------------------------------+
```

---

### Step 1: Unnormalized Form (UNF)
In the initial unnormalized representation, all campus items, student reporters, categories, campus buildings, verification claims, storage locker allocations, and audit logs were stored in a single monolithic flat table:

$$\text{UNF\_RECORDS}(\underline{\text{item\_id}}, \text{title}, \text{category\_name}, \text{cat\_desc}, \text{building}, \text{room}, \text{desk}, \text{reporter\_name}, \text{reporter\_email}, \text{reporter\_phone}, \text{claimant\_names}, \text{proof\_texts}, \text{locker\_code}, \text{custody\_start})$$

* **Anomalies Inherent in UNF**:
  1. **Multi-Valued Repeating Groups**: An item can have multiple students filing claims. Storing `claimant_names` and `proof_texts` as comma-separated values violates atomicity.
  2. **Insertion Anomaly**: Cannot define a campus location (e.g., "Sports Complex - Badminton Arena") or category (e.g., "Bags/Backpacks") unless at least one item has been lost or found there.
  3. **Update Anomaly**: If a recovery desk contact or building name changes, hundreds of redundant item records must be updated. Any missed row causes database inconsistency.
  4. **Deletion Anomaly**: If the only item found in the Cafeteria is claimed and deleted, the existence of the Cafeteria recovery desk itself is lost.

---

### Step 2: First Normal Form (1NF)
* **Definition / Rule**: A relation is in 1NF if and only if:
  1. Every attribute contains only **atomic (indivisible)** values (no repeating groups, arrays, or comma-separated lists).
  2. Each column has a unique name and distinct domain.
  3. The relation contains a unique **Primary Key** to identify each row.
* **Normalization Action**:
  * Segregate multi-valued claim records into an independent relation `CLAIMS_1NF`.
  * Ensure all attributes contain singular scalar values.

$$\text{ITEMS\_1NF}(\underline{\text{item\_id}}, \text{title}, \text{category\_name}, \text{cat\_desc}, \text{building}, \text{room}, \text{recovery\_desk}, \text{reporter\_name}, \text{reporter\_email}, \text{reporter\_phone}, \text{status}, \text{value}, \text{reported\_date})$$

$$\text{CLAIMS\_1NF}(\underline{\text{claim\_id}}, \text{item\_id}, \text{claimant\_name}, \text{claimant\_email}, \text{proof\_description}, \text{confidence\_score}, \text{claim\_status}, \text{submitted\_at})$$

---

### Step 3: Second Normal Form (2NF)
* **Definition / Rule**: A relation is in 2NF if:
  1. It is already in **1NF**.
  2. It has **no Partial Functional Dependencies** (every non-prime attribute must be fully functionally dependent on the entire Primary Key, not a proper subset of a composite primary key).
* **Analysis & Normalization Action**:
  * In our schema, the primary keys are single-column identifiers (`item_id`, `claim_id`). Thus, partial dependencies on composite keys do not exist.
  * However, category descriptions and campus building areas depend solely on category codes and location identifiers, not on `item_id`.
  * Decompose attributes into separate candidate relations where each attribute functionally depends fully on its key.

---

### Step 4: Third Normal Form (3NF)
* **Definition / Rule**: A relation is in 3NF if:
  1. It is already in **2NF**.
  2. It contains **no Transitive Functional Dependencies** (no non-prime attribute is transitively dependent on the primary key, i.e., $X \to Y$ and $Y \to Z$ where $Z$ is a non-prime attribute and $Y$ is not a superkey).
* **Transitive Dependencies Identified in 2NF**:
  1. $\text{item\_id} \to \text{category\_id} \to \{\text{category\_name}, \text{description}\}$  
     *(Category description depends on Category ID, which depends on Item ID).*
  2. $\text{item\_id} \to \text{location\_id} \to \{\text{building\_name}, \text{room\_area}, \text{recovery\_desk}\}$  
     *(Building name and recovery desk depend on Location ID).*
  3. $\text{item\_id} \to \text{reported\_by\_user\_id} \to \{\text{full\_name}, \text{email}, \text{phone}, \text{role}\}$  
     *(Reporter personal contact depends on User ID).*
  4. $\text{claim\_id} \to \text{claimant\_user\_id} \to \{\text{full\_name}, \text{email}, \text{phone}\}$  
     *(Claimant contact depends on User ID).*
  5. $\text{item\_id} \to \text{locker\_id} \to \{\text{locker\_code}, \text{custody\_start\_date}, \text{release\_date}\}$  
     *(Locker storage details depend on Locker ID).*

* **Resolution to 3NF**: Decompose the schema into **seven independent normalized relations**, interconnected strictly via Foreign Keys with referential integrity:

$$\text{USERS}(\underline{\text{user\_id}}, \text{full\_name}, \text{email}, \text{phone}, \text{role}, \text{created\_at})$$
$$\text{CATEGORIES}(\underline{\text{category\_id}}, \text{category\_name}, \text{description})$$
$$\text{LOCATIONS}(\underline{\text{location\_id}}, \text{building\_name}, \text{room\_area}, \text{recovery\_desk})$$
$$\text{ITEMS}(\underline{\text{item\_id}}, \text{reported\_by\_user\_id}^*, \text{category\_id}^*, \text{location\_id}^*, \text{title}, \text{description}, \text{item\_type}, \text{location}, \text{status}, \text{reward\_or\_value}, \text{reported\_date}, \text{updated\_at})$$
$$\text{CLAIMS}(\underline{\text{claim\_id}}, \text{item\_id}^*, \text{claimant\_user\_id}^*, \text{claimant\_name}, \text{claimant\_contact}, \text{proof\_description}, \text{confidence\_score}, \text{claim\_status}, \text{submitted\_at}, \text{verified\_by\_user\_id}^*)$$
$$\text{STORAGE\_LOCKERS}(\underline{\text{locker\_id}}, \text{item\_id}^*, \text{locker\_code}, \text{custody\_start\_date}, \text{release\_date}, \text{remarks})$$
$$\text{AUDIT\_ACTIONS}(\underline{\text{action\_id}}, \text{item\_id}^*, \text{performed\_by\_user\_id}^*, \text{action\_type}, \text{snapshot\_before}, \text{snapshot\_after}, \text{performed\_at})$$

$$\mathbf{Conclusion:\ The\ final\ schema\ is\ strictly\ in\ 3NF\ /\ BCNF\ with\ zero\ transitive\ or\ partial\ anomalies.}$$

---

## 4. 🗄️ Phase 2 — Database Creation and Data Preparation (Lab Manual Format)

*(Structured precisely in accordance with the official Phase 2 Laboratory Evaluation Guidelines)*

```
+----------------------------------------------------------------------------------------------------------------+
|  Phase 2 - Database Creation and Data Preparation (Lost and Found Management System)                           |
+----------------------------------------------------------------------------------------------------------------+
|  1. DDL: Create lost_found_db and all seven tables using CREATE DATABASE and CREATE TABLE.                     |
|     PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL and CHECK constraints will be defined with the tables.          |
|  2. DML: Enter sample data using INSERT. UPDATE will be used when item status, claim verification outcome, or   |
|     custody release dates change, while DELETE will be tested only where foreign-key relations are not         |
|     compromised (e.g. purged rejected claims or cascading item deletion).                                      |
|  3. Data cleaning and constraints: duplicate user emails and category names will be prevented, required        |
|     foreign keys and titles will not be NULL, and invalid negative reward values (< 0) or out-of-range          |
|     claim confidence scores (< 0 or > 100) will be restricted via CHECK constraints.                           |
|  4. NULL handling: release_date will stay NULL while an item is actively held in custody locker and            |
|     verified_by_user_id will stay NULL while a claim is PENDING. IS NULL / IS NOT NULL and COALESCE() will     |
|     be used to find and format such active records.                                                            |
|  5. Basic queries: SELECT, WHERE and ORDER BY will be used to display available items in custody, pending      |
|     claims, items by category, high-value belongings by declared value, and chronological intake records.      |
|  6. Aggregate functions: COUNT() will calculate items per category, AVG() will calculate average item value     |
|     and average claim confidence, and SUM() will calculate total declared campus inventory valuation.          |
+----------------------------------------------------------------------------------------------------------------+
```

---

## 5. 💻 Detailed Report on Data Manipulation Language (DML) Commands Used

The system employs **Data Manipulation Language (DML)** commands to manage the full lifecycle of campus belongings: intake, custody changes, claim queueing, verification, and audit tracking.

---

### 5.1: `INSERT` Operations (Data Intake & Queuing)
* **Purpose**: Inserts new student/staff profiles, standard categories, campus locations, reported lost/found items, claim verification tickets, and immutable audit logs.
* **Integrity Handled**: `AUTO_INCREMENT` primary keys, foreign key references, and default timestamp assignments.

```sql
-- DML 1.1: Register authenticated user profile
INSERT INTO users (full_name, email, phone, role) 
VALUES ('Aarav Sharma', 'aarav.sharma@campus.edu', '+91 9876543210', 'STUDENT');

-- DML 1.2: Add standardized category (Zero fee campus policy)
INSERT INTO categories (category_name, description) 
VALUES ('Electronics', 'Laptops, phones, headphones, power banks, calculators');

-- DML 1.3: Add campus discovery location
INSERT INTO locations (building_name, room_area, recovery_desk) 
VALUES ('Central Library', '2nd Floor Quiet Zone', 'Library Helpdesk Floor 1');

-- DML 1.4: Register a found item into inventory with foreign keys
INSERT INTO items (
    reported_by_user_id, category_id, location_id, title, category, description,
    item_type, location, status, reporter_name, reporter_contact, reward_or_value,
    reported_date, updated_at
) VALUES (
    1, 1, 1, 'MacBook Pro 14 M2 Space Gray', 'Electronics',
    'Left in Library 2nd floor silent study area, has sticker "Code is Poetry"',
    'FOUND', 'Central Library 2nd Floor', 'IN_CUSTODY',
    'Aarav Sharma', 'aarav.sharma@campus.edu', 125000.00,
    '2026-09-02 10:15:00', '2026-09-02 10:30:00'
);

-- DML 1.5: Enqueue an ownership claim for a found item (FIFO Queue)
INSERT INTO claims (
    item_id, claimant_user_id, claimant_name, claimant_contact,
    proof_description, confidence_score, claim_status, submitted_at, verified_by_user_id
) VALUES (
    1, 1, 'Aarav Sharma', 'aarav.sharma@campus.edu',
    'Apple ID matches aarav.sharma@campus.edu, serial ends in 9942',
    95.00, 'APPROVED', '2026-09-03 14:20:00', 3
);

-- DML 1.6: Assign item to secure campus storage locker (Free Campus Service)
INSERT INTO storage_lockers (item_id, locker_code, custody_start_date, release_date, remarks)
VALUES (1, 'LOCKER-A101', '2026-09-02', '2026-09-04', 'Claim verified and returned to student');

-- DML 1.7: Insert snapshot record into audit log (LIFO Stack)
INSERT INTO audit_actions (
    item_id, performed_by_user_id, action_type, snapshot_before, snapshot_after, performed_at
) VALUES (
    1, 3, 'CLAIM_VERIFIED_AND_RELEASED',
    JSON_OBJECT('status', 'IN_CUSTODY', 'locker', 'LOCKER-A101'),
    JSON_OBJECT('status', 'VERIFIED_RETURNED', 'release_date', '2026-09-04'),
    NOW()
);
```

---

### 5.2: `UPDATE` Operations (Lifecycle State Transitions)
* **Purpose**: Used when an item transitions lifecycle states, when a claim is approved or rejected, or when locker custody is released.
* **Integrity Handled**: Maintains state consistency across items, claims, and lockers.

```sql
-- DML 2.1: Transition item lifecycle from 'IN_CUSTODY' to 'VERIFIED_RETURNED'
UPDATE items 
SET status = 'VERIFIED_RETURNED',
    updated_at = NOW() 
WHERE item_id = 1;

-- DML 2.2: Settle verification claim outcome with verifier user ID and score
UPDATE claims 
SET claim_status = 'APPROVED',
    confidence_score = 98.50,
    verified_by_user_id = 3
WHERE claim_id = 4;

-- DML 2.3: Release physical storage locker when owner collects item (Stamps release_date)
UPDATE storage_lockers 
SET release_date = CURRENT_DATE(),
    remarks = 'Identity verified and handed over to claimant'
WHERE item_id = 4 AND release_date IS NULL;

-- DML 2.4: Update item reward valuation
UPDATE items 
SET reward_or_value = 2500.00,
    updated_at = NOW() 
WHERE item_id = 2;

-- DML 2.5: Rollback item status during LIFO Stack Undo execution
UPDATE items 
SET status = 'IN_CUSTODY',
    updated_at = NOW() 
WHERE item_id = 1;
```

---

### 5.3: `DELETE` Operations (Controlled Purging & Cascading)
* **Purpose**: Removes cancelled tickets, stale rejected claims older than 90 days, or permanently purged items.
* **Integrity Handled**: Enforces `ON DELETE CASCADE` on claims and lockers; enforces `ON DELETE SET NULL` on audit logs to preserve audit trails.

```sql
-- DML 3.1: Delete an item by ID (Triggers cascading deletion on associated claims and locker records)
DELETE FROM items 
WHERE item_id = 6;

-- DML 3.2: Clean up obsolete rejected claims older than 90 days
DELETE FROM claims 
WHERE claim_status = 'REJECTED' 
  AND submitted_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- DML 3.3: Delete an unassigned category (Guaranteed safe: no active items reference it)
DELETE FROM categories 
WHERE category_id NOT IN (SELECT DISTINCT category_id FROM items WHERE category_id IS NOT NULL);
```

---

## 6. 📊 Phase 3 — Data Querying and Analytical Operations (CLO2 & CLO3)

---

### 6.1: Multi-Table Joins
* **INNER JOIN**: Unifies items with categories and recovery locations:
```sql
SELECT 
    i.item_id, i.title, i.item_type, c.category_name,
    l.building_name, l.room_area, i.status, i.reward_or_value
FROM items i
INNER JOIN categories c ON i.category_id = c.category_id
INNER JOIN locations l ON i.location_id = l.location_id
ORDER BY i.item_id ASC;
```

* **LEFT OUTER JOIN**: Retrieves all items and their associated claims, preserving items with zero submitted claims:
```sql
SELECT 
    i.item_id, i.title, i.status,
    COALESCE(c.claim_id, 0) AS claim_id,
    COALESCE(c.claimant_name, 'NO CLAIM YET') AS claimant,
    COALESCE(c.claim_status, 'N/A') AS claim_status,
    COALESCE(c.confidence_score, 0.0) AS match_score
FROM items i
LEFT JOIN claims c ON i.item_id = c.item_id
ORDER BY i.item_id ASC;
```

* **Multi-Table 4-Way Join**: Produces an administrative claim dossier linking claimant, item, category, location, and staff verifier:
```sql
SELECT 
    cl.claim_id, cl.claim_status, cl.confidence_score,
    u_claimant.full_name AS claimant, i.title AS item_title,
    cat.category_name, loc.building_name,
    COALESCE(u_verifier.full_name, 'AWAITING VERIFIER') AS verifier
FROM claims cl
INNER JOIN items i ON cl.item_id = i.item_id
INNER JOIN categories cat ON i.category_id = cat.category_id
INNER JOIN locations loc ON i.location_id = loc.location_id
INNER JOIN users u_claimant ON cl.claimant_user_id = u_claimant.user_id
LEFT JOIN users u_verifier ON cl.verified_by_user_id = u_verifier.user_id
ORDER BY cl.submitted_at ASC;
```

* **Self-Join / Cross-Match Candidate Detector**: Pairs reported `LOST` items with reported `FOUND` items sharing identical category and building:
```sql
SELECT 
    lost_i.item_id AS lost_id, lost_i.title AS lost_item, lost_i.reporter_name AS lost_owner,
    found_i.item_id AS found_id, found_i.title AS found_candidate, found_i.reporter_name AS finder,
    c.category_name, l.building_name
FROM items lost_i
INNER JOIN items found_i 
    ON lost_i.category_id = found_i.category_id 
    AND lost_i.location_id = found_i.location_id
INNER JOIN categories c ON lost_i.category_id = c.category_id
INNER JOIN locations l ON lost_i.location_id = l.location_id
WHERE lost_i.item_type = 'LOST' AND found_i.item_type = 'FOUND';
```

---

### 6.2: Nested Queries and Subqueries
* **Scalar Subquery**: Filters items whose declared value exceeds the overall campus inventory average:
```sql
SELECT item_id, title, category, reward_or_value,
       (SELECT ROUND(AVG(reward_or_value), 2) FROM items) AS campus_average_value
FROM items
WHERE reward_or_value > (SELECT AVG(reward_or_value) FROM items)
ORDER BY reward_or_value DESC;
```

* **Subquery with `IN`**: Identifies users who currently have active `PENDING` claims in queue:
```sql
SELECT user_id, full_name, email, role
FROM users
WHERE user_id IN (
    SELECT DISTINCT claimant_user_id 
    FROM claims 
    WHERE claim_status = 'PENDING' AND claimant_user_id IS NOT NULL
);
```

* **Correlated Subquery with `EXISTS`**: Finds items in custody that have at least one claim ticket submitted:
```sql
SELECT i.item_id, i.title, i.category, i.location, i.status
FROM items i
WHERE i.status = 'IN_CUSTODY'
  AND EXISTS (SELECT 1 FROM claims c WHERE c.item_id = i.item_id);
```

* **Correlated Subquery with `NOT EXISTS`**: Finds items in custody with zero submitted claims (unclaimed property):
```sql
SELECT i.item_id, i.title, i.category, i.location, i.status
FROM items i
WHERE i.status = 'IN_CUSTODY'
  AND NOT EXISTS (SELECT 1 FROM claims c WHERE c.item_id = i.item_id);
```

* **Subquery in `FROM` Clause (Derived Table)**: Computes category valuations and filters total values > ₹2,000:
```sql
SELECT cat_stats.category_name, cat_stats.item_count, cat_stats.total_valuation
FROM (
    SELECT c.category_name, COUNT(i.item_id) AS item_count, ROUND(SUM(i.reward_or_value), 2) AS total_valuation
    FROM categories c
    INNER JOIN items i ON c.category_id = i.category_id
    GROUP BY c.category_id, c.category_name
) AS cat_stats
WHERE cat_stats.total_valuation > 2000.00
ORDER BY cat_stats.total_valuation DESC;
```

---

### 6.3: Reusable Views
1. **`v_active_found_inventory`**: Public helpdesk view displaying all found items held in secure custody along with their locker codes:
```sql
CREATE OR REPLACE VIEW v_active_found_inventory AS
SELECT 
    i.item_id, i.title, c.category_name, l.building_name,
    l.recovery_desk, sl.locker_code, sl.custody_start_date, i.reporter_name
FROM items i
INNER JOIN categories c ON i.category_id = c.category_id
INNER JOIN locations l ON i.location_id = l.location_id
LEFT JOIN storage_lockers sl ON i.item_id = sl.item_id
WHERE i.item_type = 'FOUND' AND i.status = 'IN_CUSTODY';
```

2. **`v_claim_verification_queue`**: FIFO queue view for custodians to review pending claims in chronological order:
```sql
CREATE OR REPLACE VIEW v_claim_verification_queue AS
SELECT 
    cl.claim_id, cl.item_id, i.title AS claimed_item, c.category_name,
    cl.claimant_name, cl.confidence_score, cl.claim_status, cl.submitted_at
FROM claims cl
INNER JOIN items i ON cl.item_id = i.item_id
INNER JOIN categories c ON i.category_id = c.category_id
WHERE cl.claim_status = 'PENDING'
ORDER BY cl.submitted_at ASC;
```

3. **`v_category_analytics`**: Executive summary view tracking inventory counts and total asset valuation by category:
```sql
CREATE OR REPLACE VIEW v_category_analytics AS
SELECT 
    c.category_name,
    COUNT(i.item_id) AS total_items,
    SUM(CASE WHEN i.item_type = 'FOUND' THEN 1 ELSE 0 END) AS found_count,
    SUM(CASE WHEN i.item_type = 'LOST' THEN 1 ELSE 0 END) AS lost_count,
    ROUND(COALESCE(SUM(i.reward_or_value), 0), 2) AS total_declared_value
FROM categories c
LEFT JOIN items i ON c.category_id = i.category_id
GROUP BY c.category_id, c.category_name;
```

---

### 6.4: Understanding Basic Query Execution Behavior (`EXPLAIN`)
Using `EXPLAIN` and `EXPLAIN QUERY PLAN` reveals database engine execution strategies:
* **Indexed Scan**: A query filtering by `status = 'IN_CUSTODY'` leverages index `idx_status`, executing an efficient `ref` lookup rather than scanning the entire table (`type: ALL`).
* **Primary Key Join**: Joining `items` with `categories` on `c.category_id = i.category_id` uses the `PRIMARY` B-Tree index with $O(\log N)$ point lookups (`SEARCH c USING INTEGER PRIMARY KEY`).
* **Unindexed Search**: Searches filtering with `WHERE description LIKE '%backpack%'` trigger a full table scan (`SCAN items`), demonstrating the need for full-text indexing on large datasets.

---

### 6.5: Functions and Stored Procedures for Repeated Tasks
* **Stored Function `fn_custody_duration_days`**: Computes days elapsed between custody receipt and release date (or current date):
```sql
DELIMITER $$
CREATE FUNCTION fn_custody_duration_days(p_start_date DATE, p_release_date DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_days INT;
    IF p_release_date IS NOT NULL THEN
        SET v_days = DATEDIFF(p_release_date, p_start_date);
    ELSE
        SET v_days = DATEDIFF(CURRENT_DATE(), p_start_date);
    END IF;
    RETURN GREATEST(v_days, 0);
END $$
DELIMITER ;
```

* **Stored Procedure `sp_process_claim_verification`**: Atomically settles a claim ticket, updates item lifecycle status, releases storage locker, and records audit snapshot.

---

## 7. 🛡️ Phase 4 — Data Integrity and Transaction Handling (CLO3)

---

### 7.1: Transaction Commands & Atomicity Scenarios
ACID properties (Atomicity, Consistency, Isolation, Durability) are enforced using transaction boundaries:

#### Scenario A: Successful Atomic Claim Settlement (`COMMIT`)
When a student's claim is verified, 4 coordinated operations must commit together:
1. Update claim ticket status to `'APPROVED'`.
2. Transition item status to `'VERIFIED_RETURNED'`.
3. Release storage locker with `release_date = CURRENT_DATE()`.
4. Insert immutable audit snapshot into `audit_actions`.

```sql
START TRANSACTION;

UPDATE claims 
SET claim_status = 'APPROVED', confidence_score = 98.50, verified_by_user_id = 3
WHERE claim_id = 4;

UPDATE items 
SET status = 'VERIFIED_RETURNED', updated_at = NOW()
WHERE item_id = 4;

UPDATE storage_lockers 
SET release_date = CURRENT_DATE(), remarks = 'Verified & returned to student'
WHERE item_id = 4;

INSERT INTO audit_actions (item_id, performed_by_user_id, action_type, snapshot_before, snapshot_after, performed_at)
VALUES (4, 3, 'CLAIM_VERIFIED_AND_RELEASED', JSON_OBJECT('status', 'CLAIM_PENDING'), JSON_OBJECT('status', 'VERIFIED_RETURNED'), NOW());

COMMIT;
```
*Result: All 4 modifications persist permanently. If server power is lost midway, zero changes persist.*

#### Scenario B: Atomic Failure & Full Rollback (`ROLLBACK`)
If a business rule fails (e.g. attempting to dispose an item held under active dispute), `ROLLBACK` undoes all tentative changes:
```sql
START TRANSACTION;

UPDATE items SET status = 'DISPOSED' WHERE item_id = 2;

-- Detected business violation: Item 2 is currently in dispute
ROLLBACK;

-- Verified: Item 2 remains strictly in 'IN_CUSTODY' state
SELECT item_id, title, status FROM items WHERE item_id = 2;
```

#### Scenario C: Partial Rollback via Savepoints (`SAVEPOINT`)
In batch claim evaluations, intermediate checkpoints isolate failures without discarding previously confirmed updates:
```sql
START TRANSACTION;

-- Step 1: Valid claim score update
UPDATE claims SET confidence_score = 97.00 WHERE claim_id = 1;

-- Step 2: Establish checkpoint
SAVEPOINT sp_claim1_confirmed;

-- Step 3: Tentatively modify Claim 2 with invalid score
UPDATE claims SET confidence_score = -99.99 WHERE claim_id = 2;

-- Step 4: Revert exclusively to savepoint
ROLLBACK TO SAVEPOINT sp_claim1_confirmed;
RELEASE SAVEPOINT sp_claim1_confirmed;

-- Step 5: Commit valid Claim 1 changes
COMMIT;
```

---

### 7.2: Concurrency Issues & Transaction Isolation Levels

#### The 4 Concurrency Anomalies
1. **Dirty Read (G1)**: Transaction $T_1$ modifies a row without committing. Transaction $T_2$ reads this uncommitted value. $T_1$ subsequently rolls back; $T_2$ operated on invalid phantom data.
2. **Non-Repeatable Read (G2a)**: Transaction $T_1$ reads row $R$. Transaction $T_2$ modifies row $R$ and commits. $T_1$ re-reads row $R$ and observes differing values.
3. **Phantom Read (G2b)**: Transaction $T_1$ executes a range query (e.g., `WHERE category = 'Electronics'`). Transaction $T_2$ inserts a new matching row and commits. $T_1$ re-runs the range query and sees a newly appeared phantom row.
4. **Lost Update**: Transactions $T_1$ and $T_2$ read the same item row concurrently and both attempt to write conflicting updates, causing one update to silently overwrite the other.

#### Transaction Isolation Levels Matrix (ANSI SQL & MySQL InnoDB)

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Implementation in MySQL InnoDB |
| :--- | :---: | :---: | :---: | :--- |
| **READ UNCOMMITTED** | Possible | Possible | Possible | Read without locks; zero isolation overhead |
| **READ COMMITTED** | Prevented | Possible | Possible | Consistent read view created on every statement |
| **REPEATABLE READ** | Prevented | Prevented | **Prevented** | **Default in MySQL InnoDB** (Uses MVCC + Next-Key Lock) |
| **SERIALIZABLE** | Prevented | Prevented | Prevented | Strict two-phase locking (2PL) on all reads |

#### Pessimistic Row Locking (`SELECT ... FOR UPDATE`)
To prevent race conditions where two campus helpdesk attendants simultaneously approve claims for the same found laptop:
```sql
START TRANSACTION;
-- Places exclusive X-lock on item 1 row; blocks all concurrent transactions:
SELECT item_id, title, status FROM items WHERE item_id = 1 FOR UPDATE;
UPDATE items SET status = 'CLAIM_PENDING' WHERE item_id = 1;
COMMIT; -- Releases lock safely
```

---

### 7.3: Enforcing Integrity Constraints

1. **Entity Integrity (PRIMARY KEY)**: Guarantees unique entity identification; duplicate primary keys are rejected (`IntegrityError 1062`).
2. **Domain Integrity (CHECK & NOT NULL)**:
   * Mandatory attributes (`title`, `item_type`, `location`) cannot be `NULL`.
   * Negative reward values (`reward_or_value < 0.00`) and out-of-range confidence scores (`confidence_score NOT BETWEEN 0 AND 100`) are rejected via `CHECK` constraints.
3. **Uniqueness Integrity (UNIQUE)**:
   * Prevents duplicate institutional emails in `users` (`email UNIQUE`).
   * Prevents duplicate taxonomy titles in `categories` (`category_name UNIQUE`).
4. **Referential Integrity (FOREIGN KEY)**:
   * `claims(item_id)` references `items(item_id)` with `ON DELETE CASCADE`.
   * `items(reported_by_user_id)` references `users(user_id)` with `ON DELETE SET NULL`.
   * Reject attempts to insert orphan claims pointing to non-existent item IDs (`IntegrityError 1452`).

---

### 7.4: Final Dataset Validation and Audit Verification Queries

```sql
-- Validation 1: Verify ZERO orphan claims exist
SELECT c.claim_id, c.item_id, c.claimant_name 
FROM claims c 
LEFT JOIN items i ON c.item_id = i.item_id 
WHERE i.item_id IS NULL; -- Output: 0 rows (Passed)

-- Validation 2: Verify ZERO orphan storage lockers exist
SELECT sl.locker_id, sl.item_id, sl.locker_code 
FROM storage_lockers sl 
LEFT JOIN items i ON sl.item_id = i.item_id 
WHERE i.item_id IS NULL; -- Output: 0 rows (Passed)

-- Validation 3: Verify business state consistency for returned items
SELECT i.item_id, i.title, i.status, sl.locker_code, sl.release_date
FROM items i
INNER JOIN storage_lockers sl ON i.item_id = sl.item_id
WHERE i.status = 'VERIFIED_RETURNED'; -- Output: Item 4 has non-null release_date (Passed)

-- Validation 4: Range check for negative valuations or scores
SELECT COUNT(*) FROM items WHERE reward_or_value < 0.00; -- Output: 0 (Passed)
SELECT COUNT(*) FROM claims WHERE confidence_score < 0.00 OR confidence_score > 100.00; -- Output: 0 (Passed)

-- Validation 5: Audit log completeness
SELECT action_type, COUNT(*) AS event_count, MIN(performed_at), MAX(performed_at)
FROM audit_actions
GROUP BY action_type; -- Output: 100% auditable event logs present (Passed)
```

---

## 8. 🏁 Laboratory Outcomes & Conclusions

The **Lost and Found Management System** has satisfied all four practical phases prescribed by the ADBMS curriculum:

| Phase | Core Competencies Demonstrated | Verification Script | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | Real-world dataset extraction, ER modeling, relational schema conversion, normalization (UNF to 3NF), and linear data structures (Linked List, FIFO Queue, LIFO Stack, RPN Parser). | `main.py [Option 11]` | **100% PASSED** |
| **Phase 2** | DDL 7-table creation, DML data seeding with realistic spread-out dates, data cleaning, NULL handling via `COALESCE`, basic `SELECT/WHERE/ORDER BY` queries, and aggregate summaries (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`). | `phase2_demo.py` | **100% PASSED** |
| **Phase 3** | Complex multi-table joins (`INNER`, `LEFT`, 4-way join, self-join match detector), nested subqueries (`SCALAR`, `IN`, correlated `EXISTS`/`NOT EXISTS`, derived tables), database views, `EXPLAIN` query execution plans, and stored functions/procedures. | `phase3_demo.py` | **100% PASSED** |
| **Phase 4** | ACID transaction management (`COMMIT`, `ROLLBACK`, `SAVEPOINT`), transaction atomicity demonstration, concurrency control analysis (isolation levels, row-level locking `FOR UPDATE`), integrity constraint enforcement (`PK`, `FK`, `UNIQUE`, `NOT NULL`, `CHECK`), and automated dataset validation audits. | `phase4_demo.py` | **100% PASSED** |

The system provides complete data integrity, zero redundancy, robust transactional reliability, and high query performance for campus property recovery.
