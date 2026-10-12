-- ====================================================================
-- LOST AND FOUND MANAGEMENT SYSTEM — PHASE 3 SQL QUERIES
-- Course: Advanced Database Management Systems (ADBMS)
-- Target: CLO2 & CLO3 (Data Querying, Analytical Operations & Advanced SQL)
-- Database Engine: MySQL / MariaDB (Compatible with SQLite)
-- Campus Policy: 100% Free Campus Service (No Custody/Storage Fees)
-- ====================================================================

USE lost_found_db;

-- ====================================================================
-- PART 1: JOINS TO COMBINE MULTIPLE TABLES (CLO2, CLO3)
-- ====================================================================

-- 1.1: INNER JOIN (Items with Category Taxonomy and Campus Locations)
-- Purpose: Produces complete inventory details with building and category descriptions.
SELECT 
    i.item_id,
    i.title AS item_name,
    i.item_type,
    c.category_name,
    l.building_name,
    l.room_area,
    l.recovery_desk,
    i.status,
    i.reward_or_value AS estimated_value
FROM items i
INNER JOIN categories c ON i.category_id = c.category_id
INNER JOIN locations l ON i.location_id = l.location_id
ORDER BY i.item_id ASC;

-- 1.2: LEFT OUTER JOIN (All Items and their Associated Verification Claims)
-- Purpose: Shows every inventory item, including items that have zero submitted claims.
SELECT 
    i.item_id,
    i.title AS item_name,
    i.item_type,
    i.status AS item_status,
    COALESCE(c.claim_id, 0) AS claim_id,
    COALESCE(c.claimant_name, 'NO CLAIM SUBMITTED') AS claimant,
    COALESCE(c.claim_status, 'N/A') AS claim_status,
    COALESCE(c.confidence_score, 0.00) AS match_score
FROM items i
LEFT JOIN claims c ON i.item_id = c.item_id
ORDER BY i.item_id ASC, c.claim_id ASC;

-- 1.3: MULTI-TABLE 4-WAY JOIN (Comprehensive Claim Verification Dossier)
-- Purpose: Unifies claimant user profile, claimed item, category taxonomy, and verifier user.
SELECT 
    cl.claim_id,
    cl.claim_status,
    cl.confidence_score,
    u_claimant.full_name AS claimant_name,
    u_claimant.email AS claimant_email,
    i.title AS claimed_item_title,
    cat.category_name,
    loc.building_name AS discovery_building,
    COALESCE(u_verifier.full_name, 'AWAITING VERIFIER') AS verified_by_staff,
    DATE_FORMAT(cl.submitted_at, '%Y-%m-%d %H:%i') AS queued_time
FROM claims cl
INNER JOIN items i ON cl.item_id = i.item_id
INNER JOIN categories cat ON i.category_id = cat.category_id
INNER JOIN locations loc ON i.location_id = loc.location_id
INNER JOIN users u_claimant ON cl.claimant_user_id = u_claimant.user_id
LEFT JOIN users u_verifier ON cl.verified_by_user_id = u_verifier.user_id
ORDER BY cl.submitted_at ASC;

-- 1.4: SELF-JOIN / PAIRWISE MATCHING (Automated Lost & Found Match Candidate Detector)
-- Purpose: Pairs reported LOST items with reported FOUND items in the same category and building.
SELECT 
    lost_item.item_id AS lost_id,
    lost_item.title AS lost_item_title,
    lost_item.reporter_name AS lost_reporter,
    found_item.item_id AS found_id,
    found_item.title AS found_item_title,
    found_item.reporter_name AS finder_custodian,
    cat.category_name,
    loc.building_name AS common_building
FROM items lost_item
INNER JOIN items found_item 
    ON lost_item.category_id = found_item.category_id 
    AND lost_item.location_id = found_item.location_id
INNER JOIN categories cat ON lost_item.category_id = cat.category_id
INNER JOIN locations loc ON lost_item.location_id = loc.location_id
WHERE lost_item.item_type = 'LOST' 
  AND found_item.item_type = 'FOUND'
  AND lost_item.status = 'REPORTED'
  AND found_item.status = 'IN_CUSTODY';


