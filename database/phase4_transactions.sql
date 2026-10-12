-- ====================================================================
-- LOST AND FOUND MANAGEMENT SYSTEM — PHASE 4 SQL TRANSACTIONS & INTEGRITY
-- Course: Advanced Database Management Systems (ADBMS)
-- Target: CLO3 (Data Integrity, Transaction Handling & Concurrency Control)
-- Database Engine: MySQL / MariaDB (InnoDB Storage Engine)
-- ====================================================================

USE lost_found_db;

-- ====================================================================
-- PART 1: TRANSACTION COMMANDS & ATOMICITY SCENARIOS (CLO3)
-- ====================================================================

-- --------------------------------------------------------------------
-- SCENARIO 1: SUCCESSFUL ATOMIC CLAIM SETTLEMENT (COMMIT)
-- Business Flow: A verified student claims a found item.
-- Atomicity Requirement: The 4 operations MUST succeed together or fail together:
--   1. Update claim record status -> APPROVED
--   2. Update item lifecycle status -> VERIFIED_RETURNED
--   3. Release physical custody locker -> Set release_date to CURRENT_DATE
--   4. Record audit snapshot entry in audit_actions
-- --------------------------------------------------------------------

START TRANSACTION;

-- Step 1: Update the claim ticket
UPDATE claims 
SET claim_status = 'APPROVED',
    confidence_score = 98.50,
    verified_by_user_id = 3
WHERE claim_id = 4 AND claim_status = 'PENDING';

-- Step 2: Transition item status to VERIFIED_RETURNED
UPDATE items 
SET status = 'VERIFIED_RETURNED',
    updated_at = NOW()
WHERE item_id = 4 AND status IN ('REPORTED', 'IN_CUSTODY', 'CLAIM_PENDING');

-- Step 3: Release storage locker holding the item
UPDATE storage_lockers 
SET release_date = CURRENT_DATE(),
    remarks = 'Identity verified and handed over to claimant'
WHERE item_id = 4 AND release_date IS NULL;

-- Step 4: Record immutable audit snapshot
INSERT INTO audit_actions (
    item_id, performed_by_user_id, action_type, snapshot_before, snapshot_after, performed_at
) VALUES (
    4, 3, 'CLAIM_VERIFIED_AND_RELEASED',
    JSON_OBJECT('status', 'CLAIM_PENDING', 'locker_state', 'OCCUPIED'),
    JSON_OBJECT('status', 'VERIFIED_RETURNED', 'locker_state', 'RELEASED'),
    NOW()
);

-- Atomicity Guaranteed: Persist all four modifications permanently
COMMIT;


-- --------------------------------------------------------------------
-- SCENARIO 2: ATOMIC FAILURE HANDLING & FULL ROLLBACK (ROLLBACK)
-- Business Flow: An invalid operation occurs (e.g., attempting to return
-- an item that has already been disposed or invalid foreign key).
-- When an error occurs, ROLLBACK reverts all partial changes, leaving
-- the database in a completely clean, uncorrupted state.
-- --------------------------------------------------------------------

START TRANSACTION;

-- Step 1: Preliminary update succeeds
UPDATE items 
SET status = 'CLAIM_PENDING',
    updated_at = NOW()
WHERE item_id = 2;

-- Step 2: An invalid operation triggers or condition fails (e.g. invalid item ID 99999)
-- In application logic, a validation exception is caught or SQL fails:
-- Simulating detection of invalid condition:
ROLLBACK; 

-- Verification: Status of item 2 remained 'IN_CUSTODY', never corrupted by partial changes!
SELECT item_id, title, status FROM items WHERE item_id = 2;


-- --------------------------------------------------------------------
-- SCENARIO 3: PARTIAL ROLLBACK VIA SAVEPOINT (SAVEPOINT & ROLLBACK TO)
-- Business Flow: Batch claim verification for multiple students.
-- Process Claim 1 successfully -> Set SAVEPOINT
-- Process Claim 2 -> Encounters bad data / rejected condition
-- ROLLBACK TO SAVEPOINT undoes Claim 2 without discarding Claim 1.
-- --------------------------------------------------------------------

START TRANSACTION;

-- Action A: Process first valid claim
UPDATE claims 
SET confidence_score = 88.00 
WHERE claim_id = 1;

-- Establish intermediate checkpoint
SAVEPOINT after_claim_one;

-- Action B: Attempt speculative or tentative modification
UPDATE claims 
SET confidence_score = -50.00 -- Invalid logical score!
WHERE claim_id = 2;

-- Revert exclusively to checkpoint after detecting bad score
ROLLBACK TO SAVEPOINT after_claim_one;

-- Release checkpoint resources and commit confirmed operations
RELEASE SAVEPOINT after_claim_one;
COMMIT;


-- ====================================================================
-- PART 2: CONCURRENCY ISSUES & TRANSACTION ISOLATION (CONCEPTUAL & SQL)
-- ====================================================================

-- 2.1: View Current Transaction Isolation Level in MySQL
SELECT @@GLOBAL.transaction_isolation AS global_isolation,
       @@SESSION.transaction_isolation AS session_isolation;

