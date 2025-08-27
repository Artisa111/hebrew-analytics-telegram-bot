# -*- coding: utf-8 -*-
"""
מודול יצירת דוחות PDF עם תמיכה מלאה בעברית מימין לשמאל
PDF report generation module with full Hebrew RTL support
PRODUCTION VERSION - NO DEMO DATA
"""

from fpdf import FPDF
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import logging
import os
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io
import numpy as np
from scipy import stats
import arabic_reshaper
from bidi.algorithm import get_display
import warnings

warnings.filterwarnings('ignore')

# Configure matplotlib for Hebrew
plt.rcParams['font.family'] = ['Noto Sans Hebrew', 'DejaVu Sans', 'Arial Unicode MS', 'Arial', 'Tahoma']

logger = logging.getLogger(__name__)

class HebrewPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        self.setup_hebrew_support()
        self.current_y = 0
        self.page_width = 210
        self.page_height = 297
        self.margin = 20
        self.rtl_support = True
    
    def _fix_hebrew_text(self, text: str) -> str:
        """תיקון טקסט עברי לתצוגה נכונה מימין לשמאל"""
        try:
            if not text:
                return ""
            
            # Handle mixed Hebrew-English text
            if any('\u0590' <= char <= '\u05FF' for char in text):
                # Reshape Arabic/Hebrew characters
                reshaped_text = arabic_reshaper.reshape(text)
                # Apply bidirectional algorithm
                bidi_text = get_display(reshaped_text)
                return bidi_text
            return text
        except Exception as e:
            logger.warning(f"Error fixing Hebrew text: {e}")
            return text

    def _fix_list(self, values) -> list:
        """Apply Hebrew fix to a sequence of strings for tick labels."""
        try:
            return [self._fix_hebrew_text(str(v)) for v in list(values)]
        except Exception:
            return [str(v) for v in list(values)]
    
    def setup_hebrew_support(self):
        """הגדרת תמיכה מלאה בעברית ל-PDF"""
        try:
            # Font paths for different operating systems
            font_paths = {
                'windows': [
                    'C:/Windows/Fonts/arial.ttf',
                    'C:/Windows/Fonts/arialbd.ttf',
                    'C:/Windows/Fonts/calibri.ttf',
                    'C:/Windows/Fonts/calibrib.ttf'
                ],
                'linux': [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
                ],
                'mac': [
                    '/System/Library/Fonts/Arial.ttf',
                    '/System/Library/Fonts/Arial Bold.ttf',
                    '/Library/Fonts/Arial.ttf'
                ]
            }
            
            regular_font = None
            bold_font = None
            
            # Detect OS and try to load fonts
            for os_type, paths in font_paths.items():
                for path in paths:
                    if os.path.exists(path):
                        if 'bold' in path.lower() or 'bd' in path.lower():
                            if bold_font is None:
                                bold_font = path
                        else:
                            if regular_font is None:
                                regular_font = path
                        
                        if regular_font and bold_font:
                            break
                if regular_font and bold_font:
                    break
            
            # Add fonts to PDF
            if regular_font:
                self.pdf.add_font('Hebrew', '', regular_font, uni=True)
                if bold_font:
                    self.pdf.add_font('Hebrew', 'B', bold_font, uni=True)
                else:
                    self.pdf.add_font('Hebrew', 'B', regular_font, uni=True)
                
                self.pdf.set_font('Hebrew', '', 12)
                logger.info("Hebrew fonts loaded successfully")
            else:
                # Fallback to core fonts
                self.pdf.set_font('Arial', '', 12)
                logger.warning("Using fallback font - Hebrew support may be limited")
            
            self.pdf.set_auto_page_break(auto=True, margin=15)
            self.pdf.set_margins(self.margin, self.margin, self.margin)
            
        except Exception as e:
            logger.error(f"Error setting up Hebrew support: {e}")
            self.pdf.set_font('Arial', '', 12)
    
    def _get_text_width(self, text: str) -> float:
        """חישוב רוחב טקסט"""
        try:
            return self.pdf.get_string_width(text)
        except:
            return len(text) * 2  # Rough estimation
    
    def _add_rtl_text(self, x: float, y: float, text: str, align: str = 'R'):
        """הוספת טקסט מימין לשמאל"""
        try:
            fixed_text = self._fix_hebrew_text(text)
            
            if align == 'R':
                # Right align - calculate x position from right margin
                text_width = self._get_text_width(fixed_text)
                x_pos = self.page_width - self.margin - text_width
            elif align == 'C':
                # Center align
                text_width = self._get_text_width(fixed_text)
                x_pos = (self.page_width - text_width) / 2
            else:
                # Left align
                x_pos = x
            
            self.pdf.text(x_pos, y, fixed_text)
            
        except Exception as e:
            logger.error(f"Error adding RTL text: {e}")
            self.pdf.text(x, y, text)
    
    def create_title_page(self, title: str, subtitle: str = None, 
                         company: str = "מערכת ניתוח נתונים", date: str = None):
        """יצירת דף כותרת מעוצב"""
        try:
            self.pdf.add_page()
            
            # Add company logo area (placeholder)
            self.pdf.set_fill_color(230, 230, 250)
            self.pdf.rect(70, 30, 70, 25, 'F')
            
            # Main title
            self.pdf.set_font('Hebrew', 'B', 24)
            self._add_rtl_text(0, 80, title, 'C')
            
            # Subtitle
            if subtitle:
                self.pdf.set_font('Hebrew', '', 16)
                self._add_rtl_text(0, 100, subtitle, 'C')
            
            # Company name
            self.pdf.set_font('Hebrew', 'B', 14)
            self._add_rtl_text(0, 120, company, 'C')
            
            # Date
            if date is None:
                try:
                    date_dt = datetime.now(ZoneInfo("Asia/Jerusalem")) if ZoneInfo else datetime.now()
                except Exception:
                    date_dt = datetime.now()
                date = date_dt.strftime("%d/%m/%Y %H:%M")
            
            self.pdf.set_font('Hebrew', '', 12)
            date_text = f"תאריך הדוח: {date}"
            self._add_rtl_text(0, 140, date_text, 'C')
            
            # Decorative lines
            self.pdf.set_line_width(0.5)
            self.pdf.line(30, 160, 180, 160)
            self.pdf.line(30, 162, 180, 162)
            
            # Page info
            self.pdf.set_font('Hebrew', '', 10)
            page_info = "דוח נוצר באופן אוטומטי על ידי מערכת ניתוח הנתונים"
            self._add_rtl_text(0, 260, page_info, 'C')
            
            self.current_y = 180
            
        except Exception as e:
            logger.error(f"Error creating title page: {e}")
    
    def add_section_header(self, title: str, level: int = 1):
        """הוספת כותרת סעיף עם עיצוב"""
        try:
            # Check if new page needed
            if self.current_y > self.page_height - 50:
                self.pdf.add_page()
                self.current_y = self.margin + 10
            
            # Add spacing before header
            if level == 1:
                self.current_y += 15
                self.pdf.set_font('Hebrew', 'B', 18)
                # Add background color for main headers
                self.pdf.set_fill_color(245, 245, 255)
                self.pdf.rect(self.margin, self.current_y - 5, 
                             self.page_width - 2 * self.margin, 12, 'F')
            elif level == 2:
                self.current_y += 12
                self.pdf.set_font('Hebrew', 'B', 14)
            else:
                self.current_y += 8
                self.pdf.set_font('Hebrew', 'B', 12)
            
            # Add header text
            self._add_rtl_text(0, self.current_y, title, 'R')
            
            # Add underline for level 1 headers
            if level == 1:
                y_line = self.current_y + 2
                self.pdf.line(self.margin, y_line, self.page_width - self.margin, y_line)
            
            self.current_y += 15
            
        except Exception as e:
            logger.error(f"Error adding section header: {e}")
    
    def add_text(self, text: str, font_size: int = 12, bold: bool = False, 
                 indent: int = 0):
        """הוספת טקסט עם תמיכה מלאה ב-RTL"""
        try:
            # Normalize inputs to avoid NoneType issues
            if text is None:
                text = ""
            if not isinstance(text, str):
                text = str(text)
            try:
                font_size = float(font_size) if font_size is not None else 12.0
            except Exception:
                font_size = 12.0
            try:
                indent = float(indent) if indent is not None else 0.0
            except Exception:
                indent = 0.0
            
            # Set font
            if bold:
                self.pdf.set_font('Hebrew', 'B', font_size)
            else:
                self.pdf.set_font('Hebrew', '', font_size)
            
            # Check if new page needed
            if self.current_y > self.page_height - 30:
                self.pdf.add_page()
                self.current_y = self.margin + 10
            
            # Handle long text - wrap lines
            max_width = self.page_width - 2 * self.margin - indent
            lines = self._wrap_text_rtl(text, max_width)
            
            for line in lines:
                if line.strip():  # Skip empty lines
                    self._add_rtl_text(indent, self.current_y, line.strip(), 'R')
                self.current_y += font_size * 0.4 + 2
            
            self.current_y += 3
            
        except Exception as e:
            logger.error(f"Error adding text: {e}")
    
    def _wrap_text_rtl(self, text: str, max_width: float) -> List[str]:
        """חלוקת טקסט ארוך לשורות עם תמיכה ב-RTL"""
        try:
            if text is None:
                text = ""
            if not isinstance(text, str):
                text = str(text)
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = f"{current_line} {word}" if current_line else word
                if self._get_text_width(test_line) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            return lines
            
        except Exception as e:
            logger.error(f"Error wrapping text: {e}")
            return [text]
    
    def analyze_real_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח מקיף של נתונים אמיתיים"""
        try:
            analysis_results = {}
            
            # Basic information
            basic_info = {
                'shape': df.shape,
                'memory_usage': df.memory_usage(deep=True).sum(),
                'dtypes': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            # Column details
            column_details = {}
            for col in df.columns:
                col_info = {
                    'type': str(df[col].dtype),
                    'unique_values': df[col].nunique(),
                    'null_count': df[col].isnull().sum(),
                    'null_percentage': round((df[col].isnull().sum() / len(df)) * 100, 2)
                }
                
                # Statistical analysis for numeric columns
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    col_info.update({
                        'mean': round(df[col].mean(), 2),
                        'median': round(df[col].median(), 2),
                        'std': round(df[col].std(), 2),
                        'min': round(df[col].min(), 2),
                        'max': round(df[col].max(), 2),
                        'q25': round(df[col].quantile(0.25), 2),
                        'q75': round(df[col].quantile(0.75), 2)
                    })
                
                # Analysis for categorical columns
                elif df[col].dtype == 'object':
                    col_info.update({
                        'top_values': df[col].value_counts().head(5).to_dict(),
                        'unique_ratio': round(df[col].nunique() / len(df), 3)
                    })
                
                column_details[col] = col_info
            
            basic_info['column_details'] = column_details
            analysis_results['basic_info'] = basic_info
            
            # Correlation analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                analysis_results['correlation_matrix'] = corr_matrix
                
                # Find strong correlations
                strong_correlations = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.5:  # Strong correlation threshold
                            strong_correlations.append({
                                'column1': corr_matrix.columns[i],
                                'column2': corr_matrix.columns[j],
                                'correlation': round(corr_val, 3)
                            })
                
                analysis_results['strong_correlations'] = strong_correlations
            
            # Generate insights
            insights = self._generate_insights(df, analysis_results)
            analysis_results['insights'] = insights
            
            # Outlier detection
            outliers = self._detect_outliers(df)
            analysis_results['outliers'] = outliers
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return {'error': str(e)}
    
    def _generate_insights(self, df: pd.DataFrame, analysis: Dict) -> List[str]:
        """יצירת תובנות אוטומטיות מהנתונים"""
        insights = []
        
        try:
            # Data size insights
            rows, cols = df.shape
            insights.append(f"הנתונים מכילים {rows:,} שורות ו-{cols} עמודות")
            
            # Missing data insights
            total_nulls = df.isnull().sum().sum()
            if total_nulls > 0:
                null_pct = (total_nulls / (rows * cols)) * 100
                insights.append(f"אחוז הערכים החסרים: {null_pct:.1f}%")
            else:
                insights.append("הנתונים שלמים - אין ערכים חסרים")
            
            # Data types insights
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            categorical_cols = len(df.select_dtypes(include=['object']).columns)
            datetime_cols = len(df.select_dtypes(include=['datetime64']).columns)
            
            insights.append(f"עמודות מספריות: {numeric_cols}, קטגוריאליות: {categorical_cols}, תאריכים: {datetime_cols}")
            
            # Duplicates insight
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                insights.append(f"נמצאו {duplicates} שורות כפולות")
            
            # Correlation insights
            if 'strong_correlations' in analysis and analysis['strong_correlations']:
                strong_corr_count = len(analysis['strong_correlations'])
                insights.append(f"נמצאו {strong_corr_count} קורלציות חזקות בין עמודות")
            
            # Outliers insights
            if 'outliers' in analysis:
                outlier_cols = len([col for col, outliers in analysis['outliers'].items() if outliers > 0])
                if outlier_cols > 0:
                    insights.append(f"זוהו ערכים חריגים ב-{outlier_cols} עמודות")
            
            # Data distribution insights
            for col in df.select_dtypes(include=[np.number]).columns:
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    direction = "ימינה" if skewness > 0 else "שמאלה"
                    insights.append(f"עמודה '{col}' מוטה {direction} (skewness: {skewness:.2f})")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append("שגיאה ביצירת תובנות")
        
        return insights
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, int]:
        """זיהוי ערכים חריגים"""
        outliers = {}
        
        try:
            for col in df.select_dtypes(include=[np.number]).columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_count = len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
                outliers[col] = outlier_count
                
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
        
        return outliers
    
    def add_data_summary(self, basic_info: Dict[str, Any]):
        """הוספת סיכום נתונים מפורט"""
        try:
            self.add_section_header("סיכום נתונים", 1)
            
            # Data dimensions
            if 'shape' in basic_info:
                rows, cols = basic_info['shape']
                self.add_text(f"מימדי הנתונים: {rows:,} שורות × {cols} עמודות", 12, bold=True)
            
            # Memory usage
            if 'memory_usage' in basic_info:
                memory_mb = basic_info['memory_usage'] / (1024 * 1024)
                self.add_text(f"שימוש בזיכרון: {memory_mb:.2f} מגה-בייט", 12)
            
            # Data types summary
            if 'dtypes' in basic_info:
                dtype_counts = {}
                for dtype in basic_info['dtypes'].values():
                    dtype_str = str(dtype)
                    dtype_counts[dtype_str] = dtype_counts.get(dtype_str, 0) + 1
                
                self.add_text("סוגי נתונים:", 12, bold=True)
                for dtype, count in dtype_counts.items():
                    self.add_text(f"  {dtype}: {count} עמודות", 11, indent=10)
            
            # Missing values
            if 'null_counts' in basic_info:
                total_nulls = sum(basic_info['null_counts'].values())
                if total_nulls > 0:
                    self.add_text(f"סך ערכים חסרים: {total_nulls:,}", 12, bold=True)
                    # Show columns with missing values
                    for col, null_count in basic_info['null_counts'].items():
                        if null_count > 0:
                            pct = (null_count / basic_info['shape'][0]) * 100
                            self.add_text(f"  {col}: {null_count:,} ({pct:.1f}%)", 11, indent=10)
                else:
                    self.add_text("✓ אין ערכים חסרים בנתונים", 12, bold=True)
            
            # Duplicates
            if 'duplicate_rows' in basic_info:
                dup_count = basic_info['duplicate_rows']
                if dup_count > 0:
                    dup_pct = (dup_count / basic_info['shape'][0]) * 100
                    self.add_text(f"שורות כפולות: {dup_count} ({dup_pct:.1f}%)", 12, bold=True)
                else:
                    self.add_text("✓ אין שורות כפולות", 12, bold=True)
            
        except Exception as e:
            logger.error(f"Error adding data summary: {e}")
    
    def add_column_analysis(self, column_details: Dict[str, Any]):
        """ניתוח מפורט של עמודות"""
        try:
            self.add_section_header("ניתוח עמודות", 1)
            
            for col_name, col_info in column_details.items():
                self.add_section_header(f"עמודה: {col_name}", 2)
                
                # Basic info
                self.add_text(f"סוג נתונים: {col_info['type']}", 11, indent=5)
                self.add_text(f"ערכים ייחודיים: {col_info['unique_values']:,}", 11, indent=5)
                
                # Null values
                if col_info['null_count'] > 0:
                    self.add_text(f"ערכים חסרים: {col_info['null_count']:,} ({col_info['null_percentage']}%)", 
                                11, indent=5)
                
                # Numeric column statistics
                if 'mean' in col_info:
                    self.add_text("סטטיסטיקות:", 11, bold=True, indent=5)
                    self.add_text(f"ממוצע: {col_info['mean']}", 10, indent=15)
                    self.add_text(f"חציון: {col_info['median']}", 10, indent=15)
                    self.add_text(f"סטיית תקן: {col_info['std']}", 10, indent=15)
                    self.add_text(f"מינימום: {col_info['min']}", 10, indent=15)
                    self.add_text(f"מקסימום: {col_info['max']}", 10, indent=15)
                    self.add_text(f"רבעון ראשון: {col_info['q25']}", 10, indent=15)
                    self.add_text(f"רבעון שלישי: {col_info['q75']}", 10, indent=15)
                
                # Categorical column analysis
                elif 'top_values' in col_info:
                    self.add_text("ערכים נפוצים:", 11, bold=True, indent=5)
                    for value, count in col_info['top_values'].items():
                        self.add_text(f"{value}: {count}", 10, indent=15)
                    
                    if col_info['unique_ratio'] < 0.05:
                        self.add_text("עמודה קטגורית עם ערכים מעטים", 10, indent=5)
                    elif col_info['unique_ratio'] > 0.95:
                        self.add_text("עמודה עם ערכים ייחודיים רבים (כמעט מזהה)", 10, indent=5)
        
        except Exception as e:
            logger.error(f"Error adding column analysis: {e}")
    
    def add_insights_section(self, insights: List[str]):
        """הוספת סעיף תובנות"""
        try:
            self.add_section_header("תובנות עיקריות", 1)
            
            for i, insight in enumerate(insights, 1):
                bullet = "•" if i <= 10 else f"{i}."
                self.add_text(f"{bullet} {insight}", 12, indent=5)
        
        except Exception as e:
            logger.error(f"Error adding insights: {e}")
    
    def add_correlation_section(self, strong_correlations: List[Dict]):
        """הוספת ניתוח קורלציות"""
        try:
            self.add_section_header("ניתוח קורלציות", 1)
            
            if strong_correlations:
                self.add_text("קורלציות חזקות שנמצאו:", 12, bold=True)
                
                for corr in strong_correlations:
                    strength = "חזקה מאוד" if abs(corr['correlation']) > 0.8 else "חזקה"
                    direction = "חיובית" if corr['correlation'] > 0 else "שלילית"
                    
                    corr_text = f"• {corr['column1']} ↔ {corr['column2']}"
                    self.add_text(corr_text, 11, indent=5)
                    self.add_text(f"  עוצמה: {strength} {direction} ({corr['correlation']:.3f})", 10, indent=15)
            else:
                self.add_text("לא נמצאו קורלציות חזקות (מעל 0.5) בין העמודות המספריות", 12)
        
        except Exception as e:
            logger.error(f"Error adding correlation section: {e}")
    
    def add_outliers_section(self, outliers: Dict[str, int]):
        """הוספת ניתוח ערכים חריגים"""
        try:
            self.add_section_header("ניתוח ערכים חריגים", 1)
            
            outlier_cols = [col for col, count in outliers.items() if count > 0]
            
            if outlier_cols:
                self.add_text("עמודות עם ערכים חריגים:", 12, bold=True)
                
                for col in outlier_cols:
                    count = outliers[col]
                    self.add_text(f"• {col}: {count} ערכים חריגים", 11, indent=5)
                
                self.add_text("\nהמלצה: בדוק את הערכים החריגים לפני המשך הניתוח", 11, bold=True)
            else:
                self.add_text("✓ לא זוהו ערכים חריגים באמצעות שיטת IQR", 12, bold=True)
        
        except Exception as e:
            logger.error(f"Error adding outliers section: {e}")
    
    def add_recommendations_section(self, analysis_results: Dict[str, Any], df: pd.DataFrame):
        """הוספת המלצות מותאמות אישית"""
        try:
            self.add_section_header("המלצות לשיפור", 1)
            
            recommendations = []
            
            # Data quality recommendations
            basic_info = analysis_results.get('basic_info', {})
            
            # Missing values recommendations
            if 'null_counts' in basic_info:
                total_nulls = sum(basic_info['null_counts'].values())
                total_cells = basic_info['shape'][0] * basic_info['shape'][1]
                null_percentage = (total_nulls / total_cells) * 100
                
                if null_percentage > 30:
                    recommendations.append("אחוז גבוה מאוד של ערכים חסרים - שקול לבדוק את איכות מקור הנתונים")
                elif null_percentage > 10:
                    recommendations.append("קיימים ערכים חסרים משמעותיים - מומלץ להחליט על אסטרטגיית טיפול (מחיקה/מילוי)")
                elif null_percentage > 0:
                    recommendations.append("ערכים חסרים מעטים - ניתן לטפל בהם באמצעות מילוי או מחיקה")
            
            # Duplicates recommendations
            if 'duplicate_rows' in basic_info and basic_info['duplicate_rows'] > 0:
                dup_pct = (basic_info['duplicate_rows'] / basic_info['shape'][0]) * 100
                if dup_pct > 5:
                    recommendations.append("אחוז גבוה של שורות כפולות - מומלץ לנקות לפני המשך הניתוח")
                else:
                    recommendations.append("נמצאו שורות כפולות מעטות - בדוק אם הן רלוונטיות לניתוח")
            
            # Correlation recommendations
            if 'strong_correlations' in analysis_results:
                strong_corrs = analysis_results['strong_correlations']
                very_high_corrs = [c for c in strong_corrs if abs(c['correlation']) > 0.9]
                
                if very_high_corrs:
                    recommendations.append("נמצאו קורלציות גבוהות מאוד - שקול להסיר עמודות מיותרות למניעת רב-קווטיות")
                elif strong_corrs:
                    recommendations.append("נמצאו קורלציות חזקות - בדוק אם יש קשרים סיבתיים או זיהוי תופעות מעניינות")
            
            # Outliers recommendations
            if 'outliers' in analysis_results:
                outlier_cols = [col for col, count in analysis_results['outliers'].items() if count > 0]
                
                if outlier_cols:
                    high_outlier_cols = [col for col in outlier_cols 
                                       if analysis_results['outliers'][col] > len(df) * 0.05]
                    
                    if high_outlier_cols:
                        recommendations.append(f"עמודות עם ערכים חריגים רבים: {', '.join(high_outlier_cols)} - בדוק אם זה שגיאות נתונים או תופעות אמיתיות")
                    else:
                        recommendations.append("ערכים חריגים מעטים - בדוק ידנית ושקול האם להשאיר או להסיר")
            
            # Data size recommendations
            rows, cols = basic_info.get('shape', (0, 0))
            
            if rows < 100:
                recommendations.append("מערך נתונים קטן - תוצאות הניתוח עלולות להיות לא יציבות")
            elif rows > 1000000:
                recommendations.append("מערך נתונים גדול מאוד - שקול לבצע דגימה לטטסטים מהירים")
            
            if cols > 50:
                recommendations.append("מספר עמודות רב - שקול לבצע בחירת תכונות (feature selection) לפני מודלים")
            
            # Memory recommendations
            if 'memory_usage' in basic_info:
                memory_mb = basic_info['memory_usage'] / (1024 * 1024)
                if memory_mb > 1000:
                    recommendations.append("שימוש גבוה בזיכרון - שקול לבצע אופטימיזציה של סוגי נתונים")
            
            # General best practices
            general_recommendations = [
                "בדוק תמיד את איכות הנתונים לפני ביצוע ניתוח מתקדם",
                "שמור גרסת גיבוי של הנתונים המקוריים לפני ביצוע שינויים",
                "תעד את כל השינויים שביצעת בנתונים לשחזור עתידי",
                "בדוק הנחות הניתוח שלך מול התוצאות שקיבלת",
                "השתמש בויזואליזציות להבנה טובה יותר של הנתונים"
            ]
            
            recommendations.extend(general_recommendations)
            
            # Add recommendations to report
            for i, rec in enumerate(recommendations, 1):
                if i <= len(recommendations) - len(general_recommendations):
                    # Specific recommendations
                    self.add_text(f"🎯 {rec}", 11, bold=True, indent=5)
                else:
                    # General recommendations
                    self.add_text(f"💡 {rec}", 11, indent=5)
            
        except Exception as e:
            logger.error(f"Error adding recommendations: {e}")
    
    def create_visualizations(self, df: pd.DataFrame, output_dir: str = "charts") -> List[str]:
        """יצירת ויזואליזציות של הנתונים"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            chart_files = []
            
            # Set Hebrew font for matplotlib
            plt.rcParams['font.family'] = ['DejaVu Sans']
            
            # 1. Correlation heatmap for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                plt.figure(figsize=(10, 8))
                correlation_matrix = df[numeric_cols].corr()
                
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                           square=True, linewidths=0.5, cbar_kws={"shrink": .8})
                plt.title(self._fix_hebrew_text('מטריצת קורלציות'), fontsize=16, pad=20)
                plt.tight_layout()
                
                chart_path = os.path.join(output_dir, 'correlation_heatmap.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files.append(chart_path)
            
            # 2. Missing values visualization
            if df.isnull().sum().sum() > 0:
                plt.figure(figsize=(12, 6))
                missing_data = df.isnull().sum()
                missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
                
                plt.bar(range(len(missing_data)), missing_data.values)
                plt.xticks(range(len(missing_data)), self._fix_list(missing_data.index), rotation=45, ha='right')
                plt.title(self._fix_hebrew_text('ערכים חסרים לפי עמודה'), fontsize=16, pad=20)
                plt.ylabel(self._fix_hebrew_text('מספר ערכים חסרים'))
                plt.tight_layout()
                
                chart_path = os.path.join(output_dir, 'missing_values.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files.append(chart_path)
            
            # 3. Distribution plots for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                n_cols = min(3, len(numeric_cols))
                n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
                
                fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
                if n_rows == 1:
                    axes = [axes] if n_cols == 1 else axes
                else:
                    axes = axes.flatten()
                
                for i, col in enumerate(numeric_cols):
                    if i < len(axes):
                        df[col].hist(bins=30, ax=axes[i], alpha=0.7)
                        axes[i].set_title(self._fix_hebrew_text(f'התפלגות: {col}'))
                        axes[i].set_ylabel(self._fix_hebrew_text('תכיפות'))
                
                # Hide empty subplots
                for i in range(len(numeric_cols), len(axes)):
                    axes[i].set_visible(False)
                
                plt.tight_layout()
                chart_path = os.path.join(output_dir, 'distributions.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files.append(chart_path)
            
            # 4. Top categories for categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
                if df[col].nunique() <= 20:  # Only for columns with reasonable number of categories
                    plt.figure(figsize=(10, 6))
                    
                    top_values = df[col].value_counts().head(10)
                    plt.bar(range(len(top_values)), top_values.values)
                    plt.xticks(range(len(top_values)), self._fix_list(top_values.index), rotation=45, ha='right')
                    plt.title(self._fix_hebrew_text(f'ערכים נפוצים: {col}'), fontsize=16, pad=20)
                    plt.ylabel(self._fix_hebrew_text('תכיפות'))
                    plt.tight_layout()
                    
                    chart_path = os.path.join(output_dir, f'top_categories_{col}.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_path)
            
            # 5. Scatter plots for top correlated pairs (with trend line)
            if len(numeric_cols) > 1:
                try:
                    corr = df[numeric_cols].corr().abs()
                    np.fill_diagonal(corr.values, 0)
                    pairs = (
                        corr.unstack()
                            .sort_values(ascending=False)
                            .drop_duplicates()
                    )
                    top_pairs = [(a, b) for (a, b) in pairs.index[:2]]
                    for x_col, y_col in top_pairs:
                        if x_col == y_col:
                            continue
                        plt.figure(figsize=(8, 6))
                        sns.regplot(x=df[x_col], y=df[y_col], scatter_kws={'alpha': 0.5})
                        plt.title(self._fix_hebrew_text(f'תרשים פיזור: {x_col} מול {y_col}'), fontsize=14)
                        plt.xlabel(x_col)
                        plt.ylabel(y_col)
                        plt.tight_layout()
                        chart_path = os.path.join(output_dir, f'scatter_{x_col}_vs_{y_col}.png')
                        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                        plt.close()
                        chart_files.append(chart_path)
                except Exception:
                    pass
            
            # 6. Box plot for numeric columns
            if len(numeric_cols) > 0:
                try:
                    plt.figure(figsize=(12, 6))
                    sns.boxplot(data=df[numeric_cols], orient='h', showfliers=False)
                    plt.title(self._fix_hebrew_text('תרשים קופסאות לעמודות מספריות'), fontsize=16, pad=20)
                    plt.tight_layout()
                    chart_path = os.path.join(output_dir, 'box_plot.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_path)
                except Exception:
                    pass
            
            # 7. Violin plot for up to 6 numeric columns
            if len(numeric_cols) > 1:
                try:
                    selected = list(numeric_cols)[:6]
                    data_to_plot = [df[c].dropna().values for c in selected]
                    plt.figure(figsize=(12, 6))
                    parts = plt.violinplot(data_to_plot, showmeans=True, showextrema=False)
                    plt.xticks(range(1, len(selected)+1), self._fix_list(selected), rotation=30, ha='right')
                    plt.title(self._fix_hebrew_text('תרשים כינור לעמודות נבחרות'), fontsize=16, pad=20)
                    plt.tight_layout()
                    chart_path = os.path.join(output_dir, 'violin_plot.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_path)
                except Exception:
                    pass
            
            # 8. Pie chart for first categorical column (top 5)
            if len(categorical_cols) > 0:
                try:
                    col = categorical_cols[0]
                    top_values = df[col].value_counts().head(5)
                    if not top_values.empty:
                        plt.figure(figsize=(8, 8))
                        plt.pie(top_values.values, labels=top_values.index, autopct='%1.1f%%', startangle=140)
                        plt.title(self._fix_hebrew_text(f'התפלגות קטגוריות (Top 5): {col}'), fontsize=16, pad=20)
                        plt.tight_layout()
                        chart_path = os.path.join(output_dir, f'pie_{col}.png')
                        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                        plt.close()
                        chart_files.append(chart_path)
                except Exception:
                    pass
            
            # 9. Area chart for time series if datetime column exists
            try:
                dt_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
                if len(dt_cols) > 0:
                    dt_col = dt_cols[0]
                    ts = df[dt_col].dropna()
                    if not ts.empty:
                        counts = ts.dt.to_period('D').value_counts().sort_index()
                        x = range(len(counts))
                        plt.figure(figsize=(12, 5))
                        plt.plot(x, counts.values, color='tab:blue')
                        plt.fill_between(x, counts.values, alpha=0.3, color='tab:blue')
                        plt.xticks(x[::max(1, len(x)//10)], [str(p) for p in counts.index[::max(1, len(x)//10)]], rotation=45, ha='right')
                        plt.title(self._fix_hebrew_text('תרשים שטח - ספירת רשומות לפי יום'), fontsize=16, pad=20)
                        plt.tight_layout()
                        chart_path = os.path.join(output_dir, 'area_timeseries.png')
                        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                        plt.close()
                        chart_files.append(chart_path)
            except Exception:
                pass
            
            return chart_files
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return []
    
    def add_charts_section(self, chart_files: List[str]):
        """הוספת תרשימים לדוח"""
        try:
            if not chart_files:
                return
            
            self.add_section_header("תרשימים וויזואליזציות", 1)
            
            chart_descriptions = {
                'correlation_heatmap.png': 'מטריצת קורלציות - מציגה את הקשרים בין העמודות המספריות',
                'missing_values.png': 'ערכים חסרים - מציג את כמות הערכים החסרים בכל עמודה',
                'distributions.png': 'התפלגויות - מציג את התפלגות הערכים בעמודות המספריות',
                'top_categories': 'קטגוריות נפוצות - מציג את הערכים השכיחים ביותר',
                'scatter_': 'תרשים פיזור עם קו מגמה',
                'box_plot.png': 'תרשים קופסאות לעמודות מספריות',
                'violin_plot.png': 'תרשים כינור לעמודות נבחרות',
                'pie_': 'תרשים עוגה (Top 5 קטגוריות)',
                'area_timeseries.png': 'תרשים שטח - סדרת זמן יומית'
            }
            
            for i, chart_file in enumerate(chart_files):
                if os.path.exists(chart_file):
                    # Add chart description
                    filename = os.path.basename(chart_file)
                    description = "תרשים נתונים"
                    
                    for key, desc in chart_descriptions.items():
                        if key in filename:
                            description = desc
                            break
                    
                    self.add_text(f"תרשים {i+1}: {description}", 12, bold=True)
                    
                    # Add the chart
                    self.add_chart(chart_file)
                    
        except Exception as e:
            logger.error(f"Error adding charts section: {e}")
    
    def add_chart(self, chart_file_path: str):
        """הוספת תרשים בודד לדוח"""
        try:
            if not os.path.exists(chart_file_path):
                logger.warning(f"Chart file not found: {chart_file_path}")
                return
            
            # Check if new page needed
            if self.current_y > self.page_height - 120:
                self.pdf.add_page()
                self.current_y = self.margin + 10
            
            # Add the chart
            chart_width = self.page_width - 2 * self.margin
            chart_height = 100
            
            self.pdf.image(chart_file_path, x=self.margin, y=self.current_y, 
                          w=chart_width, h=chart_height)
            
            self.current_y += chart_height + 10
            
        except Exception as e:
            logger.error(f"Error adding chart: {e}")
    
    def generate_comprehensive_report(self, df: pd.DataFrame, 
                                    output_path: str = "data_analysis_report.pdf") -> str:
        """יצירת דוח מקיף מנתונים אמיתיים"""
        try:
            # Analyze the data
            analysis_results = self.analyze_real_data(df)
            
            if 'error' in analysis_results:
                logger.error(f"Analysis failed: {analysis_results['error']}")
                return None
            
            # Create title page
            self.create_title_page(
                title="דוח ניתוח נתונים מקיף",
                subtitle="ניתוח אוטומטי מלא של מערך הנתונים"
            )
            
            # Add table of contents
            self.add_section_header("תוכן עניינים", 1)
            toc_items = [
                "1. סיכום נתונים",
                "2. ניתוח עמודות", 
                "3. תובנות עיקריות",
                "4. ניתוח קורלציות",
                "5. ניתוח ערכים חריגים",
                "6. המלצות לשיפור",
                "7. תרשימים וויזואליזציות"
            ]
            
            for item in toc_items:
                self.add_text(item, 12, bold=True, indent=10)
            
            # Add content sections
            if 'basic_info' in analysis_results:
                self.add_data_summary(analysis_results['basic_info'])
                
                if 'column_details' in analysis_results['basic_info']:
                    self.add_column_analysis(analysis_results['basic_info']['column_details'])
            
            if 'insights' in analysis_results:
                self.add_insights_section(analysis_results['insights'])
            
            if 'strong_correlations' in analysis_results:
                self.add_correlation_section(analysis_results['strong_correlations'])
            
            if 'outliers' in analysis_results:
                self.add_outliers_section(analysis_results['outliers'])
            
            # Add recommendations
            self.add_recommendations_section(analysis_results, df)
            
            # Create and add charts
            chart_files = self.create_visualizations(df)
            if chart_files:
                self.add_charts_section(chart_files)
            
            # Save the report
            self.pdf.output(output_path)
            logger.info(f"Comprehensive PDF report generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return None


def generate_complete_data_report(df: pd.DataFrame, 
                                output_path: str = "complete_data_report.pdf",
                                include_charts: bool = True) -> str:
    """
    פונקציה ראשית ליצירת דוח מקיף מנתונים
    Main function to generate comprehensive report from real data
    
    Args:
        df: DataFrame with your data
        output_path: Path for the output PDF file
        include_charts: Whether to include charts and visualizations
    
    Returns:
        str: Path to the generated PDF file, or None if failed
    """
    try:
        # Validate input
        if df is None or df.empty:
            logger.error("DataFrame is empty or None")
            return None
        
        # Create report generator
        report = HebrewPDFReport()
        
        # Generate comprehensive report
        result_path = report.generate_comprehensive_report(df, output_path)
        
        return result_path
        
    except Exception as e:
        logger.error(f"Error in generate_complete_data_report: {e}")
        return None


def analyze_csv_file(csv_file_path: str, output_pdf_path: str = None) -> str:
    """
    ניתוח קובץ CSV ויצירת דוח PDF
    Analyze CSV file and create PDF report
    
    Args:
        csv_file_path: Path to CSV file
        output_pdf_path: Output PDF path (optional)
    
    Returns:
        str: Path to generated PDF report
    """
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        
        # Set default output path if not provided
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
            output_pdf_path = f"דוח_ניתוח_{base_name}.pdf"
        
        # Generate report
        return generate_complete_data_report(df, output_pdf_path, include_charts=True)
        
    except Exception as e:
        logger.error(f"Error analyzing CSV file: {e}")
        return None


def analyze_excel_file(excel_file_path: str, sheet_name: Union[str, int] = 0, 
                      output_pdf_path: str = None) -> str:
    """
    ניתוח קובץ Excel ויצירת דוח PDF
    Analyze Excel file and create PDF report
    
    Args:
        excel_file_path: Path to Excel file
        sheet_name: Sheet name or index
        output_pdf_path: Output PDF path (optional)
    
    Returns:
        str: Path to generated PDF report
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        
        # Set default output path if not provided
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(excel_file_path))[0]
            output_pdf_path = f"דוח_ניתוח_{base_name}.pdf"
        
        # Generate report
        return generate_complete_data_report(df, output_pdf_path, include_charts=True)
        
    except Exception as e:
        logger.error(f"Error analyzing Excel file: {e}")
        return None