# -*- coding: utf-8 -*-
"""
מודול מסד הנתונים - Database module for managing user sessions and analysis history
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'bot_database.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """יצירת מסד הנתונים וטבלאות נדרשות"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # טבלת משתמשים
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # טבלת סשנים
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        file_name TEXT,
                        file_type TEXT,
                        file_size INTEGER,
                        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        analysis_count INTEGER DEFAULT 0,
                        last_analysis TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # טבלת היסטוריית ניתוח
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        analysis_type TEXT,
                        analysis_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                ''')
                
                # טבלת Google Sheets connections
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS google_sheets (
                        sheet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        sheet_url TEXT,
                        sheet_title TEXT,
                        connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """הוספת משתמש חדש או עדכון משתמש קיים"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                
                conn.commit()
                logger.info(f"User {user_id} added/updated successfully")
                
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
    
    def update_user_activity(self, user_id: int):
        """עדכון זמן פעילות אחרון של משתמש"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating user activity {user_id}: {e}")
    
    def create_session(self, user_id: int, file_name: str, file_type: str, file_size: int) -> int:
        """יצירת סשן חדש לניתוח קובץ"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO sessions (user_id, file_name, file_type, file_size)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, file_name, file_type, file_size))
                
                session_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Session {session_id} created for user {user_id}")
                return session_id
                
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            return None
    
    def get_active_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """קבלת הסשן הפעיל של משתמש"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM sessions 
                    WHERE user_id = ? 
                    ORDER BY upload_time DESC 
                    LIMIT 1
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            logger.error(f"Error getting active session for user {user_id}: {e}")
            return None
    
    def update_session_analysis(self, session_id: int, analysis_type: str, analysis_data: Dict[str, Any]):
        """עדכון סשן עם ניתוח חדש"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # הוספת ניתוח להיסטוריה
                cursor.execute('''
                    INSERT INTO analysis_history (session_id, analysis_type, analysis_data)
                    VALUES (?, ?, ?)
                ''', (session_id, analysis_type, json.dumps(analysis_data)))
                
                # עדכון סטטיסטיקות הסשן
                cursor.execute('''
                    UPDATE sessions 
                    SET analysis_count = analysis_count + 1,
                        last_analysis = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (session_id,))
                
                conn.commit()
                logger.info(f"Analysis updated for session {session_id}")
                
        except Exception as e:
            logger.error(f"Error updating session analysis {session_id}: {e}")
    
    def add_google_sheets_connection(self, user_id: int, sheet_url: str, sheet_title: str):
        """הוספת חיבור Google Sheets"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO google_sheets (user_id, sheet_url, sheet_title, last_access)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, sheet_url, sheet_title))
                
                conn.commit()
                logger.info(f"Google Sheets connection added for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error adding Google Sheets connection for user {user_id}: {e}")
    
    def get_user_sheets(self, user_id: int) -> list:
        """קבלת כל חיבורי Google Sheets של משתמש"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM google_sheets 
                    WHERE user_id = ? 
                    ORDER BY last_access DESC
                ''', (user_id,))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting Google Sheets for user {user_id}: {e}")
            return []
    
    def cleanup_old_sessions(self, days_old: int = 7):
        """ניקוי סשנים ישנים"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM analysis_history 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days_old))
                
                cursor.execute('''
                    DELETE FROM sessions 
                    WHERE upload_time < datetime('now', '-{} days')
                '''.format(days_old))
                
                conn.commit()
                logger.info(f"Cleaned up sessions older than {days_old} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """קבלת סטטיסטיקות משתמש"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # סך כל הניתוחים
                cursor.execute('''
                    SELECT COUNT(*) FROM analysis_history ah
                    JOIN sessions s ON ah.session_id = s.session_id
                    WHERE s.user_id = ?
                ''', (user_id,))
                total_analyses = cursor.fetchone()[0]
                
                # סך כל הקבצים
                cursor.execute('''
                    SELECT COUNT(*) FROM sessions WHERE user_id = ?
                ''', (user_id,))
                total_files = cursor.fetchone()[0]
                
                # קובץ אחרון
                cursor.execute('''
                    SELECT file_name, upload_time FROM sessions 
                    WHERE user_id = ? 
                    ORDER BY upload_time DESC 
                    LIMIT 1
                ''', (user_id,))
                last_file = cursor.fetchone()
                
                return {
                    'total_analyses': total_analyses,
                    'total_files': total_files,
                    'last_file': last_file[0] if last_file else None,
                    'last_upload': last_file[1] if last_file else None
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats for user {user_id}: {e}")
            return {}