-- ====================================================================
-- PART 2: NESTED QUERIES AND SUBQUERIES (CLO2, CLO3)
-- ====================================================================

-- 2.1: SCALAR SUBQUERY in WHERE Clause
-- Purpose: Find all items whose estimated value is strictly greater than the overall inventory average.
SELECT 
    item_id,
    title,
    category,
    reward_or_value,
    (SELECT ROUND(AVG(reward_or_value), 2) FROM items) AS campus_average_value,
    ROUND(reward_or_value - (SELECT AVG(reward_or_value) FROM items), 2) AS value_above_average
FROM items
WHERE reward_or_value > (SELECT AVG(reward_or_value) FROM items)
ORDER BY reward_or_value DESC;

-- 2.2: SUBQUERY WITH `IN` OPERATOR
-- Purpose: Identify registered campus users who currently have active PENDING claims in queue.
SELECT 
    user_id,
    full_name,
    email,
    phone,
    role
FROM users
WHERE user_id IN (
    SELECT DISTINCT claimant_user_id 
    FROM claims 
    WHERE claim_status = 'PENDING' AND claimant_user_id IS NOT NULL
);

-- 2.3: SUBQUERY WITH `NOT IN` OPERATOR
-- Purpose: Find categories under which no items are currently held in custody.
SELECT 
    category_id,
    category_name,
    description
FROM categories
WHERE category_id NOT IN (
    SELECT DISTINCT category_id 
    FROM items 
    WHERE status = 'IN_CUSTODY' AND category_id IS NOT NULL
);

-- 2.4: CORRELATED SUBQUERY WITH `EXISTS` OPERATOR
-- Purpose: Retrieve found items currently in custody that have at least one claim submitted for them.
SELECT 
    i.item_id,
    i.title,
    i.category,
    i.location,
    i.status
FROM items i
WHERE i.item_type = 'FOUND'
  AND i.status = 'IN_CUSTODY'
  AND EXISTS (
      SELECT 1 
      FROM claims c 
      WHERE c.item_id = i.item_id
  );

-- 2.5: CORRELATED SUBQUERY WITH `NOT EXISTS` OPERATOR
-- Purpose: Find found items currently in custody that have NO claims submitted yet (unclaimed assets).
SELECT 
    i.item_id,
    i.title,
    i.category,
    i.location,
    i.status
FROM items i
WHERE i.item_type = 'FOUND'
  AND i.status = 'IN_CUSTODY'
  AND NOT EXISTS (
      SELECT 1 
      FROM claims c 
      WHERE c.item_id = i.item_id
  );

-- 2.6: SUBQUERY IN `FROM` CLAUSE (Derived Table / Inline View)
-- Purpose: Calculate category statistics and filter only categories holding total value exceeding ₹2,000.
SELECT 
    cat_stats.category_name,
    cat_stats.item_count,
    cat_stats.total_valuation,
    cat_stats.average_valuation
FROM (
    SELECT 
        c.category_name,
        COUNT(i.item_id) AS item_count,
        ROUND(SUM(i.reward_or_value), 2) AS total_valuation,
        ROUND(AVG(i.reward_or_value), 2) AS average_valuation
    FROM categories c
    INNER JOIN items i ON c.category_id = i.category_id
    GROUP BY c.category_id, c.category_name
) AS cat_stats
WHERE cat_stats.total_valuation > 2000.00
ORDER BY cat_stats.total_valuation DESC;


-- ====================================================================
-- PART 3: CREATING VIEWS FOR REUSABLE QUERIES (CLO3)
-- ====================================================================

-- 3.1: VIEW `v_active_found_inventory`
-- Purpose: Clean public front-desk view showing all found items held in secure custody with locker IDs.
CREATE OR REPLACE VIEW v_active_found_inventory AS
SELECT 
    i.item_id,
    i.title,
    c.category_name,
    l.building_name,
    l.room_area,
    l.recovery_desk,
    sl.locker_code,
    sl.custody_start_date,
    i.reporter_name AS handed_over_by,
    DATE_FORMAT(i.reported_date, '%Y-%m-%d') AS date_reported
