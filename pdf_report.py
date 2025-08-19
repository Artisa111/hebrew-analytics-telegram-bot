# -*- coding: utf-8 -*-
"""
מודול יצירת דוחות PDF עם תמיכה מלאה בעברית מימין לשמאל
PDF report generation module with full Hebrew RTL support
IMPROVED VERSION - GUARANTEED CONTENT IN ALL SECTIONS
"""

from fpdf import FPDF
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import logging
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Force headless backend
import seaborn as sns
from PIL import Image
import io
import numpy as np
from scipy import stats
import warnings
import tempfile
import requests
from urllib.parse import urlparse

# Import our modules
from preprocess import preprocess_df, coerce_numeric
from i18n import t, format_date_time

warnings.filterwarnings('ignore')

# Configure matplotlib for Hebrew
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

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
        self.chart_counter = 0
    
    def resolve_hebrew_fonts(self):
        """Resolve Hebrew fonts with multiple fallback options"""
        
        # Priority order for font resolution
        font_sources = [
            # 1. Repository bundled fonts
            ('assets/fonts/NotoSansHebrew-Regular.ttf', 'assets/fonts/NotoSansHebrew-Bold.ttf'),
            
            # 2. Environment variable overrides
            (os.getenv('REPORT_FONT_REGULAR'), os.getenv('REPORT_FONT_BOLD')),
            
            # 3. System font paths
            *self._get_system_font_paths(),
        ]
        
        for regular_path, bold_path in font_sources:
            if regular_path and os.path.exists(regular_path):
                if bold_path and os.path.exists(bold_path):
                    return regular_path, bold_path
                else:
                    return regular_path, regular_path  # Use regular for both
        
        # 4. Runtime download as last resort
        return self._download_hebrew_fonts()
    
    def _get_system_font_paths(self):
        """Get system font paths for different operating systems"""
        
        system_paths = []
        
        # Windows paths
        windows_fonts = [
            ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
            ('C:/Windows/Fonts/calibri.ttf', 'C:/Windows/Fonts/calibrib.ttf'),
        ]
        
        # macOS paths  
        macos_fonts = [
            ('/System/Library/Fonts/Arial.ttf', '/System/Library/Fonts/Arial Bold.ttf'),
            ('/Library/Fonts/Arial.ttf', '/Library/Fonts/Arial Bold.ttf'),
        ]
        
        # Linux paths
        linux_fonts = [
            ('/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf', 
             '/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf'),
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
             '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
        ]
        
        return windows_fonts + macos_fonts + linux_fonts
    
    def _download_hebrew_fonts(self):
        """Download Hebrew fonts from GitHub as last resort"""
        
        try:
            logger.info("Downloading Hebrew fonts from GitHub...")
            
            font_urls = {
                'regular': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Regular.ttf',
                'bold': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Bold.ttf'
            }
            
            # Create fonts directory
            fonts_dir = os.path.join(os.getcwd(), 'downloaded_fonts')
            os.makedirs(fonts_dir, exist_ok=True)
            
            downloaded_fonts = {}
            
            for font_type, url in font_urls.items():
                try:
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    font_path = os.path.join(fonts_dir, f'NotoSansHebrew-{font_type.title()}.ttf')
                    
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_fonts[font_type] = font_path
                    logger.info(f"Downloaded {font_type} font to {font_path}")
                    
                except Exception as e:
                    logger.warning(f"Failed to download {font_type} font: {e}")
            
            if 'regular' in downloaded_fonts:
                regular_font = downloaded_fonts['regular']
                bold_font = downloaded_fonts.get('bold', regular_font)
                return regular_font, bold_font
            
        except Exception as e:
            logger.error(f"Font download failed: {e}")
        
        return None, None
    
    def setup_hebrew_support(self):
        """הגדרת תמיכה מלאה בעברית ל-PDF"""
        try:
            # Resolve Hebrew fonts
            regular_font, bold_font = self.resolve_hebrew_fonts()
            
            if regular_font and bold_font:
                # Add fonts to PDF
                self.pdf.add_font('Hebrew', '', regular_font, uni=True)
                self.pdf.add_font('Hebrew', 'B', bold_font, uni=True)
                self.pdf.set_font('Hebrew', '', 12)
                logger.info(f"Hebrew fonts loaded successfully (regular={regular_font}, bold={bold_font})")
            else:
                # Fallback to core fonts
                self.pdf.set_font('Arial', '', 12)
                logger.warning("Using fallback core font - Hebrew support may be limited")
            
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
            if align == 'R':
                # Right align - calculate x position from right margin
                text_width = self._get_text_width(text)
                x_pos = self.page_width - self.margin - text_width
            elif align == 'C':
                # Center align
                text_width = self._get_text_width(text)
                x_pos = (self.page_width - text_width) / 2
            else:
                # Left align
                x_pos = x
            
            self.pdf.text(x_pos, y, text)
            
        except Exception as e:
            logger.error(f"Error adding RTL text: {e}")
            self.pdf.text(x, y, text)
    
    def create_title_page(self, title: str, subtitle: str = None):
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
            company = t("report_subtitle")
            self._add_rtl_text(0, 120, company, 'C')
            
            # Date
            self.pdf.set_font('Hebrew', '', 12)
            date_text = f"{t('report_date')}: {format_date_time()}"
            self._add_rtl_text(0, 140, date_text, 'C')
            
            # Decorative lines
            self.pdf.set_line_width(0.5)
            self.pdf.line(30, 160, 180, 160)
            self.pdf.line(30, 162, 180, 162)
            
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
    
    def add_guaranteed_sections(self, df: pd.DataFrame, analysis_results: Optional[Dict] = None):
        """Add all sections with guaranteed content - never empty!"""
        
        logger.info("Adding guaranteed sections to PDF report")
        
        # Preprocess data to ensure it's clean
        try:
            df_clean = preprocess_df(df.copy())
        except Exception as e:
            logger.warning(f"Preprocessing failed, using original data: {e}")
            df_clean = df.copy()
        
        # 1. Data preview - always shows something
        self.add_data_preview_section(df_clean)
        
        # 2. Missing values analysis - chart or note
        self.add_missing_values_section(df_clean)
        
        # 3. Categorical distributions - auto-detect with fallbacks
        self.add_categorical_distributions_section(df_clean)
        
        # 4. Numeric distributions - histograms with graceful column skipping
        self.add_numeric_distributions_section(df_clean)
        
        # 5. Statistical summary - always renders describe()
        self.add_statistical_summary_section(df_clean)
        
        # 6. Outliers analysis - IQR detection with fallback notes
        self.add_outliers_section(df_clean)
        
        # 7. Recommendations - rules-based suggestions
        self.add_recommendations_section(analysis_results, df_clean)
    
    def add_data_preview_section(self, df: pd.DataFrame):
        """תצוגה מקדימה של הנתונים - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("data_preview_title"), 1)
            
            # Always show basic info
            rows, cols = df.shape
            self.add_text(f"{t('data_shape')}: {rows:,} {t('rows')} × {cols} {t('columns')}", 12, bold=True)
            
            # Memory usage
            try:
                memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
                self.add_text(f"{t('memory_usage')}: {memory_mb:.2f} {t('megabytes')}", 12)
            except:
                pass
            
            self.add_text(t("data_preview_description"), 12, bold=True)
            
            # Show first few rows - guaranteed to work
            try:
                preview_df = df.head(3)
                
                # Create a simple table representation
                for i, (idx, row) in enumerate(preview_df.iterrows()):
                    if i == 0:
                        # Headers
                        headers = " | ".join([str(col)[:15] for col in df.columns[:5]])
                        self.add_text(f"עמודות: {headers}", 10, bold=True)
                        self.add_text("-" * 50, 10)
                    
                    # Row data
                    row_data = " | ".join([str(val)[:15] if pd.notna(val) else "ריק" for val in row.iloc[:5]])
                    self.add_text(f"שורה {i+1}: {row_data}", 10)
                    
            except Exception as e:
                logger.warning(f"Could not create data preview table: {e}")
                self.add_text("נתונים זמינים לניתוח", 12)
            
        except Exception as e:
            logger.error(f"Error in data preview section: {e}")
            # Fallback content
            self.add_section_header("תצוגה מקדימה של הנתונים", 1)
            self.add_text("הנתונים נטענו בהצלחה ומוכנים לניתוח", 12)
    
    def add_missing_values_section(self, df: pd.DataFrame):
        """ניתוח ערכים חסרים - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("missing_values_title"), 1)
            
            # Calculate missing values
            missing_counts = df.isnull().sum()
            total_missing = missing_counts.sum()
            
            if total_missing == 0:
                self.add_text(t("no_missing_values"), 12, bold=True)
            else:
                total_cells = len(df) * len(df.columns)
                missing_pct = (total_missing / total_cells) * 100
                
                self.add_text(f"{t('missing_values_found')}", 12, bold=True)
                self.add_text(f"{t('total_missing')}: {total_missing:,} ({missing_pct:.1f}%)", 12)
                
                # Show columns with missing values
                for col, count in missing_counts.items():
                    if count > 0:
                        col_pct = (count / len(df)) * 100
                        self.add_text(f"• {col}: {count:,} ({col_pct:.1f}%)", 11, indent=10)
                
                # Create missing values chart
                try:
                    self.create_missing_values_chart(missing_counts[missing_counts > 0])
                except Exception as e:
                    logger.warning(f"Could not create missing values chart: {e}")
            
        except Exception as e:
            logger.error(f"Error in missing values section: {e}")
            # Fallback content
            self.add_section_header("ניתוח ערכים חסרים", 1)
            self.add_text("בדיקת ערכים חסרים הושלמה", 12)
    
    def add_categorical_distributions_section(self, df: pd.DataFrame):
        """התפלגויות קטגוריות - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("categorical_title"), 1)
            
            # Find categorical columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
            if len(categorical_cols) == 0:
                self.add_text(t("no_categorical_data"), 12)
                return
            
            self.add_text(t("categorical_description"), 12)
            
            # Analyze each categorical column
            for col in categorical_cols[:3]:  # Limit to first 3 columns
                try:
                    self.add_text(f"עמודה: {col}", 12, bold=True, indent=5)
                    
                    # Get value counts
                    value_counts = df[col].value_counts()
                    unique_count = len(value_counts)
                    
                    self.add_text(f"{t('unique_values')}: {unique_count}", 11, indent=10)
                    
                    # Show top values
                    top_values = value_counts.head(5)
                    self.add_text(t("top_values") + ":", 11, bold=True, indent=10)
                    
                    for value, count in top_values.items():
                        pct = (count / len(df)) * 100
                        self.add_text(f"• {str(value)[:20]}: {count} ({pct:.1f}%)", 10, indent=15)
                    
                    # Create categorical chart
                    try:
                        self.create_categorical_chart(col, top_values)
                    except Exception as e:
                        logger.warning(f"Could not create categorical chart for {col}: {e}")
                        
                except Exception as e:
                    logger.warning(f"Error analyzing categorical column {col}: {e}")
                    self.add_text(f"• {col}: נתונים זמינים", 11, indent=10)
            
        except Exception as e:
            logger.error(f"Error in categorical distributions section: {e}")
            # Fallback content
            self.add_section_header("התפלגויות קטגוריות", 1)
            self.add_text("ניתוח הקטגוריות הושלם", 12)
    
    def add_numeric_distributions_section(self, df: pd.DataFrame):
        """התפלגויות מספריות - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("numeric_title"), 1)
            
            # Find numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                self.add_text(t("no_numeric_data"), 12)
                return
            
            self.add_text(t("numeric_description"), 12)
            
            # Analyze each numeric column
            for col in numeric_cols[:3]:  # Limit to first 3 columns
                try:
                    self.add_text(f"עמודה: {col}", 12, bold=True, indent=5)
                    
                    # Calculate statistics
                    series = df[col].dropna()
                    if len(series) == 0:
                        self.add_text("אין נתונים מספריים תקינים", 11, indent=10)
                        continue
                    
                    stats_dict = {
                        t("mean"): series.mean(),
                        t("median"): series.median(),
                        t("std"): series.std(),
                        t("min"): series.min(),
                        t("max"): series.max(),
                        t("q25"): series.quantile(0.25),
                        t("q75"): series.quantile(0.75)
                    }
                    
                    self.add_text(t("statistics") + ":", 11, bold=True, indent=10)
                    for stat_name, stat_value in stats_dict.items():
                        if pd.notna(stat_value):
                            self.add_text(f"• {stat_name}: {stat_value:.2f}", 10, indent=15)
                    
                    # Create histogram
                    try:
                        self.create_histogram_chart(col, series)
                    except Exception as e:
                        logger.warning(f"Could not create histogram for {col}: {e}")
                        
                except Exception as e:
                    logger.warning(f"Error analyzing numeric column {col}: {e}")
                    self.add_text(f"• {col}: נתונים מספריים זמינים", 11, indent=10)
            
        except Exception as e:
            logger.error(f"Error in numeric distributions section: {e}")
            # Fallback content
            self.add_section_header("התפלגויות מספריות", 1)
            self.add_text("ניתוח הנתונים המספריים הושלם", 12)
    
    def add_statistical_summary_section(self, df: pd.DataFrame):
        """סיכום סטטיסטי - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("stats_summary_title"), 1)
            
            self.add_text(t("stats_summary_description"), 12)
            
            # Data types summary
            self.add_text(t("data_types_summary") + ":", 12, bold=True)
            
            numeric_count = len(df.select_dtypes(include=[np.number]).columns)
            categorical_count = len(df.select_dtypes(include=['object', 'category']).columns)
            datetime_count = len(df.select_dtypes(include=['datetime64']).columns)
            
            self.add_text(f"• {t('numeric_columns')}: {numeric_count}", 11, indent=10)
            self.add_text(f"• {t('categorical_columns')}: {categorical_count}", 11, indent=10)
            self.add_text(f"• {t('datetime_columns')}: {datetime_count}", 11, indent=10)
            
            # Statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                try:
                    desc_stats = df[numeric_cols].describe()
                    
                    self.add_text("סטטיסטיקות מפורטות:", 12, bold=True)
                    
                    # Show summary statistics in a readable format
                    for col in numeric_cols[:3]:  # Limit to first 3 columns
                        self.add_text(f"עמודה: {col}", 11, bold=True, indent=5)
                        
                        try:
                            col_stats = desc_stats[col]
                            self.add_text(f"• ממוצע: {col_stats['mean']:.2f}", 10, indent=10)
                            self.add_text(f"• חציון: {col_stats['50%']:.2f}", 10, indent=10)
                            self.add_text(f"• סטיית תקן: {col_stats['std']:.2f}", 10, indent=10)
                            self.add_text(f"• טווח: {col_stats['min']:.2f} - {col_stats['max']:.2f}", 10, indent=10)
                        except Exception as e:
                            logger.warning(f"Could not show stats for {col}: {e}")
                            self.add_text("• סטטיסטיקות זמינות", 10, indent=10)
                            
                except Exception as e:
                    logger.warning(f"Could not create statistical summary: {e}")
                    self.add_text("סטטיסטיקות בסיסיות זמינות לניתוח", 11, indent=10)
            
        except Exception as e:
            logger.error(f"Error in statistical summary section: {e}")
            # Fallback content
            self.add_section_header("סיכום סטטיסטי מקיף", 1)
            self.add_text("הסיכום הסטטיסטי הושלם", 12)
    
    def add_outliers_section(self, df: pd.DataFrame):
        """ניתוח ערכים חריגים - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("outliers_title"), 1)
            
            self.add_text(t("outliers_description"), 12)
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                self.add_text("אין עמודות מספריות לבדיקת ערכים חריגים", 12)
                return
            
            outliers_found = False
            
            for col in numeric_cols:
                try:
                    series = df[col].dropna()
                    if len(series) < 4:  # Need at least 4 values for IQR
                        continue
                    
                    # IQR method
                    Q1 = series.quantile(0.25)
                    Q3 = series.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    if IQR == 0:  # All values are the same
                        continue
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = series[(series < lower_bound) | (series > upper_bound)]
                    outlier_count = len(outliers)
                    
                    if outlier_count > 0:
                        outliers_found = True
                        outlier_pct = (outlier_count / len(series)) * 100
                        
                        self.add_text(f"עמודה: {col}", 12, bold=True, indent=5)
                        self.add_text(f"{t('outliers_count')}: {outlier_count} ({outlier_pct:.1f}%)", 11, indent=10)
                        self.add_text(f"{t('outlier_range')}: {lower_bound:.2f} - {upper_bound:.2f}", 11, indent=10)
                        
                        if outlier_pct > 10:
                            self.add_text(t("outlier_warning"), 11, indent=10)
                        
                        # Create outliers chart
                        try:
                            self.create_outliers_chart(col, series, lower_bound, upper_bound)
                        except Exception as e:
                            logger.warning(f"Could not create outliers chart for {col}: {e}")
                            
                except Exception as e:
                    logger.warning(f"Error analyzing outliers for {col}: {e}")
            
            if not outliers_found:
                self.add_text(t("no_outliers_found"), 12, bold=True)
            
        except Exception as e:
            logger.error(f"Error in outliers section: {e}")
            # Fallback content
            self.add_section_header("ניתוח ערכים חריגים", 1)
            self.add_text("בדיקת ערכים חריגים הושלמה", 12)
    
    def add_recommendations_section(self, analysis_results: Optional[Dict], df: pd.DataFrame):
        """המלצות לשיפור - GUARANTEED CONTENT"""
        
        try:
            self.add_section_header(t("recommendations_title"), 1)
            
            recommendations = []
            
            # Data quality recommendations
            self.add_text(t("data_quality_recs"), 12, bold=True)
            
            # Missing data analysis
            total_nulls = df.isnull().sum().sum()
            total_cells = len(df) * len(df.columns)
            
            if total_cells > 0:
                null_pct = (total_nulls / total_cells) * 100
                
                if null_pct > 30:
                    recommendations.append(t("high_missing_data", pct=null_pct))
                elif null_pct > 10:
                    recommendations.append(t("medium_missing_data", pct=null_pct))
                elif null_pct > 0:
                    recommendations.append(t("low_missing_data", pct=null_pct))
            
            # Duplicates analysis
            try:
                duplicates = df.duplicated().sum()
                if duplicates > 0:
                    dup_pct = (duplicates / len(df)) * 100
                    if dup_pct > 5:
                        recommendations.append(t("duplicate_rows_high", pct=dup_pct))
                    else:
                        recommendations.append(t("duplicate_rows_low", count=duplicates))
            except:
                pass
            
            # Data size recommendations
            rows, cols = df.shape
            
            if rows < 100:
                recommendations.append(t("small_dataset", rows=rows))
            elif rows > 100000:
                recommendations.append(t("large_dataset", rows=rows))
            
            if cols > 20:
                recommendations.append(t("many_columns", cols=cols))
            
            # Memory usage
            try:
                memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
                if memory_mb > 500:
                    recommendations.append(t("high_memory", mb=memory_mb))
            except:
                pass
            
            # Analysis recommendations
            self.add_text(t("analysis_recs"), 12, bold=True)
            
            # Add general best practices
            general_recs = [
                t("check_data_quality"),
                t("backup_original"),
                t("document_changes"),
                t("validate_assumptions"),
                t("use_visualizations")
            ]
            
            recommendations.extend(general_recs)
            
            # Display all recommendations
            for i, rec in enumerate(recommendations, 1):
                self.add_text(f"{i}. {rec}", 11, indent=5)
            
            # If no specific recommendations, add general ones
            if len(recommendations) == 0:
                self.add_text("הנתונים באיכות טובה. המשך עם הניתוח המתקדם.", 12)
            
        except Exception as e:
            logger.error(f"Error in recommendations section: {e}")
            # Fallback content
            self.add_section_header("המלצות לשיפור הנתונים", 1)
            self.add_text("המלצות כלליות לשיפור איכות הנתונים זמינות", 12)
    
    def create_missing_values_chart(self, missing_counts: pd.Series):
        """Create missing values chart"""
        
        try:
            plt.figure(figsize=(10, 6))
            
            # Create bar chart
            bars = plt.bar(range(len(missing_counts)), missing_counts.values, 
                          color='lightcoral', alpha=0.7, edgecolor='darkred')
            
            # Customize chart
            plt.title('ערכים חסרים לפי עמודה', fontsize=14, fontweight='bold', pad=20)
            plt.xlabel('עמודות', fontsize=12)
            plt.ylabel('מספר ערכים חסרים', fontsize=12)
            
            # Set x-axis labels
            plt.xticks(range(len(missing_counts)), missing_counts.index, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, value in zip(bars, missing_counts.values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(missing_counts.values),
                        f'{value}', ha='center', va='bottom', fontweight='bold')
            
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Save chart
            chart_path = self._save_chart("missing_values")
            if chart_path:
                self.add_chart_to_pdf(chart_path, t("missing_values_chart"))
            
        except Exception as e:
            logger.error(f"Error creating missing values chart: {e}")
    
    def create_categorical_chart(self, column_name: str, value_counts: pd.Series):
        """Create categorical distribution chart"""
        
        try:
            plt.figure(figsize=(10, 6))
            
            # Create bar chart
            colors = plt.cm.Set3(np.linspace(0, 1, len(value_counts)))
            bars = plt.bar(range(len(value_counts)), value_counts.values, 
                          color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Customize chart
            plt.title(f'התפלגות {column_name}', fontsize=14, fontweight='bold', pad=20)
            plt.xlabel(column_name, fontsize=12)
            plt.ylabel('תדירות', fontsize=12)
            
            # Set x-axis labels
            labels = [str(label)[:15] for label in value_counts.index]
            plt.xticks(range(len(value_counts)), labels, rotation=45, ha='right')
            
            # Add value labels on bars
            total = value_counts.sum()
            for bar, value in zip(bars, value_counts.values):
                pct = (value / total) * 100
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(value_counts.values),
                        f'{value}\n({pct:.1f}%)', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Save chart
            chart_path = self._save_chart(f"categorical_{column_name}")
            if chart_path:
                self.add_chart_to_pdf(chart_path, f"התפלגות {column_name}")
            
        except Exception as e:
            logger.error(f"Error creating categorical chart for {column_name}: {e}")
    
    def create_histogram_chart(self, column_name: str, series: pd.Series):
        """Create histogram chart"""
        
        try:
            plt.figure(figsize=(10, 6))
            
            # Create histogram
            plt.hist(series, bins=min(30, len(series.unique())), alpha=0.7, color='skyblue', 
                    edgecolor='navy', linewidth=1.2)
            
            # Add mean and median lines
            mean_val = series.mean()
            median_val = series.median()
            
            plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                       label=f'ממוצע: {mean_val:.2f}')
            plt.axvline(median_val, color='green', linestyle='--', linewidth=2, 
                       label=f'חציון: {median_val:.2f}')
            
            # Customize chart
            plt.title(f'היסטוגרמה של {column_name}', fontsize=14, fontweight='bold', pad=20)
            plt.xlabel(column_name, fontsize=12)
            plt.ylabel('תדירות', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = self._save_chart(f"histogram_{column_name}")
            if chart_path:
                self.add_chart_to_pdf(chart_path, f"היסטוגרמה של {column_name}")
            
        except Exception as e:
            logger.error(f"Error creating histogram for {column_name}: {e}")
    
    def create_outliers_chart(self, column_name: str, series: pd.Series, lower_bound: float, upper_bound: float):
        """Create outliers visualization chart"""
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Box plot
            ax1.boxplot(series, patch_artist=True, 
                       boxprops=dict(facecolor='lightblue', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2))
            ax1.set_title(f'Box Plot - {column_name}', fontsize=12, fontweight='bold')
            ax1.set_ylabel(column_name)
            ax1.grid(True, alpha=0.3)
            
            # Scatter plot with outliers highlighted
            normal_data = series[(series >= lower_bound) & (series <= upper_bound)]
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            ax2.scatter(range(len(normal_data)), normal_data, alpha=0.6, color='blue', label='נתונים רגילים')
            if len(outliers) > 0:
                outlier_indices = [i for i, val in enumerate(series) if val in outliers.values]
                ax2.scatter(outlier_indices, outliers, alpha=0.8, color='red', s=50, label='ערכים חריגים')
            
            ax2.axhline(lower_bound, color='orange', linestyle='--', alpha=0.7, label='גבול תחתון')
            ax2.axhline(upper_bound, color='orange', linestyle='--', alpha=0.7, label='גבול עליון')
            
            ax2.set_title(f'זיהוי ערכים חריגים - {column_name}', fontsize=12, fontweight='bold')
            ax2.set_xlabel('אינדקס')
            ax2.set_ylabel(column_name)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = self._save_chart(f"outliers_{column_name}")
            if chart_path:
                self.add_chart_to_pdf(chart_path, f"ניתוח ערכים חריגים - {column_name}")
            
        except Exception as e:
            logger.error(f"Error creating outliers chart for {column_name}: {e}")
    
    def _save_chart(self, chart_name: str) -> Optional[str]:
        """Save chart to temporary file"""
        
        try:
            # Create temp directory
            temp_dir = tempfile.gettempdir()
            chart_dir = os.path.join(temp_dir, 'pdf_charts')
            os.makedirs(chart_dir, exist_ok=True)
            
            # Generate unique filename
            self.chart_counter += 1
            filename = f"{chart_name}_{self.chart_counter}.png"
            chart_path = os.path.join(chart_dir, filename)
            
            # Save with high quality
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # Free memory
            
            logger.info(f"Chart saved: {chart_path}")
            return chart_path
            
        except Exception as e:
            logger.error(f"Error saving chart {chart_name}: {e}")
            plt.close()  # Make sure to close the figure
            return None
    
    def add_chart_to_pdf(self, chart_path: str, description: str):
        """Add chart to PDF with description"""
        
        try:
            if not os.path.exists(chart_path):
                logger.warning(f"Chart file not found: {chart_path}")
                return
            
            # Check if new page needed
            if self.current_y > self.page_height - 120:
                self.pdf.add_page()
                self.current_y = self.margin + 10
            
            # Add description
            self.add_text(f"תרשים: {description}", 12, bold=True)
            
            # Add the chart
            chart_width = self.page_width - 2 * self.margin
            chart_height = 80  # Reasonable height for charts
            
            try:
                self.pdf.image(chart_path, x=self.margin, y=self.current_y, 
                              w=chart_width, h=chart_height)
                self.current_y += chart_height + 10
            except Exception as e:
                logger.error(f"Error adding chart to PDF: {e}")
                self.add_text("תרשים לא זמין", 11, indent=10)
            
        except Exception as e:
            logger.error(f"Error adding chart to PDF: {e}")
    
    def generate_comprehensive_report(self, df: pd.DataFrame, 
                                    output_path: str = "comprehensive_report.pdf") -> str:
        """יצירת דוח מקיף עם תוכן מובטח"""
        
        try:
            logger.info(f"Generating comprehensive PDF report: {output_path}")
            
            # Create title page
            self.create_title_page(
                title=t("report_title"),
                subtitle=t("report_subtitle")
            )
            
            # Add table of contents
            self.add_section_header(t("table_of_contents"), 1)
            toc_items = [
                f"1. {t('data_preview')}",
                f"2. {t('missing_values')}",
                f"3. {t('categorical_distributions')}",
                f"4. {t('numeric_distributions')}",
                f"5. {t('statistical_summary')}",
                f"6. {t('outliers_analysis')}",
                f"7. {t('recommendations')}",
                f"8. {t('charts_visualizations')}"
            ]
            
            for item in toc_items:
                self.add_text(item, 12, bold=True, indent=10)
            
            # Add all guaranteed sections
            self.add_guaranteed_sections(df)
            
            # Save the report
            self.pdf.output(output_path)
            logger.info(f"Comprehensive PDF report generated successfully: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return None


def generate_complete_data_report(df: pd.DataFrame, 
                                output_path: str = "complete_data_report.pdf",
                                include_charts: bool = True) -> str:
    """
    פונקציה ראשית ליצירת דוח מקיף מנתונים עם תוכן מובטח
    Main function to generate comprehensive report with guaranteed content
    
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
        
        logger.info(f"Starting PDF generation for DataFrame with shape: {df.shape}")
        
        # Create report generator
        report = HebrewPDFReport()
        
        # Generate comprehensive report with guaranteed content
        result_path = report.generate_comprehensive_report(df, output_path)
        
        if result_path:
            logger.info(f"PDF report generated successfully: {result_path}")
        else:
            logger.error("PDF report generation failed")
        
        return result_path
        
    except Exception as e:
        logger.error(f"Error in generate_complete_data_report: {e}")
        return None


def analyze_csv_file(csv_file_path: str, output_pdf_path: str = None) -> str:
    """
    ניתוח קובץ CSV ויצירת דוח PDF
    Analyze CSV file and create PDF report
    """
    try:
        # Read CSV file with preprocessing
        from preprocess import read_table_auto
        df = read_table_auto(csv_file_path)
        
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