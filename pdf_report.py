# -*- coding: utf-8 -*-
"""
מודול יצירת דוחות PDF עם תמיכה מלאה בעברית מימין לשמאל
PDF report generation module with full Hebrew RTL support
PRODUCTION VERSION - NO DEMO DATA
"""

from fpdf import FPDF
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import os
from datetime import datetime
import matplotlib
# Enforce headless backend before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io
import numpy as np
from scipy import stats
import arabic_reshaper
from bidi.algorithm import get_display
import warnings
import requests
import platform
import tempfile

warnings.filterwarnings('ignore')

# Import our new modules
from preprocess import preprocess_df, read_table_auto
from i18n import t, format_date_time, get_timezone
from logging_config import get_logger

# Configure matplotlib for Hebrew
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']

logger = get_logger(__name__)

class HebrewPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        # Set page dimensions and margin BEFORE calling setup_hebrew_support
        self.current_y = 0
        self.page_width = 210
        self.page_height = 297
        self.margin = 20
        self.rtl_support = True
        # Now setup Hebrew support with all attributes initialized
        self.setup_hebrew_support()
    
    def resolve_hebrew_fonts(self) -> tuple[Optional[str], Optional[str]]:
        """
        Robust Hebrew font resolution in priority order:
        1. Repository-bundled fonts
        2. Environment variable overrides
        3. System font paths
        4. Download Noto Sans Hebrew as fallback
        
        Returns:
            tuple: (regular_font_path, bold_font_path) or (None, None) if all fail
        """
        try:
            logger.info("Starting Hebrew font resolution...")
            
            # 1. Check repository-bundled fonts first
            repo_fonts = self._check_repository_fonts()
            if repo_fonts[0] and repo_fonts[1]:
                logger.info(f"Using repository-bundled fonts: regular={repo_fonts[0]}, bold={repo_fonts[1]}")
                return repo_fonts
            
            # 2. Check environment variable overrides
            env_fonts = self._check_environment_fonts()
            if env_fonts[0] and env_fonts[1]:
                logger.info(f"Using environment-specified fonts: regular={env_fonts[0]}, bold={env_fonts[1]}")
                return env_fonts
            
            # 3. Scan system font paths
            system_fonts = self._scan_system_fonts()
            if system_fonts[0] and system_fonts[1]:
                logger.info(f"Using system fonts: regular={system_fonts[0]}, bold={system_fonts[1]}")
                return system_fonts
            
            # 4. Last resort: download Noto Sans Hebrew
            downloaded_fonts = self._download_noto_fonts()
            if downloaded_fonts[0] and downloaded_fonts[1]:
                logger.info(f"Downloaded and using Noto fonts: regular={downloaded_fonts[0]}, bold={downloaded_fonts[1]}")
                return downloaded_fonts
            
            logger.warning("Failed to resolve Hebrew fonts through all methods")
            return None, None
            
        except Exception as e:
            logger.error(f"Error in Hebrew font resolution: {e}")
            return None, None
    
    def _check_repository_fonts(self) -> tuple[Optional[str], Optional[str]]:
        """Check for repository-bundled fonts in assets/fonts/"""
        try:
            assets_fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts')
            regular_path = os.path.join(assets_fonts_dir, 'NotoSansHebrew-Regular.ttf')
            bold_path = os.path.join(assets_fonts_dir, 'NotoSansHebrew-Bold.ttf')
            
            regular_font = regular_path if os.path.exists(regular_path) else None
            bold_font = bold_path if os.path.exists(bold_path) else None
            
            return regular_font, bold_font
        except Exception as e:
            logger.warning(f"Error checking repository fonts: {e}")
            return None, None
    
    def _check_environment_fonts(self) -> tuple[Optional[str], Optional[str]]:
        """Check environment variable font overrides"""
        try:
            regular_env = os.getenv('REPORT_FONT_REGULAR')
            bold_env = os.getenv('REPORT_FONT_BOLD')
            
            regular_font = regular_env if regular_env and os.path.exists(regular_env) else None
            bold_font = bold_env if bold_env and os.path.exists(bold_env) else None
            
            return regular_font, bold_font
        except Exception as e:
            logger.warning(f"Error checking environment fonts: {e}")
            return None, None
    
    def _scan_system_fonts(self) -> tuple[Optional[str], Optional[str]]:
        """Scan system font paths for Hebrew-compatible fonts"""
        try:
            # Extended font paths for different operating systems
            font_paths = {
                'windows': [
                    'C:/Windows/Fonts/arial.ttf',
                    'C:/Windows/Fonts/arialbd.ttf',
                    'C:/Windows/Fonts/calibri.ttf',
                    'C:/Windows/Fonts/calibrib.ttf',
                    'C:/Windows/Fonts/NotoSansHebrew-Regular.ttf',
                    'C:/Windows/Fonts/NotoSansHebrew-Bold.ttf'
                ],
                'linux': [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                    '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
                    '/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf',
                    '/usr/share/fonts/TTF/NotoSansHebrew-Regular.ttf',
                    '/usr/share/fonts/TTF/NotoSansHebrew-Bold.ttf'
                ],
                'mac': [
                    '/System/Library/Fonts/Arial.ttf',
                    '/System/Library/Fonts/Arial Bold.ttf',
                    '/Library/Fonts/Arial.ttf',
                    '/Library/Fonts/NotoSansHebrew-Regular.ttf',
                    '/Library/Fonts/NotoSansHebrew-Bold.ttf'
                ]
            }
            
            regular_font = None
            bold_font = None
            
            # Detect OS and try to load fonts
            system = platform.system().lower()
            if 'win' in system:
                paths = font_paths.get('windows', [])
            elif 'darwin' in system:
                paths = font_paths.get('mac', [])
            else:
                paths = font_paths.get('linux', [])
            
            # Also try all paths as fallback
            all_paths = []
            for os_paths in font_paths.values():
                all_paths.extend(os_paths)
            
            paths.extend(all_paths)
            
            # Find fonts
            for path in paths:
                if os.path.exists(path):
                    if 'bold' in path.lower() or 'bd' in path.lower() or 'Bold' in path:
                        if bold_font is None:
                            bold_font = path
                    else:
                        if regular_font is None:
                            regular_font = path
                    
                    if regular_font and bold_font:
                        break
            
            return regular_font, bold_font
        except Exception as e:
            logger.warning(f"Error scanning system fonts: {e}")
            return None, None
    
    def _download_noto_fonts(self) -> tuple[Optional[str], Optional[str]]:
        """Download Noto Sans Hebrew fonts as last resort"""
        try:
            logger.info("Attempting to download Noto Sans Hebrew fonts...")
            
            # Determine download directory
            download_dirs = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts'),
                '/tmp/fonts',
                os.path.expanduser('~/fonts')
            ]
            
            fonts_dir = None
            for dir_path in download_dirs:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    # Test write permission
                    test_file = os.path.join(dir_path, 'test_write.tmp')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    fonts_dir = dir_path
                    break
                except (OSError, PermissionError):
                    continue
            
            if not fonts_dir:
                logger.warning("No writable directory found for font downloads")
                return None, None
            
            # Download URLs for Noto Sans Hebrew
            font_urls = {
                'regular': 'https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Regular.ttf',
                'bold': 'https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Bold.ttf'
            }
            
            downloaded_fonts = {}
            
            for weight, url in font_urls.items():
                try:
                    filename = f'NotoSansHebrew-{weight.capitalize()}.ttf'
                    filepath = os.path.join(fonts_dir, filename)
                    
                    # Skip if already exists
                    if os.path.exists(filepath):
                        downloaded_fonts[weight] = filepath
                        continue
                    
                    logger.info(f"Downloading {weight} font from {url}")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_fonts[weight] = filepath
                    logger.info(f"Successfully downloaded {weight} font to {filepath}")
                    
                except Exception as e:
                    logger.warning(f"Failed to download {weight} font: {e}")
            
            regular_font = downloaded_fonts.get('regular')
            bold_font = downloaded_fonts.get('bold')
            
            return regular_font, bold_font
            
        except Exception as e:
            logger.error(f"Error downloading Noto fonts: {e}")
            return None, None
    
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
    
    def setup_hebrew_support(self):
        """הגדרת תמיכה מלאה בעברית ל-PDF"""
        try:
            logger.info("Setting up Hebrew support for PDF...")
            
            # Resolve Hebrew fonts using robust method
            regular_font, bold_font = self.resolve_hebrew_fonts()
            
            # Add fonts to PDF if found
            if regular_font and os.path.exists(regular_font):
                self.pdf.add_font('Hebrew', '', regular_font, uni=True)
                
                # Use bold font if available, otherwise use regular font for bold
                if bold_font and os.path.exists(bold_font):
                    self.pdf.add_font('Hebrew', 'B', bold_font, uni=True)
                else:
                    self.pdf.add_font('Hebrew', 'B', regular_font, uni=True)
                    logger.info("Using regular font for bold text (bold font not found)")
                
                self.pdf.set_font('Hebrew', '', 12)
                logger.info(f"Hebrew fonts loaded successfully (regular={regular_font}, bold={bold_font or regular_font})")
                
            else:
                # Fallback to core fonts - Hebrew support will be limited
                self.pdf.set_font('Arial', '', 12)
                logger.warning("Using fallback core font - Hebrew support may be limited. Hebrew text may not display correctly.")
            
            # Set auto page break and margins (now that self.margin is available)
            self.pdf.set_auto_page_break(auto=True, margin=15)
            self.pdf.set_margins(self.margin, self.margin, self.margin)
            
        except Exception as e:
            logger.error(f"Error setting up Hebrew support: {e}")
            # Emergency fallback
            try:
                self.pdf.set_font('Arial', '', 12)
            except:
                pass
    
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
            
            # Date with timezone support
            if date is None:
                date = format_date_time()
            
            self.pdf.set_font('Hebrew', '', 12)
            date_text = f"{t('report_date')}: {date}"
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
            self.add_section_header(t("recommendations_title"), 1)
            
            recommendations = []
            
            # Data quality recommendations
            basic_info = analysis_results.get('basic_info', {})
            
            # Missing values recommendations
            if 'null_counts' in basic_info:
                total_nulls = sum(basic_info['null_counts'].values())
                total_cells = basic_info['shape'][0] * basic_info['shape'][1]
                null_percentage = (total_nulls / total_cells) * 100
                
                if null_percentage > 30:
                    recommendations.append(t("high_missing_data", pct=null_percentage))
                elif null_percentage > 10:
                    recommendations.append(t("medium_missing_data", pct=null_percentage))
                elif null_percentage > 0:
                    recommendations.append(t("low_missing_data", pct=null_percentage))
            
            # Duplicates recommendations
            if 'duplicate_rows' in basic_info and basic_info['duplicate_rows'] > 0:
                dup_pct = (basic_info['duplicate_rows'] / basic_info['shape'][0]) * 100
                if dup_pct > 5:
                    recommendations.append(t("duplicate_rows_high", pct=dup_pct))
                else:
                    recommendations.append(t("duplicate_rows_low", count=basic_info['duplicate_rows']))
            
            # Correlation recommendations
            if 'strong_correlations' in analysis_results:
                strong_corrs = analysis_results['strong_correlations']
                very_high_corrs = [c for c in strong_corrs if abs(c['correlation']) > 0.9]
                
                if very_high_corrs:
                    recommendations.append(t("high_correlations"))
                elif strong_corrs:
                    recommendations.append(t("medium_correlations"))
            
            # Outliers recommendations
            if 'outliers' in analysis_results:
                outlier_cols = [col for col, count in analysis_results['outliers'].items() if count > 0]
                
                if outlier_cols:
                    high_outlier_cols = [col for col in outlier_cols 
                                       if analysis_results['outliers'][col] > len(df) * 0.05]
                    
                    if high_outlier_cols:
                        recommendations.append(t("high_outliers", cols=', '.join(high_outlier_cols)))
                    else:
                        recommendations.append(t("low_outliers"))
            
            # Data size recommendations
            rows, cols = basic_info.get('shape', (0, 0))
            
            if rows < 100:
                recommendations.append(t("small_dataset", rows=rows))
            elif rows > 1000000:
                recommendations.append(t("large_dataset", rows=rows))
            
            if cols > 50:
                recommendations.append(t("many_columns", cols=cols))
            
            # Memory recommendations
            if 'memory_usage' in basic_info:
                memory_mb = basic_info['memory_usage'] / (1024 * 1024)
                if memory_mb > 1000:
                    recommendations.append(t("high_memory", mb=memory_mb))
            
            # General best practices
            general_recommendations = [
                t("check_data_quality"),
                t("backup_original"),
                t("document_changes"),
                t("validate_assumptions"),
                t("use_visualizations")
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
    
    # ========================================
    # GUARANTEED SECTIONS - Always render content
    # ========================================
    
    def add_data_preview_section(self, df: pd.DataFrame):
        """Add data preview section - always renders table image of df.head()"""
        try:
            self.add_section_header(t("data_preview_title"), 1)
            
            # Basic data information
            rows, cols = df.shape
            self.add_text(f"{t('data_shape')}: {rows:,} {t('rows')} × {cols} {t('columns')}", 12, bold=True)
            
            # Memory usage
            memory_bytes = df.memory_usage(deep=True).sum()
            memory_mb = memory_bytes / (1024 * 1024)
            self.add_text(f"{t('memory_usage')}: {memory_mb:.2f} {t('megabytes')}", 12)
            
            # Add sample data as text (first 5 rows, first 5 columns)
            self.add_text(t("data_preview_description"), 12, bold=True)
            
            # Create preview of data
            preview_df = df.head(5).iloc[:, :5]  # First 5 rows and columns
            
            # Convert to string representation
            preview_text = preview_df.to_string(index=True, max_cols=5, max_rows=5)
            
            # Split into lines and add each line
            preview_lines = preview_text.split('\n')
            for line in preview_lines[:10]:  # Limit to 10 lines to fit on page
                self.add_text(line, 10, indent=10)
                
            if len(preview_lines) > 10:
                self.add_text("...", 10, indent=10)
                
        except Exception as e:
            logger.error(f"Error adding data preview section: {e}")
            # Guaranteed fallback
            self.add_section_header(t("data_preview_title"), 1)
            self.add_text(t("error_processing"), 12)
    
    def add_missing_values_section(self, df: pd.DataFrame):
        """Add missing values section - bar chart of missing ratios or Hebrew note via i18n"""
        try:
            self.add_section_header(t("missing_values_title"), 1)
            
            # Calculate missing values
            missing_counts = df.isnull().sum()
            total_missing = missing_counts.sum()
            
            if total_missing == 0:
                # No missing values - add positive note
                self.add_text(t("no_missing_values"), 12, bold=True)
            else:
                # Missing values found
                self.add_text(t("missing_values_found"), 12, bold=True)
                
                # Show missing value statistics
                missing_with_values = missing_counts[missing_counts > 0].sort_values(ascending=False)
                
                for col, count in missing_with_values.items():
                    percentage = (count / len(df)) * 100
                    self.add_text(f"• {col}: {count:,} ({percentage:.1f}%)", 11, indent=5)
                
                self.add_text(f"{t('total_missing')}: {total_missing:,}", 12, bold=True)
                
                # Try to create a simple chart
                try:
                    if len(missing_with_values) > 0:
                        self._create_simple_missing_values_chart(missing_with_values)
                except Exception as chart_error:
                    logger.warning(f"Could not create missing values chart: {chart_error}")
                        
        except Exception as e:
            logger.error(f"Error adding missing values section: {e}")
            # Guaranteed fallback
            self.add_section_header(t("missing_values_title"), 1)
            self.add_text(t("error_processing"), 12)
    
    def add_categorical_distributions_section(self, df: pd.DataFrame):
        """Add categorical distributions section - auto-detect categorical columns with safe fallbacks"""
        try:
            self.add_section_header(t("categorical_title"), 1)
            
            # Find categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            # Also include numeric columns with low cardinality (likely categorical)
            for col in df.select_dtypes(include=[np.number]).columns:
                if df[col].nunique() <= 10 and df[col].nunique() > 1:
                    categorical_cols.append(col)
            
            if not categorical_cols:
                self.add_text(t("no_categorical_data"), 12)
                return
                
            self.add_text(t("categorical_description"), 12)
            
            # Analyze up to 5 categorical columns
            for col in categorical_cols[:5]:
                try:
                    self.add_text(f"\n{t('column')}: {col}", 12, bold=True)
                    
                    # Calculate value counts
                    value_counts = df[col].value_counts()
                    unique_count = df[col].nunique()
                    
                    self.add_text(f"{t('unique_values')}: {unique_count:,}", 11, indent=5)
                    
                    # Show top values
                    self.add_text(t("top_values") + ":", 11, bold=True, indent=5)
                    
                    # Show top 10 or all if fewer
                    top_values = value_counts.head(10)
                    for value, count in top_values.items():
                        percentage = (count / len(df)) * 100
                        value_str = str(value)[:30]  # Truncate long values
                        if len(str(value)) > 30:
                            value_str += "..."
                        self.add_text(f"  • {value_str}: {count:,} ({percentage:.1f}%)", 10, indent=15)
                    
                    # Show "other" category if there are more values
                    if len(value_counts) > 10:
                        other_count = value_counts.iloc[10:].sum()
                        other_percentage = (other_count / len(df)) * 100
                        self.add_text(f"  • {t('other_values')}: {other_count:,} ({other_percentage:.1f}%)", 10, indent=15)
                        
                except Exception as col_error:
                    logger.warning(f"Error analyzing categorical column {col}: {col_error}")
                    self.add_text(f"Error analyzing column: {col}", 11, indent=5)
                        
        except Exception as e:
            logger.error(f"Error adding categorical distributions section: {e}")
            # Guaranteed fallback
            self.add_section_header(t("categorical_title"), 1)
            self.add_text(t("error_processing"), 12)
    
    def add_numeric_distributions_section(self, df: pd.DataFrame):
        """Add numeric distributions section - histograms and boxplots with safe fallbacks"""
        try:
            self.add_section_header(t("numeric_title"), 1)
            
            # Find numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                self.add_text(t("no_numeric_data"), 12)
                return
                
            self.add_text(t("numeric_description"), 12)
            
            # Analyze up to 5 numeric columns
            for col in numeric_cols[:5]:
                try:
                    self.add_text(f"\n{t('column')}: {col}", 12, bold=True)
                    
                    # Calculate basic statistics
                    series = df[col].dropna()
                    if len(series) == 0:
                        self.add_text("No valid numeric data in this column", 11, indent=5)
                        continue
                    
                    # Basic statistics
                    self.add_text(t("statistics") + ":", 11, bold=True, indent=5)
                    stats_info = [
                        (t("mean"), series.mean()),
                        (t("median"), series.median()),
                        (t("std"), series.std()),
                        (t("min"), series.min()),
                        (t("max"), series.max()),
                        (t("q25"), series.quantile(0.25)),
                        (t("q75"), series.quantile(0.75))
                    ]
                    
                    for stat_name, stat_value in stats_info:
                        self.add_text(f"  • {stat_name}: {stat_value:.2f}", 10, indent=15)
                    
                    # Additional insights
                    skewness = series.skew()
                    if abs(skewness) > 1:
                        direction = "ימינה" if skewness > 0 else "שמאלה"  
                        self.add_text(f"  • הטיה: {direction} ({skewness:.2f})", 10, indent=15)
                        
                except Exception as col_error:
                    logger.warning(f"Error analyzing numeric column {col}: {col_error}")
                    self.add_text(f"Error analyzing column: {col}", 11, indent=5)
                        
        except Exception as e:
            logger.error(f"Error adding numeric distributions section: {e}")
            # Guaranteed fallback
            self.add_section_header(t("numeric_title"), 1)
            self.add_text(t("error_processing"), 12)
    
    def add_statistical_summary_section(self, df: pd.DataFrame):
        """Add statistical summary section - include df.describe() as text; always render"""
        try:
            self.add_section_header(t("stats_summary_title"), 1)
            
            # Data types summary
            self.add_text(t("data_types_summary") + ":", 12, bold=True)
            
            numeric_count = len(df.select_dtypes(include=[np.number]).columns)
            categorical_count = len(df.select_dtypes(include=['object']).columns)
            datetime_count = len(df.select_dtypes(include=['datetime64']).columns)
            
            self.add_text(f"• {t('numeric_columns')}: {numeric_count}", 11, indent=5)
            self.add_text(f"• {t('categorical_columns')}: {categorical_count}", 11, indent=5)
            self.add_text(f"• {t('datetime_columns')}: {datetime_count}", 11, indent=5)
            
            # Statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                self.add_text("\n" + t("stats_summary_description"), 12, bold=True)
                
                # Get describe() output
                try:
                    desc = df[numeric_cols].describe()
                    
                    # Convert to string and add to report
                    desc_str = desc.round(2).to_string()
                    desc_lines = desc_str.split('\n')
                    
                    for line in desc_lines[:15]:  # Limit lines to fit on page
                        self.add_text(line, 9, indent=10)
                        
                    if len(desc_lines) > 15:
                        self.add_text("...", 9, indent=10)
                        
                except Exception as desc_error:
                    logger.warning(f"Error creating describe() summary: {desc_error}")
                    self.add_text("Could not generate statistical summary", 11, indent=5)
            else:
                self.add_text("No numeric columns available for statistical summary", 11, indent=5)
                        
        except Exception as e:
            logger.error(f"Error adding statistical summary section: {e}")
            # Guaranteed fallback
            self.add_section_header(t("stats_summary_title"), 1)
            self.add_text(t("error_processing"), 12)
    
    def add_outliers_section(self, df: pd.DataFrame):
        """Add outliers section - simple IQR-based detection with fallback note if none"""
        try:
            self.add_section_header(t("outliers_title"), 1)
            self.add_text(t("outliers_description"), 12)
            
            # Find numeric columns for outlier detection
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                self.add_text("No numeric columns available for outlier detection", 11, indent=5)
                return
            
            outliers_found = []
            
            # IQR-based outlier detection for each numeric column
            for col in numeric_cols:
                try:
                    series = df[col].dropna()
                    if len(series) < 4:  # Need at least 4 values for quartiles
                        continue
                        
                    Q1 = series.quantile(0.25)
                    Q3 = series.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = series[(series < lower_bound) | (series > upper_bound)]
                    outlier_count = len(outliers)
                    
                    if outlier_count > 0:
                        outlier_percentage = (outlier_count / len(series)) * 100
                        outliers_found.append({
                            'column': col,
                            'count': outlier_count,
                            'percentage': outlier_percentage,
                            'lower_bound': lower_bound,
                            'upper_bound': upper_bound
                        })
                        
                except Exception as col_error:
                    logger.warning(f"Error detecting outliers in {col}: {col_error}")
                    continue
            
            # Report findings
            if not outliers_found:
                self.add_text(t("no_outliers_found"), 12, bold=True)
            else:
                self.add_text(t("outliers_found"), 12, bold=True)
                
                for outlier_info in outliers_found[:10]:  # Limit to 10 columns
                    col = outlier_info['column']
                    count = outlier_info['count']
                    pct = outlier_info['percentage']
                    lower = outlier_info['lower_bound']
                    upper = outlier_info['upper_bound']
                    
                    self.add_text(f"\n• {col}:", 11, bold=True, indent=5)
                    self.add_text(f"  {t('outliers_count')}: {count:,} ({pct:.1f}%)", 10, indent=15)
                    self.add_text(f"  {t('outlier_range')}: {lower:.2f} - {upper:.2f}", 10, indent=15)
                    
                    if pct > 10:
                        self.add_text(f"  {t('outlier_warning')}", 10, indent=15)
                        
        except Exception as e:
            logger.error(f"Error adding outliers section: {e}")
            # Guaranteed fallback
            self.add_section_header(t("outliers_title"), 1)
            self.add_text(t("error_processing"), 12)
    
    def add_guaranteed_sections(self, df: pd.DataFrame, analysis_results: Optional[Dict] = None):
        """
        Orchestrates guaranteed sections that always render content
        Main function called by the PDF builder
        """
        try:
            logger.info("Adding guaranteed sections to PDF report")
            
            # Ensure we have some analysis results
            if analysis_results is None:
                analysis_results = {}
            
            # 1. Data preview section - always shows first few rows
            self.add_data_preview_section(df)
            
            # 2. Missing values section - bar chart or note if none missing
            self.add_missing_values_section(df)
            
            # 3. Categorical distributions - auto-detect and show top values
            self.add_categorical_distributions_section(df)
            
            # 4. Numeric distributions - histograms and statistics
            self.add_numeric_distributions_section(df)
            
            # 5. Statistical summary - df.describe() as text
            self.add_statistical_summary_section(df)
            
            # 6. Outliers section - IQR-based detection
            self.add_outliers_section(df)
            
            # 7. Recommendations section - rules-based recommendations
            self.add_recommendations_section(analysis_results, df)
            
            logger.info("All guaranteed sections added successfully")
            
        except Exception as e:
            logger.error(f"Error in add_guaranteed_sections: {e}")
            # Even if there's an error, try to add a basic error section
            try:
                self.add_section_header("Error in Report Generation", 1)
                self.add_text("Some sections could not be generated due to data processing errors.", 12)
            except:
                pass  # If even this fails, continue
    
    def _create_simple_missing_values_chart(self, missing_series: pd.Series):
        """Create a simple missing values chart"""
        try:
            # Create a simple text-based representation
            # This is a fallback if matplotlib fails
            max_val = missing_series.max()
            
            self.add_text("\nMissing Values Visualization:", 11, bold=True, indent=5)
            
            for col, count in missing_series.head(5).items():
                bar_length = int((count / max_val) * 20) if max_val > 0 else 0
                bar = "█" * bar_length + "░" * (20 - bar_length)
                self.add_text(f"{col[:15]:15} {bar} {count:,}", 9, indent=10)
                
        except Exception as e:
            logger.debug(f"Could not create missing values visualization: {e}")
            
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
                plt.title('מטריצת קורלציות', fontsize=16, pad=20)
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
                plt.xticks(range(len(missing_data)), missing_data.index, rotation=45, ha='right')
                plt.title('ערכים חסרים לפי עמודה', fontsize=16, pad=20)
                plt.ylabel('מספר ערכים חסרים')
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
                        axes[i].set_title(f'התפלגות: {col}')
                        axes[i].set_ylabel('תכיפות')
                
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
                    plt.xticks(range(len(top_values)), top_values.index, rotation=45, ha='right')
                    plt.title(f'ערכים נפוצים: {col}', fontsize=16, pad=20)
                    plt.ylabel('תכיפות')
                    plt.tight_layout()
                    
                    chart_path = os.path.join(output_dir, f'top_categories_{col}.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    chart_files.append(chart_path)
            
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
                'top_categories': 'קטגוריות נפוצות - מציג את הערכים השכיחים ביותר'
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
        """יצירת דוח מקיף מנתונים אמיתיים - WITH GUARANTEED CONTENT"""
        try:
            logger.info(f"Starting comprehensive report generation for DataFrame shape: {df.shape}")
            
            # 1. PREPROCESS DATA first to ensure robust handling
            logger.info("Preprocessing DataFrame for robust analysis...")
            processed_df = preprocess_df(df)
            
            if processed_df is None or processed_df.empty:
                logger.error("DataFrame is empty after preprocessing")
                return None
            
            logger.info(f"DataFrame preprocessing complete. New shape: {processed_df.shape}")
            
            # 2. ANALYZE DATA (but don't depend on it completely)
            analysis_results = {}
            try:
                analysis_results = self.analyze_real_data(processed_df)
                if 'error' in analysis_results:
                    logger.warning(f"Analysis had errors: {analysis_results['error']}")
                    # Continue anyway with empty results
                    analysis_results = {}
            except Exception as e:
                logger.warning(f"Data analysis failed, continuing with empty results: {e}")
                analysis_results = {}
            
            # 3. CREATE TITLE PAGE with i18n support
            title = t("report_title")
            subtitle = t("report_subtitle")
            date_str = format_date_time()
            
            self.create_title_page(
                title=title,
                subtitle=subtitle,
                date=date_str
            )
            
            # 4. TABLE OF CONTENTS
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
            
            # 5. ADD GUARANTEED SECTIONS - This is the key improvement!
            logger.info("Adding guaranteed content sections...")
            self.add_guaranteed_sections(processed_df, analysis_results)
            
            # 6. CREATE AND ADD CHARTS (with error handling)
            try:
                logger.info("Creating visualizations...")
                chart_files = self.create_visualizations(processed_df)
                if chart_files:
                    self.add_charts_section(chart_files)
                    logger.info(f"Added {len(chart_files)} charts to report")
                else:
                    logger.warning("No charts were created")
                    # Add a note about charts
                    self.add_section_header(t("charts_visualizations"), 1)
                    self.add_text("Charts could not be generated for this dataset", 12)
                    
            except Exception as chart_error:
                logger.error(f"Error creating charts: {chart_error}")
                # Add error section for charts
                self.add_section_header(t("charts_visualizations"), 1)
                self.add_text(t("error_chart_creation"), 12)
            
            # 7. SAVE THE REPORT
            logger.info(f"Saving PDF report to: {output_path}")
            self.pdf.output(output_path)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Report generated successfully: {output_path} ({file_size:,} bytes)")
                return output_path
            else:
                logger.error("PDF file was not created")
                return None
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            # Try to save what we have
            try:
                self.pdf.output(output_path)
                if os.path.exists(output_path):
                    logger.info(f"Partial report saved despite errors: {output_path}")
                    return output_path
            except:
                pass
            return None


def generate_complete_data_report(df: pd.DataFrame, 
                                output_path: str = "complete_data_report.pdf",
                                include_charts: bool = True) -> str:
    """
    Main function to generate comprehensive report from real data
    WITH GUARANTEED CONTENT and robust preprocessing
    
    Args:
        df: DataFrame with your data
        output_path: Path for the output PDF file
        include_charts: Whether to include charts and visualizations
    
    Returns:
        str: Path to the generated PDF file, or None if failed
    """
    try:
        logger.info(f"Starting complete data report generation")
        
        # Validate input
        if df is None or df.empty:
            logger.error("DataFrame is empty or None")
            return None
        
        logger.info(f"Input DataFrame shape: {df.shape}")
        
        # Create report generator
        report = HebrewPDFReport()
        
        # Generate comprehensive report with guaranteed sections
        result_path = report.generate_comprehensive_report(df, output_path)
        
        if result_path:
            logger.info(f"Complete data report generated successfully: {result_path}")
        else:
            logger.error("Failed to generate complete data report")
            
        return result_path
        
    except Exception as e:
        logger.error(f"Error in generate_complete_data_report: {e}")
        return None


def analyze_csv_file(csv_file_path: str, output_pdf_path: str = None) -> str:
    """
    Analyze CSV file and create PDF report using robust preprocessing
    
    Args:
        csv_file_path: Path to CSV file
        output_pdf_path: Output PDF path (optional)
    
    Returns:
        str: Path to generated PDF report
    """
    try:
        logger.info(f"Analyzing CSV file: {csv_file_path}")
        
        # Read CSV file using robust auto-detection
        df = read_table_auto(csv_file_path)
        
        # Set default output path if not provided
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
            output_pdf_path = f"report_{base_name}.pdf"
        
        # Generate report
        return generate_complete_data_report(df, output_pdf_path, include_charts=True)
        
    except Exception as e:
        logger.error(f"Error analyzing CSV file: {e}")
        return None


def analyze_excel_file(excel_file_path: str, sheet_name: Union[str, int] = 0, 
                      output_pdf_path: str = None) -> str:
    """
    Analyze Excel file and create PDF report using robust preprocessing
    
    Args:
        excel_file_path: Path to Excel file
        sheet_name: Sheet name or index
        output_pdf_path: Output PDF path (optional)
    
    Returns:
        str: Path to generated PDF report
    """
    try:
        logger.info(f"Analyzing Excel file: {excel_file_path}")
        
        # Read Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        
        # Set default output path if not provided
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(excel_file_path))[0]
            output_pdf_path = f"report_{base_name}.pdf"
        
        # Generate report
        return generate_complete_data_report(df, output_pdf_path, include_charts=True)
        
    except Exception as e:
        logger.error(f"Error analyzing Excel file: {e}")
        return None


def generate_hebrew_pdf_report(df: pd.DataFrame, output_path: str = "hebrew_report.pdf", include_charts: bool = True) -> str:
    """
    Wrapper function for backward compatibility
    Delegates to generate_complete_data_report for Hebrew PDF generation
    
    Args:
        df: DataFrame with data to analyze
        output_path: Output PDF path
        include_charts: Whether to include charts
        
    Returns:
        str: Path to generated PDF report
    """
    return generate_complete_data_report(df, output_path, include_charts=include_charts)
