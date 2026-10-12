"""
Database Manager for Lost and Found Management System.
Connects to MySQL with automatic fallback to SQLite for zero-configuration portability.
"""

import os
import json
import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from config.db_config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, SQLITE_DB_PATH
)
from src.models import ItemRecord, ClaimRecord, AuditAction


class DatabaseManager:
    """
    Handles database persistence, schema initialisation, and bidirectional synchronization.
    """
    def __init__(self, prefer_mysql: bool = True):
        self.prefer_mysql = prefer_mysql
        self.db_type: str = "SQLITE"  # "MYSQL" or "SQLITE"
        self._mysql_conn = None
        self._sqlite_conn = None
        self._init_connection()
        self._create_tables()

    def _init_connection(self) -> None:
        """Attempt connection to MySQL; if unavailable, fallback gracefully to SQLite."""
        if self.prefer_mysql:
            try:
                import mysql.connector
                # First connect to server to ensure database exists
                server_conn = mysql.connector.connect(
                    host=MYSQL_HOST,
                    port=MYSQL_PORT,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD
                )
                cursor = server_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE};")
                cursor.close()
                server_conn.close()

                # Connect to specific database
                self._mysql_conn = mysql.connector.connect(
                    host=MYSQL_HOST,
                    port=MYSQL_PORT,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE,
                    autocommit=True
                )
                self.db_type = "MYSQL"
                return
            except Exception as e:
                # MySQL connection failed, fallback to SQLite
                pass

        # Fallback SQLite initialization
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        self._sqlite_conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        self._sqlite_conn.row_factory = sqlite3.Row
        self.db_type = "SQLITE"

    def _get_cursor(self):
        if self.db_type == "MYSQL":
            return self._mysql_conn.cursor(dictionary=True)
        else:
            return self._sqlite_conn.cursor()

    def _create_tables(self) -> None:
        """Create tables if they don't exist in the active database engine."""
        cursor = self._get_cursor()

        if self.db_type == "MYSQL":
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                item_type ENUM('LOST', 'FOUND') NOT NULL,
                location VARCHAR(100) NOT NULL,
                status ENUM('REPORTED', 'IN_CUSTODY', 'CLAIM_PENDING', 'VERIFIED_RETURNED', 'DISPOSED') DEFAULT 'REPORTED',
                reporter_name VARCHAR(100) NOT NULL,
                reporter_contact VARCHAR(50) NOT NULL,
                reward_or_value DECIMAL(10, 2) DEFAULT 0.00,
                reported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id INT AUTO_INCREMENT PRIMARY KEY,
                item_id INT NOT NULL,
                claimant_name VARCHAR(100) NOT NULL,
                claimant_contact VARCHAR(50) NOT NULL,
                proof_description TEXT NOT NULL,
                confidence_score DECIMAL(5, 2) DEFAULT 0.00,
                claim_status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_actions (
                action_id INT AUTO_INCREMENT PRIMARY KEY,
                action_type VARCHAR(50) NOT NULL,
                item_id INT,
                snapshot_before JSON,
                snapshot_after JSON,
                performed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        else:
            # SQLite Tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                item_type TEXT NOT NULL,
                location TEXT NOT NULL,
                status TEXT DEFAULT 'REPORTED',
                reporter_name TEXT NOT NULL,
                reporter_contact TEXT NOT NULL,
                reward_or_value REAL DEFAULT 0.0,
                reported_date TEXT,
                updated_at TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                claimant_name TEXT NOT NULL,
                claimant_contact TEXT NOT NULL,
                proof_description TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0,
                claim_status TEXT DEFAULT 'PENDING',
                submitted_at TEXT,
                FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                performed_by_user_id INTEGER,
                action_type TEXT NOT NULL,
                snapshot_before TEXT,
                snapshot_after TEXT,
                performed_at TEXT,
                FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE SET NULL,
                FOREIGN KEY (performed_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
            );
            """)
            self._sqlite_conn.commit()

        cursor.close()

    # --- Item CRUD Operations ---

    def insert_item(self, item: ItemRecord) -> int:
        """Insert a new item and return assigned item_id."""
        cursor = self._get_cursor()
        if self.db_type == "MYSQL":
            sql = """
            INSERT INTO items (title, category, description, item_type, location,
                               status, reporter_name, reporter_contact, reward_or_value,
                               reported_date, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                item.title, item.category, item.description, item.item_type,
                item.location, item.status, item.reporter_name, item.reporter_contact,
                item.reward_or_value, item.reported_date, item.updated_at
            )
            cursor.execute(sql, params)
            item_id = cursor.lastrowid
        else:
            sql = """
            INSERT INTO items (title, category, description, item_type, location,
                               status, reporter_name, reporter_contact, reward_or_value,
                               reported_date, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                item.title, item.category, item.description, item.item_type,
                item.location, item.status, item.reporter_name, item.reporter_contact,
                item.reward_or_value, item.reported_date, item.updated_at
            )
            cursor.execute(sql, params)
            self._sqlite_conn.commit()
            item_id = cursor.lastrowid

        cursor.close()
        return item_id

    def update_item(self, item: ItemRecord) -> bool:
        """Update an existing item record in database."""
        cursor = self._get_cursor()
        if self.db_type == "MYSQL":
            sql = """
            UPDATE items SET title=%s, category=%s, description=%s, item_type=%s,
                             location=%s, status=%s, reporter_name=%s, reporter_contact=%s,
                             reward_or_value=%s, updated_at=%s
            WHERE item_id=%s
            """
            params = (
                item.title, item.category, item.description, item.item_type,
                item.location, item.status, item.reporter_name, item.reporter_contact,
                item.reward_or_value, item.updated_at, item.item_id
            )
            cursor.execute(sql, params)
            affected = cursor.rowcount > 0
        else:
            sql = """
            UPDATE items SET title=?, category=?, description=?, item_type=?,
                             location=?, status=?, reporter_name=?, reporter_contact=?,
                             reward_or_value=?, updated_at=?
            WHERE item_id=?
            """
            params = (
                item.title, item.category, item.description, item.item_type,
                item.location, item.status, item.reporter_name, item.reporter_contact,
                item.reward_or_value, item.updated_at, item.item_id
            )
            cursor.execute(sql, params)
            self._sqlite_conn.commit()
            affected = cursor.rowcount > 0

        cursor.close()
        return affected

    def delete_item(self, item_id: int) -> bool:
        """Delete an item record from database."""
        cursor = self._get_cursor()
        placeholder = "%s" if self.db_type == "MYSQL" else "?"
        cursor.execute(f"DELETE FROM items WHERE item_id = {placeholder}", (item_id,))
        if self.db_type == "SQLITE":
            self._sqlite_conn.commit()
        affected = cursor.rowcount > 0
        cursor.close()
        return affected

    def fetch_all_items(self) -> List[ItemRecord]:
        """Fetch all item records from the database."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM items ORDER BY item_id ASC")
        rows = cursor.fetchall()
        cursor.close()

        items = []
        for row in rows:
            d = dict(row)
            # Ensure proper string/float types
            d["item_id"] = int(d["item_id"])
            d["reward_or_value"] = float(d.get("reward_or_value", 0.0) or 0.0)
            d["reported_date"] = str(d.get("reported_date", ""))
            d["updated_at"] = str(d.get("updated_at", ""))
            items.append(ItemRecord.from_dict(d))
        return items

    # --- Claims Operations ---

    def insert_claim(self, claim: ClaimRecord) -> int:
        """Insert a verification claim."""
        cursor = self._get_cursor()
        if self.db_type == "MYSQL":
            sql = """
            INSERT INTO claims (item_id, claimant_name, claimant_contact, proof_description,
                                confidence_score, claim_status, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                claim.item_id, claim.claimant_name, claim.claimant_contact,
                claim.proof_description, claim.confidence_score, claim.claim_status,
                claim.submitted_at
            )
            cursor.execute(sql, params)
            claim_id = cursor.lastrowid
        else:
            sql = """
            INSERT INTO claims (item_id, claimant_name, claimant_contact, proof_description,
                                confidence_score, claim_status, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                claim.item_id, claim.claimant_name, claim.claimant_contact,
                claim.proof_description, claim.confidence_score, claim.claim_status,
                claim.submitted_at
            )
            cursor.execute(sql, params)
            self._sqlite_conn.commit()
            claim_id = cursor.lastrowid

        cursor.close()
        return claim_id

    def update_claim_status(self, claim_id: int, status: str, confidence: float = 0.0) -> bool:
        """Update status and confidence score of a claim."""
        cursor = self._get_cursor()
        if self.db_type == "MYSQL":
            sql = "UPDATE claims SET claim_status=%s, confidence_score=%s WHERE claim_id=%s"
            cursor.execute(sql, (status, confidence, claim_id))
            affected = cursor.rowcount > 0
        else:
            sql = "UPDATE claims SET claim_status=?, confidence_score=? WHERE claim_id=?"
            cursor.execute(sql, (status, confidence, claim_id))
            self._sqlite_conn.commit()
            affected = cursor.rowcount > 0
        cursor.close()
        return affected

    def fetch_all_claims(self) -> List[ClaimRecord]:
        """Fetch all claims from database."""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM claims ORDER BY claim_id ASC")
        rows = cursor.fetchall()
        cursor.close()

        claims = []
        for row in rows:
            d = dict(row)
            d["claim_id"] = int(d["claim_id"])
            d["item_id"] = int(d["item_id"])
            d["confidence_score"] = float(d.get("confidence_score", 0.0) or 0.0)
            d["submitted_at"] = str(d.get("submitted_at", ""))
            claims.append(ClaimRecord.from_dict(d))
        return claims

    # --- Audit Operations ---

    def insert_audit(self, action: AuditAction) -> int:
        """Persist an audit snapshot."""
        cursor = self._get_cursor()
        sb_json = json.dumps(action.snapshot_before) if action.snapshot_before else None
        sa_json = json.dumps(action.snapshot_after) if action.snapshot_after else None

        if self.db_type == "MYSQL":
            sql = "INSERT INTO audit_actions (action_type, item_id, snapshot_before, snapshot_after, performed_at) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (action.action_type, action.item_id, sb_json, sa_json, action.performed_at))
            action_id = cursor.lastrowid
        else:
            sql = "INSERT INTO audit_actions (action_type, item_id, snapshot_before, snapshot_after, performed_at) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, (action.action_type, action.item_id, sb_json, sa_json, action.performed_at))
            self._sqlite_conn.commit()
            action_id = cursor.lastrowid

        cursor.close()
        return action_id
