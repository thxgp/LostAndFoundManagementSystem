-- ====================================================================
-- Lost and Found Management System - Phase 2 Queries (CLO2)
-- Campus Policy: 100% Free Service (No Custody / Storage Fees)
-- ====================================================================

USE lost_found_db;

-- ====================================================================
-- 1. Basic Filtering (SELECT with WHERE)
-- ====================================================================

-- 1.1: Retrieve all items currently in campus custody with dates
SELECT item_id, title, category, location, status, reporter_name, reward_or_value, DATE_FORMAT(reported_date, '%Y-%m-%d %H:%i') AS reported_on
FROM items
WHERE status = 'IN_CUSTODY'
ORDER BY reported_date DESC;

-- 1.2: Filter high-value items (Value >= ₹5,000)
SELECT item_id, title, category, reward_or_value, location, DATE_FORMAT(reported_date, '%Y-%m-%d') AS reported_date
FROM items
WHERE reward_or_value >= 5000.00
ORDER BY reward_or_value DESC;

-- 1.3: Retrieve all PENDING claims waiting in the verification queue
SELECT claim_id, item_id, claimant_name, claimant_contact, proof_description, confidence_score, claim_status, DATE_FORMAT(submitted_at, '%Y-%m-%d %H:%i') AS submitted_time
FROM claims
WHERE claim_status = 'PENDING';

-- ====================================================================
-- 2. Sorting Queries (ORDER BY)
-- ====================================================================

-- 2.1: Sort inventory by value in descending order (Highest to Lowest)
SELECT item_id, title, category, item_type, reward_or_value, DATE_FORMAT(reported_date, '%Y-%m-%d') AS reported_date
FROM items
ORDER BY reward_or_value DESC;

-- 2.2: Sort items by report date (Chronological timeline)
SELECT item_id, title, item_type, location, reported_date
FROM items
ORDER BY reported_date ASC;

-- ====================================================================
-- 3. Data Cleaning & NULL Value Handling (Free Campus Facility)
-- ====================================================================

-- 3.1: Custody Locker status with COALESCE for active vs. released items (No fees)
SELECT 
    locker_code,
    item_id,
    custody_start_date,
    COALESCE(release_date, 'STILL IN CUSTODY') AS return_status,
    remarks
FROM storage_lockers;

-- ====================================================================
-- 4. Aggregate Functions for Data Summaries (CLO2)
-- ====================================================================

-- 4.1: Overall Inventory Statistical Summary (COUNT, SUM, AVG, MAX, MIN)
SELECT 
    COUNT(*) AS total_items_logged,
    SUM(reward_or_value) AS total_declared_value_inr,
    ROUND(AVG(reward_or_value), 2) AS average_item_value_inr,
    MAX(reward_or_value) AS most_expensive_item_value,
    MIN(reward_or_value) AS least_expensive_item_value
FROM items;

-- 4.2: Category Breakdown (GROUP BY + COUNT + AVG)
SELECT 
    category,
    COUNT(*) AS items_count,
    ROUND(AVG(reward_or_value), 2) AS avg_category_value,
    SUM(reward_or_value) AS total_category_worth
FROM items
GROUP BY category
ORDER BY items_count DESC;

-- 4.3: Claims Pipeline Summary by Verification Status
SELECT 
    claim_status,
    COUNT(*) AS total_claims,
    ROUND(AVG(confidence_score), 2) AS avg_match_confidence
FROM claims
GROUP BY claim_status;