FROM items i
INNER JOIN categories c ON i.category_id = c.category_id
INNER JOIN locations l ON i.location_id = l.location_id
LEFT JOIN storage_lockers sl ON i.item_id = sl.item_id
WHERE i.item_type = 'FOUND' AND i.status = 'IN_CUSTODY';

-- Query View 3.1:
SELECT * FROM v_active_found_inventory;


-- 3.2: VIEW `v_claim_verification_queue`
-- Purpose: Administrative FIFO queue prioritizing PENDING claims with claimant profiles.
CREATE OR REPLACE VIEW v_claim_verification_queue AS
SELECT 
    cl.claim_id,
    cl.item_id,
    i.title AS claimed_item,
    c.category_name,
    cl.claimant_name,
    cl.claimant_contact,
    cl.proof_description,
    cl.confidence_score,
    cl.claim_status,
    DATE_FORMAT(cl.submitted_at, '%Y-%m-%d %H:%i') AS submission_time
FROM claims cl
INNER JOIN items i ON cl.item_id = i.item_id
INNER JOIN categories c ON i.category_id = c.category_id
WHERE cl.claim_status = 'PENDING'
ORDER BY cl.submitted_at ASC;

-- Query View 3.2:
SELECT * FROM v_claim_verification_queue;


-- 3.3: VIEW `v_category_analytics`
-- Purpose: Management reporting dashboard showing category distribution, total value, and return rates.
CREATE OR REPLACE VIEW v_category_analytics AS
SELECT 
    c.category_name,
    COUNT(i.item_id) AS total_items,
    SUM(CASE WHEN i.item_type = 'FOUND' THEN 1 ELSE 0 END) AS found_count,
    SUM(CASE WHEN i.item_type = 'LOST' THEN 1 ELSE 0 END) AS lost_count,
    SUM(CASE WHEN i.status = 'VERIFIED_RETURNED' THEN 1 ELSE 0 END) AS returned_count,
    ROUND(SUM(i.reward_or_value), 2) AS total_declared_value,
    ROUND(AVG(i.reward_or_value), 2) AS avg_item_value
FROM categories c
LEFT JOIN items i ON c.category_id = i.category_id
GROUP BY c.category_id, c.category_name;

-- Query View 3.3:
SELECT * FROM v_category_analytics;


-- ====================================================================
-- PART 4: UNDERSTANDING BASIC QUERY EXECUTION BEHAVIOR (EXPLAIN)
-- ====================================================================

-- 4.1: EXPLAIN on Index Lookup (Fast ref / range scan via idx_status)
EXPLAIN SELECT item_id, title, status, reward_or_value 
FROM items 
WHERE status = 'IN_CUSTODY';

-- 4.2: EXPLAIN on Multi-Table Join with Index Keys
EXPLAIN SELECT 
    i.item_id, i.title, c.category_name, l.building_name
FROM items i
INNER JOIN categories c ON i.category_id = c.category_id
INNER JOIN locations l ON i.location_id = l.location_id
WHERE i.status = 'IN_CUSTODY';

-- 4.3: EXPLAIN on Full Table Scan (Unindexed column search with LIKE)
EXPLAIN SELECT item_id, title, description 
FROM items 
WHERE description LIKE '%backpack%';


-- ====================================================================
-- PART 5: IMPLEMENTING FUNCTIONS AND STORED PROCEDURES (CLO3)
-- ====================================================================

-- 5.1: STORED FUNCTION `fn_custody_duration_days`
-- Purpose: Computes days elapsed between custody receipt and today (or release date).
DELIMITER $$
DROP FUNCTION IF EXISTS fn_custody_duration_days $$
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

-- Test Function 5.1:
SELECT 
    locker_code,
    item_id,
    custody_start_date,
    release_date,
    fn_custody_duration_days(custody_start_date, release_date) AS days_in_custody
FROM storage_lockers;


