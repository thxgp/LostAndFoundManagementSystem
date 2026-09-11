"""
Database Configuration for Lost and Found Management System
Supports MySQL with automated fallback to SQLite if MySQL server is unavailable.
"""

import os

# MySQL Default Connection Config
MYSQL_HOST = os.getenv("DB_HOST", "localhost")
MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))
MYSQL_USER = os.getenv("DB_USER", "root")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("DB_NAME", "lost_found_db")

# Fallback SQLite DB Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "lost_found_local.db")
SEED_DATA_PATH = os.path.join(BASE_DIR, "data", "seed_items.json")
