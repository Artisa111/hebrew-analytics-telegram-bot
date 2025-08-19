# -*- coding: utf-8 -*-
"""
Internationalization module with Hebrew text support
Default language from REPORT_LANG environment variable
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Hebrew text keys for report sections and messages
HEBREW_TEXTS = {
    # Report sections
    "report_title": "דוח ניתוח נתונים מקיף",
    "report_subtitle": "ניתוח אוטומטי מלא של מערך הנתונים",
    "report_date": "תאריך הדוח",
    
    # Table of contents
    "table_of_contents": "תוכן עניינים",
    "data_preview": "תצוגה מקדימה של הנתונים",
    "missing_values": "ניתוח ערכים חסרים",
    "categorical_distributions": "התפלגויות קטגוריות",
    "numeric_distributions": "התפלגויות מספריות",
    "statistical_summary": "סיכום סטטיסטי",
    "outliers_analysis": "ניתוח ערכים חריגים",
    "recommendations": "המלצות לשיפור",
    "charts_visualizations": "תרשימים וויזואליזציות",
    
    # Data preview section
    "data_preview_title": "תצוגה מקדימה של הנתונים",
    "data_preview_description": "השורות הראשונות מהנתונים:",
    "data_shape": "מימדי הנתונים",
    "rows": "שורות",
    "columns": "עמודות",
    "memory_usage": "שימוש בזיכרון",
    "megabytes": "מגה-בייט",
    
    # Missing values section
    "missing_values_title": "ניתוח ערכים חסרים",
    "no_missing_values": "✅ מעולה! אין ערכים חסרים בנתונים",
    "missing_values_found": "נמצאו ערכים חסרים בעמודות הבאות:",
    "missing_count": "מספר ערכים חסרים",
    "missing_percentage": "אחוז מהנתונים",
    "total_missing": "סך הכל ערכים חסרים",
    
    # Categorical distributions section
    "categorical_title": "התפלגויות קטגוריות",
    "categorical_description": "ניתוח העמודות הקטגוריאליות:",
    "top_values": "ערכים נפוצים ביותר",
    "unique_values": "ערכים ייחודיים",
    "no_categorical_data": "לא נמצאו עמודות קטגוריות בנתונים",
    "other_values": "אחר",
    
    # Numeric distributions section
    "numeric_title": "התפלגויות מספריות",
    "numeric_description": "ניתוח העמודות המספריות:",
    "no_numeric_data": "לא נמצאו עמודות מספריות בנתונים",
    "statistics": "סטטיסטיקות",
    "mean": "ממוצע",
    "median": "חציון", 
    "std": "סטיית תקן",
    "min": "מינימום",
    "max": "מקסימום",
    "q25": "רבעון ראשון",
    "q75": "רבעון שלישי",
    
    # Statistical summary section
    "stats_summary_title": "סיכום סטטיסטי מקיף",
    "stats_summary_description": "תקציר סטטיסטי של כל העמודות המספריות:",
    "data_types_summary": "סיכום סוגי הנתונים",
    "numeric_columns": "עמודות מספריות",
    "categorical_columns": "עמודות קטגוריות",
    "datetime_columns": "עמודות תאריך",
    
    # Outliers section
    "outliers_title": "ניתוח ערכים חריגים",
    "outliers_description": "זיהוי ערכים חריגים לפי שיטת IQR:",
    "no_outliers_found": "✅ לא זוהו ערכים חריגים באמצעות שיטת IQR",
    "outliers_found": "זוהו ערכים חריגים בעמודות הבאות:",
    "outliers_count": "מספר ערכים חריגים",
    "outliers_percentage": "אחוז מהנתונים",
    "outlier_range": "טווח תקין",
    "outlier_warning": "⚠️ אחוז גבוה של ערכים חריגים - מומלץ לבדוק",
    
    # Recommendations section  
    "recommendations_title": "המלצות לשיפור הנתונים",
    "data_quality_recs": "המלצות לאיכות נתונים:",
    "analysis_recs": "המלצות לניתוח מתקדם:",
    "general_recs": "עקרונות כלליים:",
    
    # Enhanced recommendations with detailed Hebrew text
    "high_missing_data": "🎯 אחוז גבוה מאוד של ערכים חסרים ({pct:.1f}%) - בדוק את מקור הנתונים ושקול שיפור תהליכי איסוף הנתונים",
    "medium_missing_data": "🎯 אחוז בינוני של ערכים חסרים ({pct:.1f}%) - שקול השלמת נתונים באמצעות ממוצע, חציון או מודלים חזויים",
    "low_missing_data": "✅ אחוז נמוך של ערכים חסרים ({pct:.1f}%) - נתונים באיכות טובה, ניתן להמשיך בניתוח",
    "duplicate_rows_high": "🎯 אחוז גבוה של שורות כפולות ({pct:.1f}%) - מומלץ לנקות כפילויות לפני המשך הניתוח",
    "duplicate_rows_low": "🎯 נמצאו מעט שורות כפולות ({count}) - בדוק אם הן רלוונטיות או שגיאות במערכת",
    "high_outliers": "🎯 עמודות עם ערכים חריגים רבים: {cols} - בדוק אם מדובר בשגיאות נתונים או תופעות אמיתיות",
    "low_outliers": "🎯 ערכים חריגים מעטים זוהו - בדוק ידנית ושקול האם להשאיר או להסיר לפי הקשר העסקי",
    
    # Data size and performance recommendations
    "small_dataset": "⚠️ מערך נתונים קטן ({rows} שורות) - תוצאות הניתוח עלולות להיות לא יציבות, שקול איסוף נתונים נוספים",
    "large_dataset": "💡 מערך נתונים גדול ({rows:,} שורות) - שקול דגימה אקראית לבדיקות מהירות ואופטימיזציה של ביצועים",
    "many_columns": "💡 מספר עמודות רב ({cols}) - שקול בחירת תכונות (Feature Selection) לפני בניית מודלים",
    "high_memory": "💡 שימוש גבוה בזיכרון ({mb:.0f}MB) - שקול אופטימיזציה של סוגי נתונים ועיבוד בחלקים",
    
    # Correlation insights
    "high_correlations": "🎯 נמצאו קורלציות גבוהות מאוד - שקול הסרת עמודות מיותרות למניעת רב-קווטיות במודלים",
    "medium_correlations": "💡 נמצאו קורלציות חזקות - בדוק קשרים סיבתיים או זהה תופעות עסקיות מעניינות",
    
    # Best practices with detailed explanations
    "check_data_quality": "💡 בדוק תמיד את איכות הנתונים לפני ביצוע ניתוח מתקדם - זה חוסך זמן ומבטיח תוצאות מדויקות",
    "backup_original": "💡 שמור גרסת גיבוי של הנתונים המקוריים לפני ביצוע שינויים - זה מאפשר חזרה למצב הקודם במקרה הצורך",
    "document_changes": "💡 תעד את כל השינויים שביצעת בנתונים לשחזור עתידי - זה חיוני לשקיפות ולחזרה על התהליך",
    "validate_assumptions": "💡 בדוק הנחות הניתוח שלך מול התוצאות שקיבלת - זה מבטיח שהמסקנות נכונות ורלוונטיות",
    "use_visualizations": "💡 השתמש בויזואליזציות להבנה טובה יותר של הנתונים - גרפים חושפים דפוסים שקשה לזהות בטבלאות",
    
    # Data quality recommendations
    # Chart descriptions with more detail
    "correlation_chart": "מטריצת קורלציות - מציגה את עוצמת הקשרים הליניאריים בין עמודות מספריות. ערכים קרובים ל-1 או -1 מעידים על קשר חזק",
    "missing_values_chart": "ערכים חסרים - מציג את כמות הערכים החסרים בכל עמודה. עמודות עם ערכים חסרים רבים עלולות להשפיע על איכות הניתוח",
    "distributions_chart": "התפלגויות - מציג את התפלגות הערכים בעמודות המספריות. עוזר לזהות התפלגויות נורמליות, מוטות או דו-מודליות",
    "categories_chart": "קטגוריות נפוצות - מציג את הערכים השכיחים ביותר בעמודות קטגוריות. עוזר לזהות דפוסים ואי-איזונים בנתונים",
    "outliers_chart": "ערכים חריגים - זיהוי וויזואליזציה של ערכים חריגים באמצעות שיטת IQR. עוזר לזהות שגיאות או תופעות חריגות",
    
    # Enhanced insights with business context
    "data_completeness_excellent": "✅ שלמות נתונים מעולה - הנתונים מוכנים לניתוח מתקדם ובניית מודלים",
    "data_completeness_good": "✅ שלמות נתונים טובה - ניתן להמשיך בניתוח עם טיפול מינימלי בערכים חסרים",
    "data_completeness_fair": "⚠️ שלמות נתונים בינונית - מומלץ לטפל בערכים חסרים לפני ניתוח מתקדם",
    "data_completeness_poor": "❌ שלמות נתונים נמוכה - נדרש טיפול מקיף בערכים חסרים או איסוף נתונים נוספים",
    
    # Business insights
    "business_insight_variability": "📊 העמודה '{col}' מציגה שונות גבוהה - זה עשוי להצביע על הזדמנויות עסקיות או אזורי סיכון",
    "business_insight_stability": "📊 העמודה '{col}' מציגה יציבות גבוהה - זה מעיד על עקביות בתהליכים העסקיים",
    "business_insight_growth": "📈 זוהתה מגמת צמיחה בנתונים - זה עשוי להצביע על הצלחה או שיפור בביצועים",
    "business_insight_decline": "📉 זוהתה מגמת ירידה בנתונים - מומלץ לבחון את הגורמים ולפתח אסטרטגיית התמודדות",
    
    # Advanced analysis suggestions
    "suggest_regression": "🔬 מומלץ לבצע ניתוח רגרסיה לזיהוי גורמים משפיעים על המשתנה התלוי",
    "suggest_clustering": "🔬 מומלץ לבצע ניתוח אשכולות (Clustering) לזיהוי קבוצות דומות בנתונים",
    "suggest_time_series": "🔬 זוהו נתוני זמן - מומלץ לבצע ניתוח מגמות ועונתיות",
    "suggest_ab_testing": "🔬 מומלץ לבצע בדיקות A/B להשוואה בין קבוצות שונות",
    "suggest_anomaly_detection": "🔬 מומלץ לבצע זיהוי אנומליות לאיתור תופעות חריגות",
    
    # Data quality scores
    "data_quality_score": "ציון איכות נתונים: {score}/100",
    "data_quality_excellent": "🌟 איכות נתונים מעולה (90-100) - הנתונים מוכנים לכל סוג ניתוח",
    "data_quality_good": "✅ איכות נתונים טובה (70-89) - הנתונים מתאימים לרוב סוגי הניתוח",
    "data_quality_fair": "⚠️ איכות נתונים בינונית (50-69) - נדרש טיפול בבעיות איכות לפני ניתוח מתקדם",
    "data_quality_poor": "❌ איכות נתונים נמוכה (מתחת ל-50) - נדרש טיפול מקיף לפני כל ניתוח"
    
    # Error messages
    "error_no_data": "❌ אין נתונים לעיבוד",
    "error_empty_data": "❌ הנתונים ריקים או לא תקינים", 
    "error_processing": "❌ שגיאה בעיבוד הנתונים",
    "error_chart_creation": "❌ שגיאה ביצירת תרשים",
    
    # Success messages
    "processing_complete": "✅ העיבוד הושלם בהצלחה",
    "chart_created": "📊 תרשים נוצר בהצלחה",
    "analysis_complete": "🎉 הניתוח הושלם בהצלחה",
    
    # Generic terms
    "column": "עמודה",
    "value": "ערך",
    "count": "כמות",
    "percentage": "אחוז",
    "total": "סך הכל",
    "average": "ממוצע",
    "frequency": "תדירות",
    "distribution": "התפלגות",
}

# English fallback texts for missing keys
ENGLISH_TEXTS = {
    "report_title": "Comprehensive Data Analysis Report",
    "report_subtitle": "Complete Automated Analysis of the Dataset",
    "report_date": "Report Date",
    "no_missing_values": "✅ Excellent! No missing values in the data",
    "error_no_data": "❌ No data to process",
    "processing_complete": "✅ Processing completed successfully",
}


def get_default_language() -> str:
    """Get default language from environment variable"""
    return os.getenv('REPORT_LANG', 'he')


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Get translated text by key
    
    Args:
        key: Text key to look up
        lang: Language code (defaults to REPORT_LANG env var or 'he')
        **kwargs: Format parameters for string formatting
        
    Returns:
        Translated text with formatting applied
    """
    if lang is None:
        lang = get_default_language()
    
    # Select text dictionary based on language
    if lang == 'he':
        texts = HEBREW_TEXTS
        fallback_texts = ENGLISH_TEXTS
    else:
        texts = ENGLISH_TEXTS
        fallback_texts = HEBREW_TEXTS
    
    # Get text, fallback to English if not found, then to key itself
    text = texts.get(key, fallback_texts.get(key, key))
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Error formatting text key '{key}': {e}")
            # Return unformatted text on error
    
    return text


def get_timezone() -> str:
    """Get report timezone from environment variable"""
    return os.getenv('REPORT_TZ', 'Asia/Jerusalem')


def format_date_time(dt=None) -> str:
    """Format datetime according to Hebrew conventions (DD/MM/YYYY HH:MM)"""
    if dt is None:
        from datetime import datetime
        try:
            # Try to use specified timezone
            tz_name = get_timezone()
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo(tz_name)
                dt = datetime.now(tz)
            except (ImportError, Exception):
                # Fallback to system timezone
                logger.debug(f"Could not use timezone {tz_name}, using system timezone")
                dt = datetime.now()
        except Exception:
            dt = datetime.now()
    
    return dt.strftime("%d/%m/%Y %H:%M")


# Convenience functions for common translations
def section_title(section_key: str) -> str:
    """Get section title by key"""
    return t(section_key)


def error_message(error_key: str) -> str:
    """Get error message by key"""
    return t(error_key)


def success_message(success_key: str) -> str:
    """Get success message by key"""
    return t(success_key)