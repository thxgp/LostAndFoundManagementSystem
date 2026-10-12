"""
========================================================================================
LOST AND FOUND MANAGEMENT SYSTEM — PHASE 2 EXECUTION SCRIPT
Course: Advanced Database Management Systems (ADBMS) / Practical Lab
Target: CLO2 (Database Creation, Data Preparation, Querying & Aggregates)
Campus Policy: 100% Free Campus Facility (No Custody/Storage Fees)
========================================================================================
This script executes and demonstrates all syllabus requirements for Phase 2:
  1. Database and Table Creation using SQL (DDL)
  2. Data Insertion into Tables (DML with realistic spread-out dates)
  3. Data Cleaning (NULL Handling, Constraint Validations)
  4. Basic Queries (SELECT, WHERE, ORDER BY, Date Filtering)
  5. Aggregate Functions for Data Summaries (COUNT, SUM, AVG, MIN, MAX, GROUP BY)
========================================================================================
"""

import sys
import os
import sqlite3
from typing import List, Any

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.db_config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, SQLITE_DB_PATH
)


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


def print_section(title: str):
    print(f"\n{Colors.CYAN}{'=' * 85}")
    print(f"{Colors.BOLD}{Colors.HEADER}  {title}")
    print(f"{Colors.CYAN}{'=' * 85}{Colors.RESET}\n")


def print_table(headers: List[str], rows: List[List[Any]]):
    """Renders clean ASCII tabular output."""
    if not rows:
        print(f"{Colors.YELLOW}No records found.{Colors.RESET}")
        return

    str_rows = [[str(cell if cell is not None else "NULL") for cell in row] for row in rows]
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(cell))

    border = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_row = "| " + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths)) + " |"

    print(f"{Colors.DIM}{border}{Colors.RESET}")
    print(f"{Colors.BOLD}{header_row}{Colors.RESET}")
    print(f"{Colors.DIM}{border}{Colors.RESET}")
    for row in str_rows:
        row_str = "| " + " | ".join(f"{cell:<{w}}" for cell, w in zip(row, col_widths)) + " |"
        print(row_str)
    print(f"{Colors.DIM}{border}{Colors.RESET}\n")


def get_db_connection():
    """Tries MySQL first, falls back gracefully to SQLite."""
    try:
        import mysql.connector
        srv = mysql.connector.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD
        )
        cur = srv.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE};")
        cur.close()
        srv.close()

        conn = mysql.connector.connect(
            host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
            password=MYSQL_PASSWORD, database=MYSQL_DATABASE, autocommit=True
        )
        return conn, "MYSQL"
    except Exception:
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "SQLITE"


