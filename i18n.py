# -*- coding: utf-8 -*-
"""
Internationalization module for Hebrew Analytics Telegram Bot
Supports Hebrew (default) and English languages for PDF reports
"""

import os

# Get language preference from environment variable
REPORT_LANG = os.getenv('REPORT_LANG', 'he')

# Translation dictionaries
TRANSLATIONS = {
    'he': {
        # Report sections
        'table_of_contents': 'תוכן עניינים',
        'data_summary': 'סיכום נתונים',
        'column_analysis': 'ניתוח עמודות',
        'key_findings': 'תובנות עיקריות',
        'outlier_analysis': 'ניתוח ערכים חריגים',
        'recommendations': 'המלצות לשיפור',
        'charts_and_visualizations': 'תרשימים וויזואליזציות',
        'statistical_summary': 'סיכום סטטיסטי',
        
        # Report details
        'report_date': 'תאריך הדוח',
        'statistical_summary_subtitle': 'סיכום סטטיסטי של העמודות המספריות',
        
        # Title page
        'comprehensive_report_title': 'דוח ניתוח נתונים מקיף',
        'comprehensive_report_subtitle': 'ניתוח אוטומטי מלא של מערך הנתונים',
        'data_analysis_system': 'מערכת ניתוח נתונים',
        'auto_generated_report': 'דוח נוצר באופן אוטומטי על ידי מערכת ניתוח הנתונים',
        
        # Data analysis
        'missing_values': 'ערכים חסרים',
        'duplicate_rows': 'שורות כפולות',
        'no_duplicates': '✓ אין שורות כפולות',
        'data_dimensions': 'מימדי הנתונים',
        'memory_usage': 'שימוש בזיכרון',
        'data_types': 'סוגי נתונים',
        'columns': 'עמודות',
        'rows': 'שורות',
        'megabytes': 'מגה-בייט',
        
        # Statistics
        'statistics': 'סטטיסטיקות',
        'mean': 'ממוצע',
        'median': 'חציון',
        'std_dev': 'סטיית תקן',
        'minimum': 'מינימום',
        'maximum': 'מקסימום',
        'first_quartile': 'רבעון ראשון',
        'third_quartile': 'רבעון שלישי',
        'common_values': 'ערכים נפוצים',
        
        # Chart descriptions
        'chart': 'תרשים',
        'correlation_matrix': 'מטריצת קורלציות - מציגה את הקשרים בין העמודות המספריות',
        'missing_values_chart': 'ערכים חסרים - מציג את כמות הערכים החסרים בכל עמודה',
        'distributions_chart': 'התפלגויות - מציג את התפלגות הערכים בעמודות המספריות',
        'top_categories_chart': 'קטגוריות נפוצות - מציג את הערכים השכיחים ביותר',
        'data_visualization': 'תרשים נתונים'
    },
    
    'en': {
        # Report sections
        'table_of_contents': 'Table of Contents',
        'data_summary': 'Data Summary',
        'column_analysis': 'Column Analysis',
        'key_findings': 'Key Findings',
        'outlier_analysis': 'Outlier Analysis',
        'recommendations': 'Recommendations',
        'charts_and_visualizations': 'Charts and Visualizations',
        'statistical_summary': 'Statistical Summary',
        
        # Report details
        'report_date': 'Report Date',
        'statistical_summary_subtitle': 'Statistical summary of numeric columns',
        
        # Title page
        'comprehensive_report_title': 'Comprehensive Data Analysis Report',
        'comprehensive_report_subtitle': 'Complete automated analysis of the dataset',
        'data_analysis_system': 'Data Analysis System',
        'auto_generated_report': 'Report generated automatically by the data analysis system',
        
        # Data analysis
        'missing_values': 'Missing Values',
        'duplicate_rows': 'Duplicate Rows',
        'no_duplicates': '✓ No duplicate rows',
        'data_dimensions': 'Data Dimensions',
        'memory_usage': 'Memory Usage',
        'data_types': 'Data Types',
        'columns': 'columns',
        'rows': 'rows',
        'megabytes': 'MB',
        
        # Statistics
        'statistics': 'Statistics',
        'mean': 'Mean',
        'median': 'Median',
        'std_dev': 'Standard Deviation',
        'minimum': 'Minimum',
        'maximum': 'Maximum',
        'first_quartile': 'First Quartile',
        'third_quartile': 'Third Quartile',
        'common_values': 'Common Values',
        
        # Chart descriptions
        'chart': 'Chart',
        'correlation_matrix': 'Correlation Matrix - Shows relationships between numeric columns',
        'missing_values_chart': 'Missing Values - Shows amount of missing values per column',
        'distributions_chart': 'Distributions - Shows value distributions in numeric columns',
        'top_categories_chart': 'Top Categories - Shows most frequent values',
        'data_visualization': 'Data Chart'
    }
}

def t(key: str, lang: str = None) -> str:
    """
    Translation helper function
    
    Args:
        key: Translation key
        lang: Language code (he/en), uses REPORT_LANG if None
        
    Returns:
        Translated string or key if not found
    """
    if lang is None:
        lang = REPORT_LANG
    
    # Fallback to Hebrew if language not supported
    if lang not in TRANSLATIONS:
        lang = 'he'
    
    return TRANSLATIONS[lang].get(key, key)

def get_current_language() -> str:
    """Get current language setting"""
    return REPORT_LANG

def set_language(lang: str):
    """Set language for translations"""
    global REPORT_LANG
    if lang in TRANSLATIONS:
        REPORT_LANG = lang
        os.environ['REPORT_LANG'] = lang