-- ====================================================================
-- Lost and Found Management System - MySQL Database Schema (ADBMS)
-- Database: lost_found_db
-- Target: CLO1 & CLO2 (3NF Schema, DDL, DML, Constraints & Queries)
-- Campus Policy: 100% Free College Service (No Custody/Storage Fees)
-- ====================================================================

-- Clean Reset: Drop and recreate database to prevent duplicate key errors (1062)
DROP DATABASE IF EXISTS lost_found_db;
CREATE DATABASE lost_found_db;
USE lost_found_db;

-- ====================================================================
-- 1. Table Definitions (DDL)
-- ====================================================================

-- 1. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    role ENUM('STUDENT', 'STAFF', 'ADMIN', 'CUSTODIAN') DEFAULT 'STUDENT',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Categories Table (Free Institutional Taxonomy)
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Locations Table
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    building_name VARCHAR(100) NOT NULL,
    room_area VARCHAR(100) NOT NULL,
    recovery_desk VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Items Table (Core Lost & Found Inventory)
CREATE TABLE items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    reported_by_user_id INT DEFAULT NULL,
    category_id INT DEFAULT NULL,
    location_id INT DEFAULT NULL,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    item_type ENUM('LOST', 'FOUND') NOT NULL,
    location VARCHAR(100) NOT NULL,
    status ENUM('REPORTED', 'IN_CUSTODY', 'CLAIM_PENDING', 'VERIFIED_RETURNED', 'DISPOSED') DEFAULT 'REPORTED',
    reporter_name VARCHAR(100) NOT NULL,
    reporter_contact VARCHAR(50) NOT NULL,
    reward_or_value DECIMAL(10, 2) DEFAULT 0.00,
    reported_date DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_item_type (item_type),
    CONSTRAINT fk_items_user FOREIGN KEY (reported_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_items_cat FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    CONSTRAINT fk_items_loc FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Claims Table (FIFO Verification Queue)
CREATE TABLE claims (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    claimant_user_id INT DEFAULT NULL,
    claimant_name VARCHAR(100) NOT NULL,
    claimant_contact VARCHAR(50) NOT NULL,
    proof_description TEXT NOT NULL,
    confidence_score DECIMAL(5, 2) DEFAULT 0.00,
    claim_status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    submitted_at DATETIME NOT NULL,
    verified_by_user_id INT DEFAULT NULL,
    CONSTRAINT fk_claims_item FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    CONSTRAINT fk_claims_user FOREIGN KEY (claimant_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_claims_verifier FOREIGN KEY (verified_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_claim_status (claim_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Audit Actions Table (LIFO Action History)
CREATE TABLE audit_actions (
    action_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT DEFAULT NULL,
    performed_by_user_id INT DEFAULT NULL,
    action_type VARCHAR(50) NOT NULL,
    snapshot_before JSON,
    snapshot_after JSON,
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_item FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE SET NULL,
    CONSTRAINT fk_audit_user FOREIGN KEY (performed_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Storage Lockers Table (Physical Security Storage - No Fee Charged)
CREATE TABLE storage_lockers (
    locker_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    locker_code VARCHAR(20) NOT NULL,
    custody_start_date DATE NOT NULL,
    release_date DATE DEFAULT NULL,
    remarks VARCHAR(100) DEFAULT 'Secured in campus recovery locker',
    CONSTRAINT fk_locker_item FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- 2. Seed Data Insertion (DML with Realistic Spread-Out Dates)
-- ====================================================================

-- Users
INSERT IGNORE INTO users (full_name, email, phone, role) VALUES
('Aarav Sharma', 'aarav.sharma@campus.edu', '+91 9876543210', 'STUDENT'),
('Priya Patel', 'priya.patel@campus.edu', '+91 9876543211', 'STUDENT'),
('Security Desk Alpha', 'security.alpha@campus.edu', '+91 9876543212', 'CUSTODIAN'),
('Dr. Ramesh Rao', 'ramesh.rao@campus.edu', '+91 9876543213', 'STAFF');

-- Categories (No fees)
INSERT IGNORE INTO categories (category_name, description) VALUES
('Electronics', 'Laptops, phones, headphones, chargers'),
('Documents/Cards', 'ID cards, licenses, passports, files'),
('Keys/Wallets', 'House keys, vehicle keys, wallets, purses'),
('Bags/Backpacks', 'Knapsacks, laptop bags, luggage'),
('Clothing/Apparel', 'Jackets, hoodies, caps, umbrellas'),
('Others', 'Miscellaneous general items');

-- Locations
INSERT IGNORE INTO locations (building_name, room_area, recovery_desk) VALUES
('Central Library', '2nd Floor Quiet Zone', 'Library Helpdesk Floor 1'),
('Student Cafeteria', 'Block C Dining Area', 'Campus Facility Office'),
('Computer Science Block', 'Lab 304', 'CS Dept Office'),
('Auditorium', 'Main Gate Entrance', 'Security Gate 1');

-- Items with Realistic Distinct Dates
INSERT IGNORE INTO items (reported_by_user_id, category_id, location_id, title, category, description, item_type, location, status, reporter_name, reporter_contact, reward_or_value, reported_date, updated_at) VALUES
(1, 1, 1, 'MacBook Pro 14 M2 Space Gray', 'Electronics', 'Left in Library 2nd floor silent study area, has sticker "Code is Poetry".', 'FOUND', 'Central Library 2nd Floor', 'IN_CUSTODY', 'Aarav Sharma', 'aarav.sharma@campus.edu', 125000.00, '2026-09-02 10:15:00', '2026-09-02 10:30:00'),
(2, 3, 2, 'Leather Bifold Wallet with ID Cards', 'Keys/Wallets', 'Brown fossil wallet containing student ID and campus meal card.', 'FOUND', 'Student Cafeteria Block C', 'IN_CUSTODY', 'Priya Patel', 'priya.patel@campus.edu', 2500.00, '2026-09-08 13:45:00', '2026-09-08 14:00:00'),
(4, 1, 3, 'Sony WH-1000XM5 Headphones', 'Electronics', 'Black noise cancelling headphones in black zipper carrying case.', 'LOST', 'Computer Science Lab 304', 'REPORTED', 'Dr. Ramesh Rao', 'ramesh.rao@campus.edu', 28000.00, '2026-09-14 16:20:00', '2026-09-14 16:20:00'),
(3, 2, 4, 'Campus Identity Card & Access Badge', 'Documents/Cards', 'Student ID card for Department of AI & Data Science.', 'FOUND', 'Auditorium Main Gate', 'CLAIM_PENDING', 'Security Desk Alpha', 'security.alpha@campus.edu', 500.00, '2026-09-19 11:10:00', '2026-09-20 09:15:00'),
(1, 5, 1, 'Blue Hydro Flask Water Bottle', 'Clothing/Apparel', 'Stainless steel bottle with university logo.', 'FOUND', 'Central Library 2nd Floor', 'IN_CUSTODY', 'Aarav Sharma', 'aarav.sharma@campus.edu', 1800.00, '2026-09-22 15:30:00', '2026-09-22 15:30:00'),
(2, 1, 3, 'Scientific Calculator FX-991EX', 'Electronics', 'Black Casio scientific calculator left in lab.', 'LOST', 'Computer Science Lab 304', 'REPORTED', 'Rohan Deshmukh', 'rohan@campus.edu', 1500.00, '2026-09-24 17:00:00', '2026-09-24 17:00:00');

-- Claims with Distinct Dates & All Statuses (APPROVED, REJECTED, PENDING)
INSERT IGNORE INTO claims (item_id, claimant_user_id, claimant_name, claimant_contact, proof_description, confidence_score, claim_status, submitted_at) VALUES
(1, 1, 'Aarav Sharma', 'aarav.sharma@campus.edu', 'Apple ID matches aarav.sharma@campus.edu, serial ends in 9942', 95.00, 'APPROVED', '2026-09-03 14:20:00'),
(4, 2, 'Priya Patel', 'priya.patel@campus.edu', 'Card belongs to my classmate, Department AI & DS', 40.00, 'REJECTED', '2026-09-21 16:00:00'),
(4, 1, 'Ananya Iyer', 'ananya.iyer@campus.edu', 'Access badge card number matches 26MCC042 with photo ID', 92.00, 'PENDING', '2026-09-24 11:30:00');

-- Storage Lockers (No Custody Fee - 100% Free College Facility)
INSERT IGNORE INTO storage_lockers (item_id, locker_code, custody_start_date, release_date, remarks) VALUES
(1, 'LOCKER-A101', '2026-09-02', '2026-09-04', 'Claim verified and returned to owner'),
(2, 'LOCKER-B204', '2026-09-08', NULL, 'Currently held in Cafeteria security desk locker'),
(4, 'LOCKER-C301', '2026-09-19', NULL, 'Held in Sports Complex security locker'),
(5, 'LOCKER-A102', '2026-09-22', NULL, 'Stored in Central Library safe locker');

-- ====================================================================
-- 3. Phase 2 Verification & Summary Queries (CLO2)
-- ====================================================================

-- Query 1: Filter all active inventory currently IN_CUSTODY with realistic dates
SELECT item_id, title, category, location, status, reward_or_value, DATE_FORMAT(reported_date, '%Y-%m-%d') AS reported_on
FROM items 
WHERE status = 'IN_CUSTODY'
ORDER BY reported_date DESC;

-- Query 2: Overall inventory summary
SELECT 
    COUNT(*) AS total_items,
    SUM(reward_or_value) AS total_declared_value,
    ROUND(AVG(reward_or_value), 2) AS average_item_value,
    MAX(reward_or_value) AS highest_value,
    MIN(reward_or_value) AS lowest_value
FROM items;

-- Query 3: Category breakdown
SELECT 
    category,
    COUNT(*) AS item_count,
    ROUND(AVG(reward_or_value), 2) AS avg_value,
    SUM(reward_or_value) AS total_category_val
FROM items
GROUP BY category
ORDER BY item_count DESC;

-- Query 4: Claims verification queue showing PENDING claims
SELECT claim_id, item_id, claimant_name, proof_description, confidence_score, claim_status, DATE_FORMAT(submitted_at, '%Y-%m-%d') AS claim_date
FROM claims
WHERE claim_status = 'PENDING';

-- Query 5: Active lockers showing NULL handling (without fees)
SELECT 
    locker_code,
    item_id,
    custody_start_date,
    COALESCE(release_date, 'STILL IN CUSTODY') AS status,
    remarks
FROM storage_lockers;
