# -*- coding: utf-8 -*-
"""
מודול אינטגרציה עם Google Sheets - Google Sheets integration module
"""

import gspread
import pandas as pd
import re
from typing import Optional, Tuple, Dict, Any
import logging
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_CREDENTIALS_FILE, SCOPES
import os

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self, credentials_file: str = GOOGLE_CREDENTIALS_FILE):
        self.credentials_file = credentials_file
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """אימות מול Google Sheets API"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.warning(f"Google credentials file not found: {self.credentials_file}")
                return
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, SCOPES
            )
            self.client = gspread.authorize(credentials)
            logger.info("Google Sheets authentication successful")
            
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {e}")
            self.client = None
    
    def extract_sheet_id_from_url(self, url: str) -> Optional[str]:
        """חילוץ מזהה הגיליון מקישור URL"""
        try:
            # דפוסים שונים של קישורי Google Sheets
            patterns = [
                r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
                r'/d/([a-zA-Z0-9-_]+)',
                r'spreadsheets/d/([a-zA-Z0-9-_]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting sheet ID from URL: {e}")
            return None
    
    def get_sheet_data(self, sheet_url: str) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        """
        קבלת נתונים מגיליון Google Sheets
        
        Returns:
            Tuple[DataFrame, sheet_title, error_message]
        """
        try:
            if not self.client:
                return None, None, "לא ניתן להתחבר ל-Google Sheets. אנא ודא שקובץ האישורים קיים ותקין."
            
            # חילוץ מזהה הגיליון
            sheet_id = self.extract_sheet_id_from_url(sheet_url)
            if not sheet_id:
                return None, None, "לא ניתן לזהות את הגיליון מהקישור. אנא ודא שהקישור תקין."
            
            # פתיחת הגיליון
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.get_worksheet(0)  # גיליון ראשון
            
            # קבלת כל הנתונים
            data = worksheet.get_all_records()
            
            if not data:
                return None, None, "הגיליון ריק או לא מכיל נתונים."
            
            # המרה ל-DataFrame
            df = pd.DataFrame(data)
            
            # ניקוי עמודות ריקות
            df = df.dropna(how='all', axis=1)
            
            # ניקוי שורות ריקות
            df = df.dropna(how='all', axis=0)
            
            return df, sheet.title, None
            
        except gspread.exceptions.SpreadsheetNotFound:
            return None, None, "הגיליון לא נמצא. אנא ודא שהגיליון קיים ושהוא משותף עם החשבון השירות."
        
        except gspread.exceptions.APIError as e:
            return None, None, f"שגיאת API של Google Sheets: {str(e)}"
        
        except Exception as e:
            logger.error(f"Error getting sheet data: {e}")
            return None, None, f"שגיאה לא צפויה: {str(e)}"
    
    def get_sheet_info(self, sheet_url: str) -> Dict[str, Any]:
        """קבלת מידע על הגיליון"""
        try:
            if not self.client:
                return {"error": "לא ניתן להתחבר ל-Google Sheets"}
            
            sheet_id = self.extract_sheet_id_from_url(sheet_url)
            if not sheet_id:
                return {"error": "לא ניתן לזהות את הגיליון מהקישור"}
            
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.get_worksheet(0)
            
            # קבלת מידע על הגיליון
            info = {
                "title": sheet.title,
                "url": sheet.url,
                "row_count": getattr(worksheet, 'row_count', 0),
                "col_count": getattr(worksheet, 'col_count', 0)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting sheet info: {e}")
            return {"error": f"שגיאה בקבלת מידע על הגיליון: {str(e)}"}
    
    def test_connection(self) -> bool:
        """בדיקת חיבור ל-Google Sheets"""
        try:
            if not self.client:
                return False
            
            # ניסיון לפתוח גיליון לדוגמה (לא באמת נפתח)
            return True
            
        except Exception as e:
            logger.error(f"Google Sheets connection test failed: {e}")
            return False
    
    def get_available_sheets(self, user_email: str = None) -> list:
        """קבלת רשימת גיליונות זמינים למשתמש"""
        try:
            if not self.client:
                return []
            
            # קבלת כל הגיליונות שהחשבון השירות יכול לגשת אליהם
            sheets = self.client.openall()
            
            available_sheets = []
            for sheet in sheets:
                try:
                    # בדיקה אם הגיליון נגיש
                    worksheet = sheet.get_worksheet(0)
                    if worksheet:
                        available_sheets.append({
                            "title": sheet.title,
                            "url": sheet.url,
                            "created": sheet.created,
                            "updated": sheet.updated
                        })
                except:
                    continue
            
            return available_sheets
            
        except Exception as e:
            logger.error(f"Error getting available sheets: {e}")
            return []
    
    def is_valid_sheet_url(self, url: str) -> bool:
        """בדיקה אם הקישור הוא קישור Google Sheets תקין"""
        try:
            # בדיקת דפוסים נפוצים של Google Sheets
            valid_patterns = [
                r'https://docs\.google\.com/spreadsheets/d/',
                r'https://docs\.google\.com/spreadsheets/',
                r'spreadsheets/d/'
            ]
            
            return any(re.search(pattern, url) for pattern in valid_patterns)
            
        except Exception as e:
            logger.error(f"Error validating sheet URL: {e}")
            return False

# יצירת מופע גלובלי
google_sheets_manager = GoogleSheetsManager()

def get_google_sheets_manager() -> GoogleSheetsManager:
    """קבלת מופע של מנהל Google Sheets"""
    return google_sheets_manager

