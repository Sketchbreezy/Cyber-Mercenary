"""
Database Service

SQLite persistence for scans, bounties, and statistics.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScanRecord:
    """A saved scan record"""
    id: int
    scan_id: str
    contract_address: str
    chain_id: int
    status: str
    risk_score: float
    vulnerability_count: int
    created_at: str
    result_data: Optional[str] = None


@dataclass
class BountyRecord:
    """A saved bounty record"""
    id: int
    bounty_id: int
    contract_address: str
    amount_wei: int
    status: str
    created_at: str
    claimed_at: Optional[str] = None


class DatabaseService:
    """SQLite database service for persistence"""

    def __init__(self, db_url: str = "sqlite:///./data/cyber_mercenary.db"):
        # Parse the URL
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
        else:
            db_path = db_url

        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Scans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT UNIQUE NOT NULL,
                contract_address TEXT NOT NULL,
                chain_id INTEGER DEFAULT 10143,
                status TEXT DEFAULT 'queued',
                risk_score REAL DEFAULT 0,
                vulnerability_count INTEGER DEFAULT 0,
                result_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bounties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bounties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bounty_id INTEGER NOT NULL,
                contract_address TEXT,
                amount_wei INTEGER DEFAULT 0,
                status TEXT DEFAULT 'created',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                claimed_at TEXT
            )
        """)

        # Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                contracts_scanned INTEGER DEFAULT 0,
                vulnerabilities_found INTEGER DEFAULT 0,
                bounties_earned REAL DEFAULT 0,
                gigs_completed INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Initialize stats row
        cursor.execute("""
            INSERT OR IGNORE INTO stats (id) VALUES (1)
        """)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    # Scan operations
    def save_scan(self, scan_id: str, contract_address: str, chain_id: int = 10143,
                  status: str = "queued", risk_score: float = 0,
                  vulnerability_count: int = 0, result_data: Optional[str] = None) -> int:
        """Save a scan record"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO scans (scan_id, contract_address, chain_id, status, risk_score, vulnerability_count, result_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, contract_address, chain_id, status, risk_score, vulnerability_count, result_data))

        conn.commit()
        conn.close()

        # Update stats
        self._increment_stat("contracts_scanned")

        return cursor.lastrowid

    def get_scan(self, scan_id: str) -> Optional[dict]:
        """Get a scan by scan_id"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_scans(self, limit: int = 100) -> list[dict]:
        """Get all scans"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Bounty operations
    def save_bounty(self, bounty_id: int, contract_address: Optional[str] = None,
                    amount_wei: int = 0, status: str = "created") -> int:
        """Save a bounty record"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bounties (bounty_id, contract_address, amount_wei, status)
            VALUES (?, ?, ?, ?)
        """, (bounty_id, contract_address, amount_wei, status))

        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_bounty(self, bounty_id: int) -> Optional[dict]:
        """Get a bounty by bounty_id"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bounties WHERE bounty_id = ?", (bounty_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def claim_bounty(self, bounty_id: int) -> bool:
        """Mark a bounty as claimed"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE bounties SET claimed_at = CURRENT_TIMESTAMP WHERE bounty_id = ?
        """, (bounty_id,))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # Statistics operations
    def get_stats(self) -> dict:
        """Get current statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stats WHERE id = 1")
        row = cursor.fetchone()

        # Count from tables
        cursor.execute("SELECT COUNT(*) FROM scans")
        contracts_scanned = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(vulnerability_count) FROM scans")
        vuln_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM bounties WHERE claimed_at IS NOT NULL")
        bounties_earned = cursor.fetchone()[0]

        conn.close()

        return {
            "contracts_scanned": contracts_scanned,
            "vulnerabilities_found": vuln_count,
            "bounties_earned": bounties_earned,
            "gigs_completed": 0,
        }

    def _increment_stat(self, stat_name: str):
        """Increment a statistic"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(f"UPDATE stats SET {stat_name} = {stat_name} + 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
        conn.commit()
        conn.close()

    def increment_vulnerabilities(self, count: int = 1):
        """Increment vulnerability count"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE stats SET vulnerabilities_found = vulnerabilities_found + ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (count,))
        conn.commit()
        conn.close()
