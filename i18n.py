# -*- coding: utf-8 -*-
"""
Internationalization (i18n) module
Provides translation support with Hebrew as default language
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
import zoneinfo
import logging

logger = logging.getLogger(__name__)

# Translation dictionaries
TRANSLATIONS = {
    'he': {
        # Report sections
        'report_title': 'דוח ניתוח נתונים מקיף',
        'report_subtitle': 'ניתוח אוטומטי מלא של מערך הנתונים',
        'report_date': 'תאריך הדוח',
        'table_of_contents': 'תוכן עניינים',
        
        # Data preview section
        'data_preview': 'תצוגה מקדימה של הנתונים',
        'data_preview_subtitle': 'השורות הראשונות של מערך הנתונים',
        'data_shape': 'מבנה הנתונים',
        'rows_count': 'מספר שורות',
        'columns_count': 'מספר עמודות',
        
        # Missing values section
        'missing_values': 'ניתוח ערכים חסרים',
        'missing_values_subtitle': 'התפלגות ערכים חסרים בעמודות',
        'no_missing_values': 'אין ערכים חסרים במערך הנתונים',
        'missing_percentage': 'אחוז ערכים חסרים',
        'missing_count': 'כמות ערכים חסרים',
        
        # Categorical distributions section  
        'categorical_distributions': 'התפלגות נתונים קטגוריאליים',
        'categorical_distributions_subtitle': 'ניתוח עמודות קטגוריאליות וערכים נפוצים',
        'top_values': 'ערכים נפוצים',
        'value_counts': 'ספירת ערכים',
        'no_categorical_data': 'לא נמצאו עמודות קטגוריאליות מתאימות לניתוח',
        
        # Numeric distributions section
        'numeric_distributions': 'התפלגות נתונים מספריים', 
        'numeric_distributions_subtitle': 'היסטוגרמות ותרשימי קופסה לעמודות מספריות',
        'histogram': 'היסטוגרמה',
        'boxplot': 'תרשים קופסה',
        'no_numeric_data': 'לא נמצאו עמודות מספריות לניתוח',
        
        # Statistical summary section
        'statistical_summary': 'סיכום סטטיסטי',
        'statistical_summary_subtitle': 'סטטיסטיקות תיאוריות לעמודות מספריות',
        'descriptive_statistics': 'סטטיסטיקות תיאוריות',
        'count': 'כמות',
        'mean': 'ממוצע',
        'std': 'סטיית תקן',
        'min': 'מינימום',
        'max': 'מקסימום',
        'median': '50% (חציון)',
        'q25': '25% (רבעון ראשון)',
        'q75': '75% (רבעון שלישי)',
        
        # General terms
        'column': 'עמודה',
        'value': 'ערך',
        'frequency': 'תדירות',
        'percentage': 'אחוז',
        'total': 'סה"כ',
        'analysis': 'ניתוח',
        'insights': 'תובנות',
        'recommendations': 'המלצות',
        
        # Error messages  
        'error_processing_data': 'שגיאה בעיבוד הנתונים',
        'error_generating_chart': 'שגיאה ביצירת תרשים',
        'error_missing_data': 'לא נמצאו נתונים לניתוח',
        
        # Date formats
        'date_format': '%d/%m/%Y %H:%M',
        'date_format_short': '%d/%m/%Y',
    },
    
    'en': {
        # Report sections
        'report_title': 'Comprehensive Data Analysis Report',
        'report_subtitle': 'Complete Automated Analysis of Dataset',
        'report_date': 'Report Date',
        'table_of_contents': 'Table of Contents',
        
        # Data preview section
        'data_preview': 'Data Preview',
        'data_preview_subtitle': 'First rows of the dataset',
        'data_shape': 'Data Structure',
        'rows_count': 'Number of Rows',
        'columns_count': 'Number of Columns',
        
        # Missing values section
        'missing_values': 'Missing Values Analysis',
        'missing_values_subtitle': 'Distribution of missing values across columns',
        'no_missing_values': 'No missing values found in the dataset',
        'missing_percentage': 'Missing Percentage',
        'missing_count': 'Missing Count',
        
        # Categorical distributions section
        'categorical_distributions': 'Categorical Data Distributions',
        'categorical_distributions_subtitle': 'Analysis of categorical columns and common values',
        'top_values': 'Top Values',
        'value_counts': 'Value Counts',
        'no_categorical_data': 'No suitable categorical columns found for analysis',
        
        # Numeric distributions section
        'numeric_distributions': 'Numeric Data Distributions',
        'numeric_distributions_subtitle': 'Histograms and boxplots for numeric columns',
        'histogram': 'Histogram',
        'boxplot': 'Box Plot',
        'no_numeric_data': 'No numeric columns found for analysis',
        
        # Statistical summary section
        'statistical_summary': 'Statistical Summary',
        'statistical_summary_subtitle': 'Descriptive statistics for numeric columns',
        'descriptive_statistics': 'Descriptive Statistics',
        'count': 'Count',
        'mean': 'Mean',
        'std': 'Standard Deviation', 
        'min': 'Minimum',
        'max': 'Maximum',
        'median': '50% (Median)',
        'q25': '25% (First Quartile)',
        'q75': '75% (Third Quartile)',
        
        # General terms
        'column': 'Column',
        'value': 'Value',
        'frequency': 'Frequency',
        'percentage': 'Percentage',
        'total': 'Total',
        'analysis': 'Analysis',
        'insights': 'Insights',
        'recommendations': 'Recommendations',
        
        # Error messages
        'error_processing_data': 'Error processing data',
        'error_generating_chart': 'Error generating chart',
        'error_missing_data': 'No data found for analysis',
        
        # Date formats
        'date_format': '%d/%m/%Y %H:%M',
        'date_format_short': '%d/%m/%Y',
    }
}


def get_default_language() -> str:
    """
    Get default language from REPORT_LANG environment variable
    
    Returns:
        str: Language code (default: 'he')
    """
    return os.getenv('REPORT_LANG', 'he')


def get_timezone() -> zoneinfo.ZoneInfo:
    """
    Get timezone from REPORT_TZ environment variable
    
    Returns:
        zoneinfo.ZoneInfo: Timezone object (default: Asia/Jerusalem)
    """
    tz_name = os.getenv('REPORT_TZ', 'Asia/Jerusalem')
    try:
        return zoneinfo.ZoneInfo(tz_name)
    except Exception as e:
        logger.warning(f"Invalid timezone '{tz_name}', falling back to Asia/Jerusalem: {e}")
        return zoneinfo.ZoneInfo('Asia/Jerusalem')


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Get translated string for given key
    
    Args:
        key: Translation key
        lang: Language code (optional, uses default if not provided)
        **kwargs: Additional format arguments for string formatting
        
    Returns:
        str: Translated string, or key if translation not found
    """
    if lang is None:
        lang = get_default_language()
    
    # Get translation
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        translation = TRANSLATIONS[lang][key]
    elif 'he' in TRANSLATIONS and key in TRANSLATIONS['he']:
        # Fallback to Hebrew
        translation = TRANSLATIONS['he'][key]
        logger.debug(f"Translation key '{key}' not found for language '{lang}', using Hebrew fallback")
    else:
        # Fallback to key itself
        translation = key
        logger.warning(f"Translation key '{key}' not found for any language, using key as fallback")
    
    # Apply string formatting if kwargs provided
    try:
        if kwargs:
            translation = translation.format(**kwargs)
    except (KeyError, ValueError) as e:
        logger.warning(f"Error formatting translation '{key}' with args {kwargs}: {e}")
    
    return translation