-- 5.2: STORED PROCEDURE `sp_register_found_item`
-- Purpose: Atomically registers a found item and automatically reserves a storage locker.
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_register_found_item $$
CREATE PROCEDURE sp_register_found_item(
    IN p_reporter_user_id INT,
    IN p_category_id INT,
    IN p_location_id INT,
    IN p_title VARCHAR(150),
    IN p_description TEXT,
    IN p_reporter_name VARCHAR(100),
    IN p_reporter_contact VARCHAR(50),
    IN p_reward_or_value DECIMAL(10,2),
    IN p_locker_code VARCHAR(20),
    OUT p_new_item_id INT
)
BEGIN
    DECLARE v_category_name VARCHAR(50);
    DECLARE v_location_name VARCHAR(100);

    -- Fetch taxonomy text representations for backward compatibility
    SELECT category_name INTO v_category_name FROM categories WHERE category_id = p_category_id;
    SELECT building_name INTO v_location_name FROM locations WHERE location_id = p_location_id;

    -- Step 1: Insert item
    INSERT INTO items (
        reported_by_user_id, category_id, location_id, title, category, description,
        item_type, location, status, reporter_name, reporter_contact,
        reward_or_value, reported_date, updated_at
    ) VALUES (
        p_reporter_user_id, p_category_id, p_location_id, p_title, v_category_name, p_description,
        'FOUND', v_location_name, 'IN_CUSTODY', p_reporter_name, p_reporter_contact,
        p_reward_or_value, NOW(), NOW()
    );

    SET p_new_item_id = LAST_INSERT_ID();

    -- Step 2: Allocate custody locker box
    INSERT INTO storage_lockers (item_id, locker_code, custody_start_date, release_date, remarks)
    VALUES (p_new_item_id, p_locker_code, CURRENT_DATE(), NULL, 'Secured in campus recovery locker');

    -- Step 3: Record initial audit entry
    INSERT INTO audit_actions (item_id, performed_by_user_id, action_type, snapshot_before, snapshot_after, performed_at)
    VALUES (
        p_new_item_id, p_reporter_user_id, 'ITEM_REGISTRATION',
        NULL, JSON_OBJECT('status', 'IN_CUSTODY', 'locker', p_locker_code), NOW()
    );
END $$
DELIMITER ;


-- 5.3: STORED PROCEDURE `sp_process_claim_verification`
-- Purpose: Atomically updates claim status, transitions item lifecycle, and releases custody locker.
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_process_claim_verification $$
CREATE PROCEDURE sp_process_claim_verification(
    IN p_claim_id INT,
    IN p_verifier_user_id INT,
    IN p_decision ENUM('APPROVED', 'REJECTED'),
    IN p_confidence_score DECIMAL(5,2),
    OUT p_result_message VARCHAR(100)
)
BEGIN
    DECLARE v_item_id INT;
    DECLARE v_current_status VARCHAR(50);

    -- Find target claim
    SELECT item_id INTO v_item_id FROM claims WHERE claim_id = p_claim_id;

    IF v_item_id IS NULL THEN
        SET p_result_message = 'ERROR: Claim ID not found';
    ELSE
        -- Update claim outcome
        UPDATE claims 
        SET claim_status = p_decision,
            confidence_score = p_confidence_score,
            verified_by_user_id = p_verifier_user_id
        WHERE claim_id = p_claim_id;

        IF p_decision = 'APPROVED' THEN
            -- Update item status to returned
            UPDATE items 
            SET status = 'VERIFIED_RETURNED', updated_at = NOW() 
            WHERE item_id = v_item_id;

            -- Release locker box
            UPDATE storage_lockers 
            SET release_date = CURRENT_DATE(), remarks = 'Claim verified and returned to student'
            WHERE item_id = v_item_id AND release_date IS NULL;

            -- Audit action
            INSERT INTO audit_actions (item_id, performed_by_user_id, action_type, snapshot_before, snapshot_after, performed_at)
            VALUES (
                v_item_id, p_verifier_user_id, 'CLAIM_APPROVAL',
                JSON_OBJECT('status', 'IN_CUSTODY'), JSON_OBJECT('status', 'VERIFIED_RETURNED'), NOW()
            );

            SET p_result_message = 'SUCCESS: Claim approved, item returned, locker released';
        ELSE
            SET p_result_message = 'NOTICE: Claim rejected; item remains in custody';
        END IF;
    END IF;
END $$
DELIMITER ;
