import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "instance" / "pis.db"

def init_db():
    """Initialize SQLite database"""
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create pis table
    c.execute("""
        CREATE TABLE IF NOT EXISTS pis (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            ip TEXT NOT NULL,
            city TEXT DEFAULT 'bergen',
            dashboard_mode TEXT DEFAULT 'operations',
            theme TEXT DEFAULT '',
            refresh_secs INTEGER DEFAULT 300,
            last_status TEXT DEFAULT 'unknown',
            last_updated TIMESTAMP
        )
    """)

    # Initialize with default Pi's if empty
    c.execute("SELECT COUNT(*) FROM pis")
    if c.fetchone()[0] == 0:
        pis = [
            ("operations-oslo", "10.0.1.99", "oslo", "operations"),
            ("mekanisk-oslo", "10.0.1.28", "oslo", "mechanics"),
        ]
        for name, ip, city, mode in pis:
            c.execute(
                "INSERT INTO pis (name, ip, city, dashboard_mode) VALUES (?, ?, ?, ?)",
                (name, ip, city, mode)
            )

    conn.commit()
    conn.close()


class PiConfig:
    """Manage Pi configurations"""

    @staticmethod
    def get_all():
        """Get all Pi configurations"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM pis")
        pis = [dict(row) for row in c.fetchall()]
        conn.close()
        return pis

    @staticmethod
    def get_by_id(pi_id):
        """Get Pi configuration by ID"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM pis WHERE id = ?", (pi_id,))
        pi = c.fetchone()
        conn.close()
        return dict(pi) if pi else None

    @staticmethod
    def update(pi_id, data):
        """Update Pi configuration"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        updates = []
        values = []

        if "city" in data:
            updates.append("city = ?")
            values.append(data["city"])

        if "dashboard_mode" in data:
            updates.append("dashboard_mode = ?")
            values.append(data["dashboard_mode"])

        if "theme" in data:
            updates.append("theme = ?")
            values.append(data["theme"])

        if "refresh_secs" in data:
            updates.append("refresh_secs = ?")
            values.append(data["refresh_secs"])

        updates.append("last_updated = ?")
        values.append(datetime.now())
        values.append(pi_id)

        if updates:
            query = f"UPDATE pis SET {', '.join(updates)} WHERE id = ?"
            c.execute(query, values)
            conn.commit()

        conn.close()
        return True

    @staticmethod
    def update_status(pi_id, status):
        """Update Pi status"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE pis SET last_status = ?, last_updated = ? WHERE id = ?",
            (status, datetime.now(), pi_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def add_pi(name, ip, city="bergen"):
        """Add new Pi"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO pis (name, ip, city) VALUES (?, ?, ?)",
                (name, ip, city)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