def format_datetime(dt: datetime, lang: Optional[str] = None, include_time: bool = True) -> str:
    """
    Format datetime according to language preferences and timezone
    
    Args:
        dt: Datetime object to format
        lang: Language code (optional, uses default if not provided)
        include_time: Whether to include time in format
        
    Returns:
        str: Formatted datetime string
    """
    if lang is None:
        lang = get_default_language()
    
    # Convert to report timezone if needed
    tz = get_timezone()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=zoneinfo.ZoneInfo('UTC'))
    dt_local = dt.astimezone(tz)
    
    # Get appropriate format
    format_key = 'date_format' if include_time else 'date_format_short'
    date_format = t(format_key, lang)
    
    try:
        return dt_local.strftime(date_format)
    except Exception as e:
        logger.warning(f"Error formatting datetime with format '{date_format}': {e}")
        # Fallback format
        return dt_local.strftime('%d/%m/%Y %H:%M' if include_time else '%d/%m/%Y')


def get_current_datetime_formatted(lang: Optional[str] = None, include_time: bool = True) -> str:
    """
    Get current datetime formatted according to language and timezone preferences
    
    Args:
        lang: Language code (optional, uses default if not provided)
        include_time: Whether to include time in format
        
    Returns:
        str: Formatted current datetime
    """
    return format_datetime(datetime.now(), lang, include_time)


def add_translation(lang: str, key: str, value: str) -> None:
    """
    Add or update a translation
    
    Args:
        lang: Language code
        key: Translation key
        value: Translation value
    """
    if lang not in TRANSLATIONS:
        TRANSLATIONS[lang] = {}
    
    TRANSLATIONS[lang][key] = value
    logger.debug(f"Added translation for '{key}' in language '{lang}'")


def get_available_languages() -> list:
    """
    Get list of available language codes
    
    Returns:
        list: List of available language codes
    """
    return list(TRANSLATIONS.keys())


def validate_translations() -> Dict[str, Any]:
    """
    Validate translation completeness across languages
    
    Returns:
        dict: Validation report with missing translations
    """
    report = {
        'complete': True,
        'missing_keys': {},
        'total_keys': 0,
        'languages': list(TRANSLATIONS.keys())
    }
    
    # Get all keys from all languages
    all_keys = set()
    for lang_dict in TRANSLATIONS.values():
        all_keys.update(lang_dict.keys())
    
    report['total_keys'] = len(all_keys)
    
    # Check each language for missing keys
    for lang in TRANSLATIONS:
        missing = all_keys - set(TRANSLATIONS[lang].keys())
        if missing:
            report['complete'] = False
            report['missing_keys'][lang] = list(missing)
    
    return report


# Initialize logging for this module
logger.info(f"i18n module initialized with default language: {get_default_language()}")
logger.info(f"Available languages: {', '.join(get_available_languages())}")