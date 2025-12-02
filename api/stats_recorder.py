# stats_recorder.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os

class ModeStatistics:
    def __init__(self, db_path="data/mode_stats.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """originalize the database and tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # create mode selections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mode_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                page_url TEXT
            )
        ''')
        
        # create daily stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                chill_count INTEGER DEFAULT 0,
                action_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_selection(self, mode, session_id=None, page_url=None):
        """record a mode selection"""
        if mode not in ['chill', 'action']:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # plug mode selection
        cursor.execute('''
            INSERT INTO mode_selections (mode, session_id, page_url)
            VALUES (?, ?, ?)
        ''', (mode, session_id, page_url))
        
        # update daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            INSERT OR IGNORE INTO daily_stats (date) VALUES (?)
        ''', (today,))
        
        if mode == 'chill':
            cursor.execute('''
                UPDATE daily_stats 
                SET chill_count = chill_count + 1, 
                    total_count = total_count + 1 
                WHERE date = ?
            ''', (today,))
        else:
            cursor.execute('''
                UPDATE daily_stats 
                SET action_count = action_count + 1, 
                    total_count = total_count + 1 
                WHERE date = ?
            ''', (today,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_overall_stats(self):
        """recieve overall statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN mode = 'chill' THEN 1 END) as chill,
                COUNT(CASE WHEN mode = 'action' THEN 1 END) as action,
                COUNT(*) as total,
                MAX(timestamp) as last_updated
            FROM mode_selections
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'chill': row[0],
                'action': row[1],
                'total': row[2],
                'last_updated': row[3]
            }
        return {'chill': 0, 'action': 0, 'total': 0, 'last_updated': None}
    
    def get_daily_stats(self, days=30):
        """receive daily statistics for the past 'days' days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, chill_count, action_count, total_count
            FROM daily_stats
            WHERE date >= DATE('now', ?)
            ORDER BY date
        ''', (f'-{days} days',))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'date': row[0],
                'chill': row[1],
                'action': row[2],
                'total': row[3]
            }
            for row in rows
        ]
    
    def get_hourly_stats(self):
        """receive hourly statistics for today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%H:00', timestamp) as hour,
                COUNT(CASE WHEN mode = 'chill' THEN 1 END) as chill,
                COUNT(CASE WHEN mode = 'action' THEN 1 END) as action,
                COUNT(*) as total
            FROM mode_selections
            WHERE date(timestamp) = date('now')
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'hour': row[0],
                'chill': row[1],
                'action': row[2],
                'total': row[3]
            }
            for row in rows
        ]

# example usage
statistics = ModeStatistics()