"""
Universal AI Web Scraper - Database Module
Handles SQLite operations, database creation, table setups, history tracking, logs insertion, and configuration settings.
"""

import sqlite3
import os
import json
import threading
from typing import Dict, List, Any, Optional

DB_FILE = "scraper.db"
_db_lock = threading.RLock()

class DatabaseManager:
    """
    Singleton class to coordinate database access.
    Uses context managers for transactions to ensure thread-safety and avoid locks.
    """
    _instance: Optional['DatabaseManager'] = None

    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        if cls._instance is None:
            with _db_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        if DatabaseManager._instance is not None:
            raise RuntimeError("DatabaseManager is a singleton, use get_instance().")
        self.db_path = DB_FILE
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a connection with thread-safety enabled and row factory set to dict."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        """Creates the tables if they do not exist and sets up initial settings."""
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON;")

                # Settings table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                """)

                # Projects table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                );
                """)

                # History table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    url TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    export_path TEXT,
                    results_count INTEGER DEFAULT 0,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL
                );
                """)

                # Results table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    history_id INTEGER NOT NULL,
                    result_key TEXT NOT NULL,
                    result_value TEXT,
                    FOREIGN KEY(history_id) REFERENCES history(id) ON DELETE CASCADE
                );
                """)

                # Logs table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                );
                """)

                # Insert Default Settings if not present
                default_settings = {
                    "theme": "Dark",
                    "browser": "Chrome",
                    "headless": "True",
                    "timeout": "30",
                    "retry_count": "3",
                    "output_folder": os.path.abspath(os.path.join(os.getcwd(), "scrapes"))
                }
                
                for key, val in default_settings.items():
                    cursor.execute(
                        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);",
                        (key, val)
                    )

                conn.commit()

    # --- Settings Manager ---
    def get_setting(self, key: str, default: str = "") -> str:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
                row = cursor.fetchone()
                return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);",
                    (key, str(value))
                )
                conn.commit()

    def get_all_settings(self) -> Dict[str, str]:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings;")
                return {row["key"]: row["value"] for row in cursor.fetchall()}

    # --- Logs Table Writer (used by DatabaseHandler) ---
    def insert_log(self, timestamp: str, level: str, message: str):
        # We don't acquire the global _db_lock inside dynamic log statements if it slows down threads, 
        # but to keep SQLite safe from parallel writes, a short-lived transaction is used.
        try:
            with _db_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?);",
                        (timestamp, level, message)
                    )
                    conn.commit()
        except Exception:
            pass

    def get_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, timestamp, level, message FROM logs ORDER BY id DESC LIMIT ?;",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]

    def clear_logs(self):
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM logs;")
                conn.commit()

    # --- History Manager ---
    def add_history_entry(self, url: str, prompt: str, timestamp: str, status: str, project_id: Optional[int] = None) -> int:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO history (url, prompt, timestamp, status, project_id)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (url, prompt, timestamp, status, project_id)
                )
                conn.commit()
                return cursor.lastrowid

    def update_history_status(self, history_id: int, status: str, export_path: Optional[str] = None, count: int = 0):
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE history 
                    SET status = ?, export_path = ?, results_count = ?
                    WHERE id = ?;
                    """,
                    (status, export_path, count, history_id)
                )
                conn.commit()

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, project_id, url, prompt, timestamp, status, export_path, results_count FROM history ORDER BY id DESC LIMIT ?;",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]

    def delete_history_entry(self, history_id: int):
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history WHERE id = ?;", (history_id,))
                conn.commit()

    # --- Results Manager ---
    def save_results(self, history_id: int, results_list: List[Dict[str, Any]]):
        """Saves scraped key-value pairs linked to a specific history entry."""
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # To support quick lookup of row-based dicts, we serialize rows/dicts as json value 
                # or store individual records. Let's serialize dicts as key: index/row_id, value: json representation
                # which keeps parsing very clean.
                for idx, item in enumerate(results_list):
                    cursor.execute(
                        """
                        INSERT INTO results (history_id, result_key, result_value)
                        VALUES (?, ?, ?);
                        """,
                        (history_id, f"row_{idx}", json.dumps(item))
                    )
                conn.commit()

    def get_results_for_history(self, history_id: int) -> List[Dict[str, Any]]:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT result_value FROM results WHERE history_id = ? ORDER BY id ASC;",
                    (history_id,)
                )
                rows = cursor.fetchall()
                results = []
                for r in rows:
                    try:
                        results.append(json.loads(r["result_value"]))
                    except Exception:
                        pass
                return results

    # --- Projects Manager ---
    def create_project(self, name: str, description: str) -> int:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO projects (name, description, created_at) VALUES (?, ?, ?);",
                    (name, description, now)
                )
                conn.commit()
                return cursor.lastrowid

    def get_projects(self) -> List[Dict[str, Any]]:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, description, created_at FROM projects ORDER BY id DESC;")
                return [dict(row) for row in cursor.fetchall()]

    # --- Analytics & Dashboard Stats ---
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        with _db_lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total Runs
                cursor.execute("SELECT COUNT(*) FROM history;")
                total_runs = cursor.fetchone()[0]

                # Success vs Failed
                cursor.execute("SELECT COUNT(*) FROM history WHERE status = 'COMPLETED';")
                successful_runs = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM history WHERE status = 'FAILED';")
                failed_runs = cursor.fetchone()[0]

                # Total Items Scraped
                cursor.execute("SELECT SUM(results_count) FROM history;")
                total_items = cursor.fetchone()[0] or 0

                # Unique Domains Scraped
                cursor.execute("SELECT url FROM history;")
                urls = [r[0] for r in cursor.fetchall()]
                domains = set()
                for url in urls:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        if domain:
                            domains.add(domain)
                    except Exception:
                        pass
                unique_domains = len(domains)

                return {
                    "total_runs": total_runs,
                    "successful_runs": successful_runs,
                    "failed_runs": failed_runs,
                    "total_items_scraped": total_items,
                    "unique_domains_scraped": unique_domains
                }
