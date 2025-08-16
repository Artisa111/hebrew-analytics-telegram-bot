# -*- coding: utf-8 -*-
"""
מודול בינאומיות ותרגום - Internationalization (i18n) module
תמיכה בתרגום לעברית עם ערכי ברירת מחדל
"""

import os
from datetime import datetime
import pytz
import pandas as pd
from typing import Dict, Any


# Default language is Hebrew
REPORT_LANG = os.getenv('REPORT_LANG', 'he')
REPORT_TZ = os.getenv('REPORT_TZ', 'Asia/Jerusalem')


# Hebrew translations
TRANSLATIONS = {
    'he': {
        # Report sections
        'data_preview': 'תצוגה מקדימה של הנתונים',
        'data_preview_subtitle': 'ראשת שורות מהנתונים',
        'missing_values': 'ניתוח ערכים חסרים',
        'missing_values_subtitle': 'אחוז הערכים החסרים בכל עמודה',
        'no_missing_values': 'אין ערכים חסרים בנתונים - מצוין! 👍',
        'categorical_distributions': 'התפלגות קטגוריות',
        'categorical_distributions_subtitle': 'ערכים נפוצים בעמודות קטגוריות',
        'numeric_distributions': 'התפלגות מספרית',
        'numeric_distributions_subtitle': 'היסטוגרמות ותיבות של עמודות מספריות',
        'statistical_summary': 'סיכום סטטיסטי',
        'statistical_summary_subtitle': 'סטטיסטיקות תיאוריות עבור עמודות מספריות',
        
        # Title page
        'report_title': 'דוח ניתוח נתונים',
        'report_date': 'תאריך הדוח',
        'generated_at': 'נוצר ב',
        
        # Data info
        'rows': 'שורות',
        'columns': 'עמודות',
        'data_shape': 'צורת הנתונים',
        
        # Charts and visualizations
        'frequency': 'תדירות',
        'value': 'ערך',
        'count': 'כמות',
        'percentage': 'אחוז',
        'column': 'עמודה',
        'missing_percentage': 'אחוז ערכים חסרים',
        'distribution': 'התפלגות',
        'boxplot': 'תרשים תיבה',
        'histogram': 'היסטוגרמה',
        
        # Statistics
        'mean': 'ממוצע',
        'median': 'חציון',
        'std': 'סטיית תקן',
        'min': 'מינימום',
        'max': 'מקסימום',
        'q25': 'רבעון ראשון',
        'q75': 'רבעון שלישי',
        'count_stat': 'מספר ערכים',
        
        # Errors and warnings
        'no_data': 'אין נתונים זמינים',
        'error_generating': 'שגיאה ביצירת הקטע',
        'no_numeric_columns': 'לא נמצאו עמודות מספריות',
        'no_categorical_columns': 'לא נמצאו עמודות קטגוריות',
        
        # File operations
        'processing_file': 'מעבד קובץ',
        'file_processed': 'קובץ עובד בהצלחה',
        'error_reading_file': 'שגיאה בקריאת הקובץ',
    },
    
    'en': {
        # Report sections
        'data_preview': 'Data Preview',
        'data_preview_subtitle': 'First few rows from the dataset',
        'missing_values': 'Missing Values Analysis',
        'missing_values_subtitle': 'Percentage of missing values per column',
        'no_missing_values': 'No missing values found - excellent! 👍',
        'categorical_distributions': 'Categorical Distributions',
        'categorical_distributions_subtitle': 'Most frequent values in categorical columns',
        'numeric_distributions': 'Numeric Distributions',
        'numeric_distributions_subtitle': 'Histograms and boxplots of numeric columns',
        'statistical_summary': 'Statistical Summary',
        'statistical_summary_subtitle': 'Descriptive statistics for numeric columns',
        
        # Title page
        'report_title': 'Data Analysis Report',
        'report_date': 'Report Date',
        'generated_at': 'Generated at',
        
        # Data info
        'rows': 'Rows',
        'columns': 'Columns',
        'data_shape': 'Data Shape',
        
        # Charts and visualizations
        'frequency': 'Frequency',
        'value': 'Value',
        'count': 'Count',
        'percentage': 'Percentage',
        'column': 'Column',
        'missing_percentage': 'Missing Percentage',
        'distribution': 'Distribution',
        'boxplot': 'Boxplot',
        'histogram': 'Histogram',
        
        # Statistics
        'mean': 'Mean',
        'median': 'Median',
        'std': 'Std Dev',
        'min': 'Minimum',
        'max': 'Maximum',
        'q25': 'Q1',
        'q75': 'Q3',
        'count_stat': 'Count',
        
        # Errors and warnings
        'no_data': 'No data available',
        'error_generating': 'Error generating section',
        'no_numeric_columns': 'No numeric columns found',
        'no_categorical_columns': 'No categorical columns found',
        
        # File operations
        'processing_file': 'Processing file',
        'file_processed': 'File processed successfully',
        'error_reading_file': 'Error reading file',
    }
}