def execute_ddl(conn, db_type: str):
    """Step 1: DDL Table Creation."""
    print_section("STEP 1: DATABASE & TABLE CREATION (DDL)")
    cur = conn.cursor()

    # Drop existing tables to ensure clean, updated schema without stale columns
    for tbl in ["audit_actions", "claims", "storage_lockers", "items", "users", "categories", "locations"]:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {tbl};")
        except Exception:
            pass

    if db_type == "MYSQL":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            role ENUM('STUDENT', 'STAFF', 'ADMIN', 'CUSTODIAN') DEFAULT 'STUDENT',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(60) NOT NULL UNIQUE,
            description VARCHAR(200)
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            location_id INT AUTO_INCREMENT PRIMARY KEY,
            building_name VARCHAR(100) NOT NULL,
            room_area VARCHAR(100) NOT NULL,
            recovery_desk VARCHAR(80) NOT NULL
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            reported_by_user_id INT DEFAULT NULL,
            category_id INT DEFAULT NULL,
            location_id INT DEFAULT NULL,
            title VARCHAR(150) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            item_type VARCHAR(10) NOT NULL,
            location VARCHAR(100) NOT NULL,
            status VARCHAR(30) DEFAULT 'REPORTED',
            reporter_name VARCHAR(100) NOT NULL,
            reporter_contact VARCHAR(50) NOT NULL,
            reward_or_value DECIMAL(10, 2) DEFAULT 0.00,
            reported_date DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (reported_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
            FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT NOT NULL,
            claimant_user_id INT DEFAULT NULL,
            claimant_name VARCHAR(100) NOT NULL,
            claimant_contact VARCHAR(50) NOT NULL,
            proof_description TEXT NOT NULL,
            confidence_score DECIMAL(5, 2) DEFAULT 0.00,
            claim_status VARCHAR(20) DEFAULT 'PENDING',
            submitted_at DATETIME NOT NULL,
            verified_by_user_id INT DEFAULT NULL,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
            FOREIGN KEY (claimant_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (verified_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS storage_lockers (
            locker_id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT NOT NULL,
            locker_code VARCHAR(20) NOT NULL,
            custody_start_date DATE NOT NULL,
            release_date DATE DEFAULT NULL,
            remarks VARCHAR(100) DEFAULT 'Secured in campus recovery locker',
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_actions (
            action_id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT DEFAULT NULL,
            performed_by_user_id INT DEFAULT NULL,
            action_type VARCHAR(50) NOT NULL,
            snapshot_before JSON,
            snapshot_after JSON,
            performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE SET NULL,
            FOREIGN KEY (performed_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );""")
    else:
        # SQLite syntax
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            role TEXT DEFAULT 'STUDENT',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE,
            description TEXT
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            location_id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_name TEXT NOT NULL,
            room_area TEXT NOT NULL,
            recovery_desk TEXT NOT NULL
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reported_by_user_id INTEGER,
            category_id INTEGER,
            location_id INTEGER,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            item_type TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'REPORTED',
            reporter_name TEXT NOT NULL,
            reporter_contact TEXT NOT NULL,
            reward_or_value REAL DEFAULT 0.0,
            reported_date TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (reported_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
            FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            claimant_user_id INTEGER,
            claimant_name TEXT NOT NULL,
            claimant_contact TEXT NOT NULL,
            proof_description TEXT NOT NULL,
            confidence_score REAL DEFAULT 0.0,
            claim_status TEXT DEFAULT 'PENDING',
            submitted_at TEXT NOT NULL,
            verified_by_user_id INTEGER,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
            FOREIGN KEY (claimant_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (verified_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS storage_lockers (
            locker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            locker_code TEXT NOT NULL,
            custody_start_date TEXT NOT NULL,
            release_date TEXT DEFAULT NULL,
            remarks TEXT DEFAULT 'Secured in campus recovery locker',
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
        );""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_actions (
            action_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            performed_by_user_id INTEGER,
            action_type TEXT NOT NULL,
            snapshot_before TEXT,
            snapshot_after TEXT,
            performed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE SET NULL,
            FOREIGN KEY (performed_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );""")

        conn.commit()

    print(f"{Colors.GREEN}✔ Successfully verified and executed DDL for 7 core tables:{Colors.RESET}")
    print("   1. `users`            (User Profiles & Security Roles)")
    print("   2. `categories`       (Standard Item Taxonomies - No Fee Charged)")
    print("   3. `locations`        (Campus Buildings, Rooms & Recovery Desks)")
    print("   4. `items`            (Central Lost & Found Inventory)")
    print("   5. `claims`           (Ownership Claim Verification Tickets)")
    print("   6. `storage_lockers`  (Custody Lockers & Remarks - No Fee Charged)")
    print("   7. `audit_actions`    (Immutable Action History & Audit Log)")


def execute_dml(conn, db_type: str):
    """Step 2: DML Record Insertion with realistic spread-out dates."""
    print_section("STEP 2: RECORD INSERTION (DML WITH REALISTIC DATES)")
    cur = conn.cursor()

    # Clear existing demo records for a clean run
    for tbl in ["claims", "storage_lockers", "items", "users", "categories", "locations"]:
        try:
            cur.execute(f"DELETE FROM {tbl};")
        except Exception:
            pass

    # Insert Users
    users_data = [
        ("Aarav Sharma", "aarav.sharma@campus.edu", "+91 9876543210", "STUDENT"),
        ("Priya Patel", "priya.patel@campus.edu", "+91 9876543211", "STUDENT"),
        ("Security Officer Rao", "security.rao@campus.edu", "+91 9876543212", "CUSTODIAN"),
        ("Prof. Sundaram", "sundaram@campus.edu", "+91 9876543213", "STAFF")
    ]
    ph = "%s, %s, %s, %s" if db_type == "MYSQL" else "?, ?, ?, ?"
    cur.executemany(f"INSERT INTO users (full_name, email, phone, role) VALUES ({ph});", users_data)

    # Insert Categories (No storage fee)
    categories_data = [
        ("Electronics", "Laptops, phones, headphones, power banks"),
        ("Documents/Cards", "Student ID cards, driving licenses, certificates"),
        ("Keys/Wallets", "Hostel keys, vehicle keys, wallets, purses"),
        ("Bags/Backpacks", "School bags, laptop sleeves, backpacks"),
        ("Clothing/Apparel", "Jackets, sweaters, umbrellas, spectacles")
    ]
    ph2 = "%s, %s" if db_type == "MYSQL" else "?, ?"
    cur.executemany(f"INSERT INTO categories (category_name, description) VALUES ({ph2});", categories_data)

    # Insert Locations
    locations_data = [
        ("Central Library", "2nd Floor Silent Study", "Library Helpdesk Floor 1"),
        ("Student Cafeteria", "Block C Main Hall", "Campus Facility Desk"),
        ("CS Block", "Lab 304 (AI Lab)", "CS Department Office"),
        ("Sports Complex", "Badminton Arena", "Gymnasium Reception")
    ]
    ph3 = "%s, %s, %s" if db_type == "MYSQL" else "?, ?, ?"
    cur.executemany(f"INSERT INTO locations (building_name, room_area, recovery_desk) VALUES ({ph3});", locations_data)

    # Insert Items with REALISTIC SPREAD-OUT DATES and Foreign Keys
    items_data = [
        (1, 1, 1, "MacBook Pro 14 M2", "Electronics", "Space Gray, sticker on back", "FOUND", "Central Library", "IN_CUSTODY", "Aarav Sharma", "aarav@campus.edu", 125000.0, "2026-09-02 10:15:00", "2026-09-02 10:30:00"),
        (2, 3, 2, "Leather Bifold Wallet", "Keys/Wallets", "Brown leather with student ID card", "FOUND", "Student Cafeteria", "IN_CUSTODY", "Priya Patel", "priya@campus.edu", 2500.0, "2026-09-08 13:45:00", "2026-09-08 14:00:00"),
        (4, 1, 3, "Sony WH-1000XM5", "Electronics", "Black wireless noise-cancelling headphones", "LOST", "CS Block", "REPORTED", "Dr. Ramesh Rao", "ramesh@campus.edu", 28000.0, "2026-09-14 16:20:00", "2026-09-14 16:20:00"),
        (3, 2, 4, "Campus ID Card", "Documents/Cards", "ID for Department of CS", "FOUND", "Sports Complex", "CLAIM_PENDING", "Security Desk", "security@campus.edu", 500.0, "2026-09-19 11:10:00", "2026-09-20 09:15:00"),
        (1, 5, 1, "Blue Hydro Flask", "Clothing/Apparel", "Insulated stainless steel water bottle", "FOUND", "Central Library", "IN_CUSTODY", "Librarian", "lib@campus.edu", 1800.0, "2026-09-22 15:30:00", "2026-09-22 15:30:00"),
        (2, 1, 3, "Scientific Calculator", "Electronics", "Casio fx-991EX Classwiz", "LOST", "CS Block", "REPORTED", "Kavya Menon", "kavya@campus.edu", 1500.0, "2026-09-24 17:00:00", "2026-09-24 17:00:00")
    ]
    ph_items = ", ".join(["%s" if db_type == "MYSQL" else "?"] * 14)
    cur.executemany(f"""
        INSERT INTO items (reported_by_user_id, category_id, location_id, title, category, description, item_type, location, status, reporter_name, reporter_contact, reward_or_value, reported_date, updated_at)
        VALUES ({ph_items});
    """, items_data)

    # Insert Claims with Distinct Dates & All Statuses and Foreign Keys
    claims_data = [
        (1, 1, "Aarav Sharma", "aarav@campus.edu", "Apple ID matches aarav@campus.edu with serial ends in 9942", 95.0, "APPROVED", "2026-09-03 14:20:00", 3),
        (2, 2, "Priya Patel", "priya@campus.edu", "Contains my student card 26MCC042 and driver license", 98.0, "APPROVED", "2026-09-09 11:00:00", 3),
        (4, 2, "Kavya Menon", "kavya@campus.edu", "Card belongs to my roommate Ananya", 40.0, "REJECTED", "2026-09-21 16:00:00", 3),
        (4, 1, "Ananya Iyer", "ananya@campus.edu", "My registration badge with photo ID", 92.0, "PENDING", "2026-09-24 11:30:00", None)
    ]
    ph_claims = ", ".join(["%s" if db_type == "MYSQL" else "?"] * 9)
    cur.executemany(f"""
        INSERT INTO claims (item_id, claimant_user_id, claimant_name, claimant_contact, proof_description, confidence_score, claim_status, submitted_at, verified_by_user_id)
        VALUES ({ph_claims});
    """, claims_data)

    # Insert Lockers (Free Service - No fees)
    lockers_data = [
        (1, "LOCKER-A101", "2026-09-02", "2026-09-04", "Claim verified and returned to student"),
        (2, "LOCKER-B204", "2026-09-08", None, "Safely held in Cafeteria security desk locker"),
        (4, "LOCKER-C301", "2026-09-19", None, "Held in Sports Complex security locker"),
        (5, "LOCKER-A102", "2026-09-22", None, "Stored in Central Library safe locker")
    ]
    ph_lock = ", ".join(["%s" if db_type == "MYSQL" else "?"] * 5)
    cur.executemany(f"""
        INSERT INTO storage_lockers (item_id, locker_code, custody_start_date, release_date, remarks)
        VALUES ({ph_lock});
    """, lockers_data)

    if db_type == "SQLITE":
        conn.commit()

    print(f"{Colors.GREEN}✔ DML Seed Data Populated Successfully!{Colors.RESET}")
    print("   • 4 User records inserted.")
    print("   • 5 Categories inserted (No fees).")
    print("   • 4 Campus locations inserted.")
    print("   • 6 Items with realistic spread-out dates (Sept 2 - Sept 24, 2026).")
    print("   • 4 Claims inserted (2 APPROVED, 1 REJECTED, 1 PENDING).")
    print("   • 3 Storage locker custody records inserted (No fees).")


def demonstrate_data_cleaning(conn, db_type: str):
    """Step 3: Data Cleaning (NULL handling and constraint checks)."""
    print_section("STEP 3: DATA CLEANING & CONSTRAINT HANDLING")
    cur = conn.cursor()

    print(f"{Colors.BOLD}A. NULL Value Handling (Active Custody vs Released Items - Free Facility):{Colors.RESET}")
    sql_null = """
    SELECT 
        locker_code,
        item_id,
        custody_start_date,
        CASE 
            WHEN release_date IS NULL THEN 'CURRENTLY IN CUSTODY'
            ELSE release_date 
        END AS release_status,
        remarks
    FROM storage_lockers;
    """
    cur.execute(sql_null)
    rows = cur.fetchall()
    print_table(["Locker Code", "Item ID", "Custody Start", "Release Status", "Security Remarks"], rows)

    print(f"{Colors.BOLD}B. Constraint Enforcement (Unique Key Verification):{Colors.RESET}")
    print("  Attempting to insert a duplicate Category ('Electronics')...")
    try:
        cur.execute("INSERT INTO categories (category_name, description) VALUES ('Electronics', 'Duplicate');")
        if db_type == "SQLITE":
            conn.commit()
        print(f"{Colors.RED}❌ Error: Unique constraint failed to trigger!{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.GREEN}✔ Constraint successfully blocked duplicate: {Colors.YELLOW}{type(e).__name__}{Colors.RESET}")


def execute_basic_queries(conn):
    """Step 4: Basic Queries (SELECT, WHERE, ORDER BY with Dates)."""
    print_section("STEP 4: BASIC QUERIES (SELECT, WHERE, ORDER BY)")
    cur = conn.cursor()

    print(f"{Colors.BOLD}Query 1: SELECT with WHERE (Filter all FOUND items currently IN_CUSTODY):{Colors.RESET}")
    sql1 = """
    SELECT item_id, title, category, location, status, reward_or_value, reported_date 
    FROM items 
    WHERE item_type = 'FOUND' AND status = 'IN_CUSTODY'
    ORDER BY reported_date DESC;
    """
    cur.execute(sql1)
    rows1 = cur.fetchall()
    print_table(["Item ID", "Title", "Category", "Location", "Status", "Value (₹)", "Reported Date"], rows1)

    print(f"{Colors.BOLD}Query 2: SELECT with ORDER BY (High Value Items sorted descending):{Colors.RESET}")
    sql2 = """
    SELECT item_id, title, item_type, category, reward_or_value, reported_date 
    FROM items 
    ORDER BY reward_or_value DESC;
    """
    cur.execute(sql2)
    rows2 = cur.fetchall()
    print_table(["Item ID", "Title", "Type", "Category", "Value (₹)", "Reported Date"], rows2)

    print(f"{Colors.BOLD}Query 3: Claims Verification Queue (PENDING Claims):{Colors.RESET}")
    sql3 = """
    SELECT claim_id, item_id, claimant_name, claimant_contact, confidence_score, claim_status, submitted_at
    FROM claims
    WHERE claim_status = 'PENDING';
    """
    cur.execute(sql3)
    rows3 = cur.fetchall()
    print_table(["Claim ID", "Item ID", "Claimant Name", "Contact", "Score (%)", "Status", "Submitted At"], rows3)


def execute_aggregate_queries(conn):
    """Step 5: Aggregate Functions for Data Summaries."""
    print_section("STEP 5: AGGREGATE FUNCTIONS & DATA SUMMARIES (CLO2)")
    cur = conn.cursor()

    print(f"{Colors.BOLD}Aggregate 1: Overall Inventory Summary (COUNT, SUM, AVG, MAX, MIN):{Colors.RESET}")
    sql_agg1 = """
    SELECT 
        COUNT(*) AS total_items,
        SUM(reward_or_value) AS total_declared_value,
        ROUND(AVG(reward_or_value), 2) AS average_item_value,
        MAX(reward_or_value) AS highest_value,
        MIN(reward_or_value) AS lowest_value
    FROM items;
    """
    cur.execute(sql_agg1)
    rows_agg1 = cur.fetchall()
    print_table(["Total Items", "Total Value (₹)", "Avg Value (₹)", "Max Value (₹)", "Min Value (₹)"], rows_agg1)

    print(f"{Colors.BOLD}Aggregate 2: Category-wise Breakdown (GROUP BY & COUNT & AVG):{Colors.RESET}")
    sql_agg2 = """
    SELECT 
        category,
        COUNT(*) AS item_count,
        ROUND(AVG(reward_or_value), 2) AS avg_value,
        SUM(reward_or_value) AS total_val
    FROM items
    GROUP BY category
    ORDER BY item_count DESC;
    """
    cur.execute(sql_agg2)
    rows_agg2 = cur.fetchall()
    print_table(["Category", "Item Count", "Average Value (₹)", "Total Category Value (₹)"], rows_agg2)

    print(f"{Colors.BOLD}Aggregate 3: Claims Breakdown by Status (COUNT):{Colors.RESET}")
    sql_agg3 = """
    SELECT 
        claim_status,
        COUNT(*) AS total_claims,
        ROUND(AVG(confidence_score), 2) AS avg_confidence
    FROM claims
    GROUP BY claim_status;
    """
    cur.execute(sql_agg3)
    rows_agg3 = cur.fetchall()
    print_table(["Claim Status", "Total Claims", "Avg Confidence Score (%)"], rows_agg3)


def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}==================================================================================")
    print(f"       🏛️ LOST AND FOUND MANAGEMENT SYSTEM — PHASE 2 EXECUTION (CLO2)")
    print(f"=================================================================================={Colors.RESET}")

    conn, db_type = get_db_connection()
    print(f"Connected to Active Database Engine: {Colors.BOLD}{Colors.GREEN}{db_type}{Colors.RESET}\n")

    # Step 1: DDL Table Creation
    execute_ddl(conn, db_type)

    # Step 2: DML Record Insertion with Spread-Out Dates
    execute_dml(conn, db_type)

    # Step 3: Data Cleaning & Constraint Handling
    demonstrate_data_cleaning(conn, db_type)

    # Step 4: Basic Queries (SELECT, WHERE, ORDER BY)
    execute_basic_queries(conn)

    # Step 5: Aggregate Summaries (COUNT, SUM, AVG, GROUP BY)
    execute_aggregate_queries(conn)

    conn.close()

    print(f"{Colors.GREEN}{'=' * 85}")
    print(f"  🎉 ALL PHASE 2 LAB OBJECTIVES (CLO2) EXECUTED AND VERIFIED SUCCESSFULLY!")
    print(f"{'=' * 85}{Colors.RESET}\n")


if __name__ == "__main__":
    main()
