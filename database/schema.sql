-- ====================================================================
-- Lost and Found Management System - MySQL Database Schema (ADBMS)
-- Database: lost_found_db
-- ====================================================================

CREATE DATABASE IF NOT EXISTS lost_found_db;
USE lost_found_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    role ENUM('STUDENT', 'STAFF', 'ADMIN', 'CUSTODIAN') DEFAULT 'STUDENT',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(200),
    daily_storage_rate DECIMAL(6, 2) DEFAULT 2.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Locations Table
CREATE TABLE IF NOT EXISTS locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    building_name VARCHAR(100) NOT NULL,
    room_area VARCHAR(100) NOT NULL,
    recovery_desk VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Items Table (Core Lost & Found Inventory)
CREATE TABLE IF NOT EXISTS items (
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
    reported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_item_type (item_type),
    CONSTRAINT fk_items_user FOREIGN KEY (reported_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_items_cat FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    CONSTRAINT fk_items_loc FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Claims Table (FIFO Verification Queue)
CREATE TABLE IF NOT EXISTS claims (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    claimant_user_id INT DEFAULT NULL,
    claimant_name VARCHAR(100) NOT NULL,
    claimant_contact VARCHAR(50) NOT NULL,
    proof_description TEXT NOT NULL,
    confidence_score DECIMAL(5, 2) DEFAULT 0.00,
    claim_status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_by_user_id INT DEFAULT NULL,
    CONSTRAINT fk_claims_item FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    CONSTRAINT fk_claims_user FOREIGN KEY (claimant_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_claims_verifier FOREIGN KEY (verified_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_claim_status (claim_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Audit Actions / Logs Table (LIFO Undo Stack History)
CREATE TABLE IF NOT EXISTS audit_actions (
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

-- 7. Storage Lockers Table (Physical Custody Allocation)
CREATE TABLE IF NOT EXISTS storage_lockers (
    locker_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    locker_code VARCHAR(20) NOT NULL,
    custody_start_date DATE NOT NULL,
    release_date DATE DEFAULT NULL,
    total_custody_fee DECIMAL(8, 2) DEFAULT 0.00,
    CONSTRAINT fk_locker_item FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- Sample Seed Data
-- ====================================================================

INSERT INTO users (full_name, email, phone, role) VALUES
('Aarav Sharma', 'aarav.sharma@campus.edu', '+91 9876543210', 'STUDENT'),
('Priya Patel', 'priya.patel@campus.edu', '+91 9876543211', 'STUDENT'),
('Security Desk Alpha', 'security.alpha@campus.edu', '+91 9876543212', 'CUSTODIAN'),
('Dr. Ramesh Rao', 'ramesh.rao@campus.edu', '+91 9876543213', 'STAFF');

INSERT INTO categories (category_name, description, daily_storage_rate) VALUES
('Electronics', 'Laptops, phones, headphones, chargers', 5.00),
('Documents/Cards', 'ID cards, licenses, passports, files', 1.00),
('Keys/Wallets', 'House keys, vehicle keys, wallets, purses', 2.00),
('Bags/Backpacks', 'Knapsacks, laptop bags, luggage', 3.00),
('Clothing/Apparel', 'Jackets, hoodies, caps, umbrellas', 1.50),
('Others', 'Miscellaneous general items', 2.00);

INSERT INTO locations (building_name, room_area, recovery_desk) VALUES
('Central Library', '2nd Floor Quiet Zone', 'Library Helpdesk Floor 1'),
('Student Cafeteria', 'Block C Dining Area', 'Campus Facility Office'),
('Computer Science Block', 'Lab 304', 'CS Dept Office'),
('Auditorium', 'Main Gate Entrance', 'Security Gate 1');
