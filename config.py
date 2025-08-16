# -*- coding: utf-8 -*-
"""
תצורת הבוט - Configuration file for the Hebrew Data Analytics Bot
"""

import os

# Try to load dotenv if available, otherwise continue without it
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, which is fine - we'll use environment variables directly
    pass

# Report Configuration
REPORT_LANG = os.getenv('REPORT_LANG', 'he')  # Default to Hebrew
REPORT_TZ = os.getenv('REPORT_TZ', 'Asia/Jerusalem')  # Default timezone

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOGS_MAX_PER_SEC = int(os.getenv('LOGS_MAX_PER_SEC', '100'))  # Token bucket rate limit

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

# Hebrew Text Constants
HEBREW_TEXTS = {
    # Main Menu
    'welcome': 'ברוך הבא לבוט הניתוח הנתונים! 📊\n\nאני יכול לעזור לך לנתח קבצי נתונים, ליצור תרשימים, ולגלות תובנות מעניינות.\n\nמה תרצה לעשות?',
    'main_menu': 'תפריט ראשי - בחר פעולה:',
    
    # File Upload
    'upload_file': '📁 העלה קובץ נתונים (CSV, Excel) או הכנס קישור לגיליון Google Sheets',
    'file_received': '✅ קובץ התקבל בהצלחה! מעבד את הנתונים...',
    'processing_data': '🔄 מעבד את הנתונים... אנא המתן.',
    'data_ready': '🎉 הנתונים מוכנים לניתוח! מה תרצה לעשות?',
    
    # Data Analysis
    'analyzing_data': '🔍 מנתח את הנתונים...',
    'basic_stats': '📊 סטטיסטיקות בסיסיות',
    'data_quality': '🔍 איכות הנתונים',
    'correlation': '📈 ניתוח קורלציה',
    'insights': '💡 תובנות ותגליות',
    
    # Visualizations
    'choose_chart': '📊 בחר סוג תרשים:',
    'chart_types': {
        'bar': '📊 תרשים עמודות',
        'line': '📈 תרשים קווי',
        'pie': '🥧 תרשים עוגה',
        'histogram': '📊 היסטוגרמה',
        'scatter': '🔵 תרשים פיזור',
        'box': '📦 תרשים קופסה'
    },
    
    # PDF Report
    'generating_pdf': '📄 יוצר דוח PDF...',
    'pdf_ready': '✅ הדוח מוכן! שולח לך...',
    'report_date': 'תאריך הדוח',
    'data_preview': 'תצוגה מקדימה של הנתונים',
    'missing_values': 'ערכים חסרים',
    'no_missing_values': 'אין ערכים חסרים בנתונים',
    'categorical_frequencies': 'תדירויות קטגוריות',
    'numeric_distributions': 'התפלגויות מספריות',
    'statistical_summary': 'סיכום סטטיסטי',
    
    # Google Sheets
    'enter_sheets_url': '🔗 הכנס את הקישור לגיליון Google Sheets:',
    'sheets_connected': '✅ התחברות לגיליון Google Sheets הצליחה!',
    'sheets_error': '❌ שגיאה בהתחברות לגיליון Google Sheets',
    
    # Natural Language Queries
    'ask_question': '❓ שאל שאלה על הנתונים (בעברית):',
    'question_examples': 'דוגמאות:\n• "מי הרווח הכי הרבה?"\n• "הצג את הפיזור של גיל לפי הכנסה"\n• "מה המגמה של המכירות?"',
    
    # Errors
    'file_error': '❌ שגיאה בקובץ. אנא ודא שהקובץ תקין ונסה שוב.',
    'no_data': '❌ אין נתונים לניתוח. אנא העלה קובץ תחילה.',
    'processing_error': '❌ שגיאה בעיבוד הנתונים. אנא נסה שוב.',
    
    # Success Messages
    'analysis_complete': '✅ הניתוח הושלם בהצלחה!',
    'chart_sent': '📊 התרשים נשלח!',
    'insights_found': '💡 נמצאו תובנות מעניינות!',
    
    # Buttons
    'buttons': {
        'upload_file': '📁 העלה קובץ',
        'google_sheets': '🔗 Google Sheets',
        'analyze_data': '🔍 נתח נתונים',
        'show_charts': '📊 הצג תרשימים',
        'generate_pdf': '📄 צור דוח PDF',
        'ask_question': '❓ שאל שאלה',
        'back_to_menu': '🔙 חזור לתפריט',
        'new_analysis': '🆕 ניתוח חדש'
    }
}

# Chart Configuration
CHART_CONFIG = {
    'figure_size': (10, 6),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'font_family': 'DejaVu Sans',
    'hebrew_font': 'Arial'
}

# Database Configuration
DATABASE_PATH = 'bot_database.db'

# File Upload Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']
TEMP_FOLDER = 'temp_files'

# Google Sheets Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Translation function
def t(key: str, lang: str = None) -> str:
    """
    Translation function for i18n support
    
    Args:
        key: Translation key
        lang: Language code (defaults to REPORT_LANG)
    
    Returns:
        Translated text or key if not found
    """
    if lang is None:
        lang = REPORT_LANG
    
    # For now we only support Hebrew, but structure allows expansion
    if lang == 'he':
        return HEBREW_TEXTS.get(key, key)
    else:
        # Fallback to Hebrew if language not supported
        return HEBREW_TEXTS.get(key, key)

