"""
SANTOSO-GRID - Database Management
SQLite database for storing campaigns, templates, and settings
Version: 1.0
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class Database:
    """SQLite database management"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        self.connect()
        
        cursor = self.conn.cursor()
        
        # Campaigns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                start_time TEXT,
                end_time TEXT,
                total INTEGER DEFAULT 0,
                sent INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                email TEXT,
                status TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        """)
        
        self.conn.commit()
        print("✅ Database initialized")
    
    # === CAMPAIGNS ===
    
    def create_campaign(self, total: int, subject: str) -> int:
        """Create new campaign"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO campaigns (subject, total, status, start_time)
            VALUES (?, ?, 'running', datetime('now'))
        """, (subject, total))
        
        self.conn.commit()
        campaign_id = cursor.lastrowid
        
        return campaign_id
    
    def update_campaign_status(
        self,
        campaign_id: int,
        status: str,
        sent: int = None,
        failed: int = None
    ):
        """Update campaign status"""
        self.connect()
        cursor = self.conn.cursor()
        
        if status == "completed":
            cursor.execute("""
                UPDATE campaigns
                SET status = ?, sent = ?, failed = ?, end_time = datetime('now')
                WHERE id = ?
            """, (status, sent, failed, campaign_id))
        else:
            if sent is not None:
                cursor.execute("""
                    UPDATE campaigns SET sent = ? WHERE id = ?
                """, (sent, campaign_id))
            if failed is not None:
                cursor.execute("""
                    UPDATE campaigns SET failed = ? WHERE id = ?
                """, (failed, campaign_id))
            cursor.execute("""
                UPDATE campaigns SET status = ? WHERE id = ?
            """, (status, campaign_id))
        
        self.conn.commit()
    
    def get_campaign(self, campaign_id: int) -> Optional[Dict]:
        """Get campaign by ID"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM campaigns WHERE id = ?
        """, (campaign_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM campaigns ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    # === TEMPLATES ===
    
    def save_template(self, name: str, content: str, content_type: str) -> int:
        """Save template"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO templates (name, content, content_type)
            VALUES (?, ?, ?)
        """, (name, content, content_type))
        
        self.conn.commit()
        
        return cursor.lastrowid
    
    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get template by ID"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM templates WHERE id = ?
        """, (template_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_templates(self) -> List[Dict]:
        """Get all templates"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM templates ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def delete_template(self, template_id: int):
        """Delete template"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM templates WHERE id = ?
        """, (template_id,))
        
        self.conn.commit()
    
    # === SETTINGS ===
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get setting value"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT value FROM settings WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        
        if row:
            return row[0]
        return None
    
    def set_setting(self, key: str, value: str):
        """Set setting value"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, value))
        
        self.conn.commit()
    
    def get_settings(self) -> Dict:
        """Get all settings"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT key, value FROM settings
        """)
        
        rows = cursor.fetchall()
        
        return {row[0]: row[1] for row in rows}
    
    # === LOGS ===
    
    def add_log(self, campaign_id: int, email: str, status: str):
        """Add log entry"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs (campaign_id, email, status)
            VALUES (?, ?, ?)
        """, (campaign_id, email, status))
        
        self.conn.commit()
    
    def get_campaign_logs(self, campaign_id: int) -> List[Dict]:
        """Get campaign logs"""
        self.connect()
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM logs WHERE campaign_id = ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, (campaign_id,))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]