-- 2.2: The 4 Classic Concurrency Anomalies:
--   1. DIRTY READ: Transaction A reads data modified by Transaction B before B has committed.
--      If B rolls back, Transaction A operated on "dirty" phantom values.
--   2. NON-REPEATABLE READ: Transaction A reads a row twice. Between the two reads,
--      Transaction B commits an UPDATE to that row, causing Transaction A to see different values.
--   3. PHANTOM READ: Transaction A executes a range query (e.g., WHERE category='Electronics').
--      Between reads, Transaction B INSERTs a new matching row and commits. Transaction A sees a phantom row.
--   4. LOST UPDATE: Two transactions read the same item row concurrently and both update it;
--      one overwrites the other without taking its changes into account.

-- 2.3: MySQL InnoDB Isolation Levels:
-- Level 1: READ UNCOMMITTED (Allows Dirty Reads, Non-Repeatable Reads, Phantom Reads)
-- SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- Level 2: READ COMMITTED (Prevents Dirty Reads; Allows Non-Repeatable & Phantom Reads)
-- SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Level 3: REPEATABLE READ (Default in MySQL InnoDB; Uses MVCC & Next-Key Locks to prevent Phantom Reads)
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Level 4: SERIALIZABLE (Strictest; Forces all transactions into serial execution order)
-- SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 2.4: Pessimistic Row Locking (`SELECT ... FOR UPDATE`) in Lost & Found
-- Prevents race condition where two campus helpdesks attempt to claim the same item simultaneously:
START TRANSACTION;

SELECT item_id, title, status 
FROM items 
WHERE item_id = 1 
FOR UPDATE; -- Exclusive X-Lock held on row until COMMIT / ROLLBACK

-- Any other concurrent transaction attempting to read or update item 1 will wait until this commits:
UPDATE items SET status = 'CLAIM_PENDING' WHERE item_id = 1;

COMMIT;


-- ====================================================================
-- PART 3: ENFORCING INTEGRITY CONSTRAINTS (CLO3)
-- ====================================================================

-- 3.1: Entity Integrity (PRIMARY KEY)
-- Verification that duplicate item IDs are strictly rejected:
-- INSERT INTO items (item_id, title, category, ...) VALUES (1, 'Duplicate Test', ...); -> ERROR 1062

-- 3.2: Domain Integrity (CHECK Constraints & NOT NULL)
-- Enforce non-negative reward values and valid score ranges:
ALTER TABLE items 
ADD CONSTRAINT chk_item_value_non_negative CHECK (reward_or_value >= 0.00);

ALTER TABLE claims 
ADD CONSTRAINT chk_confidence_score_range CHECK (confidence_score >= 0.00 AND confidence_score <= 100.00);

-- 3.3: Referential Integrity (FOREIGN KEY with ON DELETE Constraints)
-- Items belong to Categories: ON DELETE SET NULL preserves item record even if taxonomy changes.
-- Claims belong to Items: ON DELETE CASCADE automatically purges claims when item is purged.
-- Lockers belong to Items: ON DELETE CASCADE frees locker linkage when item record is deleted.

-- Test Referential Integrity: Reject orphan claim with non-existent item_id
-- INSERT INTO claims (item_id, claimant_name, claimant_contact, proof_description, submitted_at)
-- VALUES (99999, 'Ghost User', 'ghost@campus.edu', 'Proof', NOW()); -> ERROR 1452 (Cannot add or update child row)


-- ====================================================================
-- PART 4: DATASET VALIDATION QUERIES (CLO3)
-- ====================================================================

-- 4.1: Referential Integrity Check for Orphan Claims
-- Expected result: 0 rows (No claims referencing missing items)
SELECT c.claim_id, c.item_id, c.claimant_name 
FROM claims c 
LEFT JOIN items i ON c.item_id = i.item_id 
WHERE i.item_id IS NULL;

-- 4.2: Referential Integrity Check for Orphan Storage Lockers
-- Expected result: 0 rows (No lockers assigned to missing items)
SELECT sl.locker_id, sl.item_id, sl.locker_code 
FROM storage_lockers sl 
LEFT JOIN items i ON sl.item_id = i.item_id 
WHERE i.item_id IS NULL;

-- 4.3: Business State Consistency Check
-- Rule: Every item marked 'VERIFIED_RETURNED' must have a recorded release_date in storage_lockers
SELECT i.item_id, i.title, i.status, sl.locker_code, sl.release_date
FROM items i
INNER JOIN storage_lockers sl ON i.item_id = sl.item_id
WHERE i.status = 'VERIFIED_RETURNED' AND sl.release_date IS NULL;

-- 4.4: Range Validation Check
-- Rule: Ensure zero negative values or out-of-bounds scores exist in the database
SELECT item_id, title, reward_or_value 
FROM items 
WHERE reward_or_value < 0.00;

SELECT claim_id, claimant_name, confidence_score 
FROM claims 
WHERE confidence_score < 0.00 OR confidence_score > 100.00;

-- 4.5: Final Audit Log Completeness Check
-- Count logged actions by operation type to verify audit trail coverage
SELECT 
    action_type,
    COUNT(*) AS total_logged_events,
    MIN(performed_at) AS first_event_time,
    MAX(performed_at) AS latest_event_time
FROM audit_actions
GROUP BY action_type;