def t(key: str, lang: str = None) -> str:
    """
    פונקציית תרגום - Translation function
    
    Args:
        key: Translation key
        lang: Language code (defaults to REPORT_LANG)
        
    Returns:
        str: Translated string
    """
    if lang is None:
        lang = REPORT_LANG
    
    try:
        return TRANSLATIONS.get(lang, TRANSLATIONS['he']).get(key, key)
    except Exception:
        return key


def get_current_time_hebrew() -> str:
    """
    קבלת זמן נוכחי בפורמט עברי
    Get current time in Hebrew format with proper timezone
    
    Returns:
        str: Formatted date/time string in Hebrew
    """
    try:
        # Get timezone
        tz = pytz.timezone(REPORT_TZ)
        now = datetime.now(tz)
        
        # Format in Hebrew style: DD/MM/YYYY HH:MM
        return now.strftime('%d/%m/%Y %H:%M')
    except Exception:
        # Fallback to system time
        return datetime.now().strftime('%d/%m/%Y %H:%M')


def get_hebrew_date_time_text() -> str:
    """
    קבלת טקסט תאריך ושעה בעברית
    Get Hebrew date/time text for report title
    
    Returns:
        str: Full Hebrew date/time text
    """
    current_time = get_current_time_hebrew()
    return f"{t('report_date')}: {current_time}"


def format_number_hebrew(num: float, decimal_places: int = 2) -> str:
    """
    עיצוב מספר בפורמט עברי
    Format number in Hebrew style
    
    Args:
        num: Number to format
        decimal_places: Number of decimal places
        
    Returns:
        str: Formatted number string
    """
    try:
        if pd.isna(num):
            return 'N/A'
        
        # Format with appropriate decimal places
        if decimal_places == 0:
            return f"{int(num):,}".replace(',', ' ')  # Use space as thousands separator
        else:
            return f"{num:,.{decimal_places}f}".replace(',', ' ')
    except:
        return str(num)


def get_chart_labels(chart_type: str) -> Dict[str, str]:
    """
    קבלת תוויות לתרשימים
    Get chart labels based on type
    
    Args:
        chart_type: Type of chart ('histogram', 'boxplot', 'bar', etc.)
        
    Returns:
        dict: Dictionary with chart labels
    """
    base_labels = {
        'xlabel': t('value'),
        'ylabel': t('frequency'),
        'title': t('distribution')
    }
    
    if chart_type == 'missing_values':
        base_labels.update({
            'xlabel': t('column'),
            'ylabel': t('missing_percentage'),
            'title': t('missing_values')
        })
    elif chart_type == 'categorical':
        base_labels.update({
            'xlabel': t('value'),
            'ylabel': t('count'),
            'title': t('categorical_distributions')
        })
    elif chart_type == 'boxplot':
        base_labels.update({
            'ylabel': t('value'),
            'title': t('boxplot')
        })
    
    return base_labels