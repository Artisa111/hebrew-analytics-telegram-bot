# -*- coding: utf-8 -*-
"""
מודול יצירת דוחות PDF - PDF report generation module with Hebrew support
"""

from fpdf import FPDF
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image
import io
try:
    import arabic_reshaper  # for proper RTL shaping (safe for Hebrew)
    from bidi.algorithm import get_display
except Exception:
    arabic_reshaper = None
    get_display = None

logger = logging.getLogger(__name__)

class HebrewPDFReport:
    def __init__(self):
        self.pdf = FPDF()
        self.setup_hebrew_support()
        self.current_y = 0
        self.page_width = 210
        self.page_height = 297
        self.margin = 20
    
    def _rtl_text(self, text: str) -> str:
        """Return visually-correct RTL text using bidi/arabic_reshaper if available."""
        try:
            s = "" if text is None else str(text)
            if arabic_reshaper and get_display:
                s = arabic_reshaper.reshape(s)
                s = get_display(s)
            return s
        except Exception:
            return str(text)
    
    def setup_hebrew_support(self):
        """הגדרת תמיכה בעברית ל-PDF (ניסיון לטעון פונט יוניקוד ממערכת ההפעלה)."""
        try:
            font_candidates = [
                # Common Linux paths
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                # Windows Arial
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/arialbd.ttf',
            ]
            regular = None
            bold = None
            # Locate regular and bold
            for path in font_candidates:
                if os.path.exists(path):
                    if path.lower().endswith('bold.ttf') or path.lower().endswith('bd.ttf'):
                        bold = path
                    else:
                        regular = path if regular is None else regular
                        if 'DejaVuSans.ttf' in path and os.path.exists(path.replace('.ttf', '-Bold.ttf')):
                            bold = path.replace('.ttf', '-Bold.ttf')
            if regular:
                self.pdf.add_font('DejaVu', '', regular, uni=True)
                if bold and os.path.exists(bold):
                    self.pdf.add_font('DejaVu', 'B', bold, uni=True)
                else:
                    self.pdf.add_font('DejaVu', 'B', regular, uni=True)
                self.pdf.set_font('DejaVu', '', 12)
            else:
                # Fallback to core font (might not fully support Hebrew but keeps PDF working)
                self.pdf.set_font('Arial', '', 12)

            self.pdf.set_auto_page_break(auto=True, margin=15)
            self.pdf.set_margins(self.margin, self.margin, self.margin)

        except Exception as e:
            logger.warning(f"Could not load Hebrew fonts: {e}")
            self.pdf.set_font('Arial', '', 12)
    
    def create_title_page(self, title: str, subtitle: str = None, 
                         company: str = "בוט ניתוח נתונים", date: str = None):
        """יצירת דף כותרת"""
        try:
            self.pdf.add_page()
            self.pdf.set_font('DejaVu', 'B', 24)
            
            # כותרת ראשית
            title_width = self.pdf.get_string_width(title)
            title_x = (self.page_width - title_width) / 2
            self.pdf.text(title_x, 80, title)
            
            # כותרת משנה
            if subtitle:
                self.pdf.set_font('DejaVu', '', 16)
                subtitle_width = self.pdf.get_string_width(subtitle)
                subtitle_x = (self.page_width - subtitle_width) / 2
                self.pdf.text(subtitle_x, 100, subtitle)
            
            # שם החברה
            self.pdf.set_font('DejaVu', 'B', 14)
            company_width = self.pdf.get_string_width(company)
            company_x = (self.page_width - company_width) / 2
            self.pdf.text(company_x, 120, company)
            
            # תאריך
            if date is None:
                date = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            self.pdf.set_font('DejaVu', '', 12)
            date_width = self.pdf.get_string_width(date)
            date_x = (self.page_width - date_width) / 2
            self.pdf.text(date_x, 140, date)
            
            # קו מפריד
            self.pdf.line(30, 160, 180, 160)
            
            self.current_y = 180
            
        except Exception as e:
            logger.error(f"Error creating title page: {e}")
    
    def add_section_header(self, title: str, level: int = 1):
        """הוספת כותרת סעיף"""
        try:
            if level == 1:
                self.pdf.set_font('DejaVu', 'B', 18)
                self.current_y += 20
            elif level == 2:
                self.pdf.set_font('DejaVu', 'B', 14)
                self.current_y += 15
            else:
                self.pdf.set_font('DejaVu', 'B', 12)
                self.current_y += 10
            
            # בדיקה אם צריך דף חדש
            if self.current_y > self.page_height - 50:
                self.pdf.add_page()
                self.current_y = self.margin
            
            # Right aligned for RTL
            self.pdf.set_xy(self.margin, self.current_y)
            self.pdf.cell(0, 10, self._rtl_text(title), align='R')
            self.current_y += 10
            
        except Exception as e:
            logger.error(f"Error adding section header: {e}")
    
    def add_text(self, text: str, font_size: int = 12, bold: bool = False):
        """הוספת טקסט רגיל"""
        try:
            if bold:
                self.pdf.set_font('DejaVu', 'B', font_size)
            else:
                self.pdf.set_font('DejaVu', '', font_size)
            
            # בדיקה אם צריך דף חדש
            if self.current_y > self.page_height - 50:
                self.pdf.add_page()
                self.current_y = self.margin
            
            self.pdf.set_xy(self.margin, self.current_y)
            self.pdf.multi_cell(0, font_size * 0.5, self._rtl_text(text), align='R')
            self.current_y = self.pdf.get_y() + 5
            
        except Exception as e:
            logger.error(f"Error adding text: {e}")
    
    def add_data_summary(self, basic_info: Dict[str, Any]):
        """הוספת סיכום נתונים בסיסי"""
        try:
            self.add_section_header("סיכום נתונים", 1)
            
            # מידע על גודל הנתונים
            if 'shape' in basic_info:
                rows, cols = basic_info['shape']
                self.add_text(f"מספר שורות: {rows:,}", 12)
                self.add_text(f"מספר עמודות: {cols}", 12)
            
            # מידע על זיכרון
            if 'memory_usage' in basic_info:
                memory_mb = basic_info['memory_usage'] / (1024 * 1024)
                self.add_text(f"שימוש זיכרון: {memory_mb:.2f} MB", 12)
            
            # מידע על ערכים חסרים
            if 'null_counts' in basic_info:
                total_nulls = sum(basic_info['null_counts'].values())
                if total_nulls > 0:
                    self.add_text(f"סך ערכים חסרים: {total_nulls:,}", 12)
                else:
                    self.add_text("אין ערכים חסרים בנתונים", 12)
            
            # מידע על כפילויות
            if 'duplicate_rows' in basic_info:
                dup_count = basic_info['duplicate_rows']
                if dup_count > 0:
                    self.add_text(f"מספר שורות כפולות: {dup_count}", 12)
                else:
                    self.add_text("אין שורות כפולות בנתונים", 12)
            
        except Exception as e:
            logger.error(f"Error adding data summary: {e}")
    
    def add_column_details(self, column_info: Dict[str, Any]):
        """הוספת פרטי עמודות"""
        try:
            self.add_section_header("פרטי עמודות", 2)
            
            for col_name, col_details in column_info.items():
                self.add_text(f"עמודה: {col_name}", 12, bold=True)
                
                if 'type' in col_details:
                    self.add_text(f"  סוג: {col_details['type']}", 10)
                
                if 'unique_values' in col_details:
                    self.add_text(f"  ערכים ייחודיים: {col_details['unique_values']:,}", 10)
                
                if 'null_count' in col_details:
                    null_pct = col_details.get('null_percentage', 0)
                    self.add_text(f"  ערכים חסרים: {col_details['null_count']:,} ({null_pct}%)", 10)
                
                # סטטיסטיקות לעמודות מספריות
                if 'mean' in col_details:
                    self.add_text(f"  ממוצע: {col_details['mean']:.2f}", 10)
                    self.add_text(f"  חציון: {col_details['median']:.2f}", 10)
                    self.add_text(f"  סטיית תקן: {col_details['std']:.2f}", 10)
                    self.add_text(f"  מינימום: {col_details['min']:.2f}", 10)
                    self.add_text(f"  מקסימום: {col_details['max']:.2f}", 10)
                
                self.current_y += 5
            
        except Exception as e:
            logger.error(f"Error adding column details: {e}")
    
    def add_insights(self, insights: List[str]):
        """הוספת תובנות"""
        try:
            self.add_section_header("תובנות עיקריות", 1)
            
            for i, insight in enumerate(insights, 1):
                self.add_text(f"{i}. {insight}", 12)
            
        except Exception as e:
            logger.error(f"Error adding insights: {e}")
    
    def add_correlation_analysis(self, correlation_data: Dict[str, Any]):
        """הוספת ניתוח קורלציה"""
        try:
            if not correlation_data or 'strong_correlations' not in correlation_data:
                return
            
            self.add_section_header("ניתוח קורלציה", 2)
            
            strong_corrs = correlation_data['strong_correlations']
            if strong_corrs:
                self.add_text("קורלציות חזקות שנמצאו:", 12, bold=True)
                
                for corr in strong_corrs:
                    corr_text = f"• {corr['column1']} ↔ {corr['column2']}: {corr['correlation']:.3f}"
                    self.add_text(corr_text, 10)
            else:
                self.add_text("לא נמצאו קורלציות חזקות בין העמודות", 12)
            
        except Exception as e:
            logger.error(f"Error adding correlation analysis: {e}")
    
    def add_trend_analysis(self, trends: Dict[str, Any]):
        """הוספת ניתוח מגמות"""
        try:
            if not trends:
                return
            
            self.add_section_header("ניתוח מגמות", 2)
            
            if 'trend_direction' in trends:
                self.add_text(f"כיוון מגמה כללי: {trends['trend_direction']}", 12)
            
            if 'trend_strength' in trends:
                strength = trends['trend_strength']
                if strength > 0.1:
                    strength_desc = "חזקה"
                elif strength > 0.05:
                    strength_desc = "בינונית"
                else:
                    strength_desc = "חלשה"
                
                self.add_text(f"עוצמת מגמה: {strength_desc}", 12)
            
            # ניתוח שינויים יחסיים
            relative_changes = {k: v for k, v in trends.items() if 'relative_change' in k}
            if relative_changes:
                self.add_text("שינויים יחסיים בעמודות:", 12, bold=True)
                for col, change in relative_changes.items():
                    col_name = col.replace('_relative_change', '')
                    change_pct = change * 100
                    self.add_text(f"  {col_name}: {change_pct:+.1f}%", 10)
            
        except Exception as e:
            logger.error(f"Error adding trend analysis: {e}")
    
    def add_segmentation_analysis(self, segmentation: Dict[str, Any]):
        """הוספת ניתוח פילוח"""
        try:
            if not segmentation or 'cluster_analysis' not in segmentation:
                return
            
            self.add_section_header("ניתוח פילוח וקבצים", 2)
            
            cluster_analysis = segmentation['cluster_analysis']
            self.add_text(f"מספר קבצים שנוצרו: {len(cluster_analysis)}", 12)
            
            for cluster_name, cluster_data in cluster_analysis.items():
                self.add_text(f"קבץ {cluster_name}:", 12, bold=True)
                self.add_text(f"  גודל: {cluster_data['size']:,} רשומות ({cluster_data['percentage']}%)", 10)
                
                # מאפיינים של הקבץ
                if 'characteristics' in cluster_data:
                    self.add_text("  מאפיינים:", 10)
                    for col, stats in cluster_data['characteristics'].items():
                        self.add_text(f"    {col}: ממוצע={stats['mean']:.2f}, סטת={stats['std']:.2f}", 9)
                
                self.current_y += 5
            
        except Exception as e:
            logger.error(f"Error adding segmentation analysis: {e}")
    
    def add_recommendations(self, analysis_results: Dict[str, Any]):
        """הוספת המלצות אוטומטיות"""
        try:
            self.add_section_header("המלצות", 1)
            
            recommendations = []
            
            # המלצות על בסיס איכות הנתונים
            if 'basic_info' in analysis_results:
                basic_info = analysis_results['basic_info']
                
                if 'null_counts' in basic_info:
                    total_nulls = sum(basic_info['null_counts'].values())
                    total_cells = basic_info['shape'][0] * basic_info['shape'][1]
                    null_percentage = (total_nulls / total_cells) * 100
                    
                    if null_percentage > 20:
                        recommendations.append("יש אחוז גבוה של ערכים חסרים. מומלץ לבדוק את מקור הנתונים ולשקול אסטרטגיות מילוי.")
                    elif null_percentage > 5:
                        recommendations.append("יש ערכים חסרים בנתונים. מומלץ לטפל בהם לפני הניתוח.")
                
                if 'duplicate_rows' in basic_info and basic_info['duplicate_rows'] > 0:
                    recommendations.append("נמצאו שורות כפולות. מומלץ לנקות אותן לפני הניתוח.")
            
            # המלצות על בסיס קורלציות
            if 'correlation_matrix' in analysis_results:
                corr_matrix = analysis_results['correlation_matrix']
                if not corr_matrix.empty:
                    high_corr_count = len([(i, j) for i in range(len(corr_matrix.columns)) 
                                        for j in range(i+1, len(corr_matrix.columns)) 
                                        if abs(corr_matrix.iloc[i, j]) > 0.8])
                    
                    if high_corr_count > 0:
                        recommendations.append(f"נמצאו {high_corr_count} קורלציות גבוהות מאוד. שקול להסיר עמודות מיותרות.")
            
            # המלצות על בסיס מגמות
            if 'trends' in analysis_results:
                trends = analysis_results['trends']
                if 'trend_direction' in trends:
                    if trends['trend_direction'] == 'עולה':
                        recommendations.append("הנתונים מראים מגמה עולה. שקול לבדוק אם יש גורמים חיצוניים המשפיעים על המגמה.")
                    elif trends['trend_direction'] == 'יורדת':
                        recommendations.append("הנתונים מראים מגמה יורדת. מומלץ לחקור את הסיבות לירידה.")
            
            # המלצות כלליות
            recommendations.extend([
                "בדוק תמיד את איכות הנתונים לפני הניתוח",
                "שקול להשתמש בטכניקות נרמול אם יש הבדלים גדולים בסדרי גודל בין עמודות",
                "בדוק ערכים חריגים והחלט אם להסיר או לטפל בהם",
                "שקול להשתמש בטכניקות דגימה אם הנתונים גדולים מדי"
            ])
            
            # הוספת ההמלצות לדוח
            for i, rec in enumerate(recommendations, 1):
                self.add_text(f"{i}. {rec}", 11)
            
        except Exception as e:
            logger.error(f"Error adding recommendations: {e}")
    
    def add_chart(self, chart_file_path: str, caption: str = ""):
        """הוספת תרשים לדוח"""
        try:
            if not os.path.exists(chart_file_path):
                logger.warning(f"Chart file not found: {chart_file_path}")
                return
            
            # בדיקה אם צריך דף חדש
            if self.current_y > self.page_height - 150:
                self.pdf.add_page()
                self.current_y = self.margin
            
            # הוספת התרשים
            self.pdf.image(chart_file_path, x=self.margin, y=self.current_y, 
                          w=self.page_width - 2 * self.margin, h=100)
            
            self.current_y += 110
            
            # הוספת כיתוב
            if caption:
                self.pdf.set_font('DejaVu', '', 10)
                self.pdf.text(self.margin, self.current_y, caption)
                self.current_y += 15
            
        except Exception as e:
            logger.error(f"Error adding chart: {e}")
    
    def _wrap_text(self, text: str, max_width: float) -> List[str]:
        """חלוקת טקסט ארוך לשורות"""
        try:
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.pdf.get_string_width(test_line) <= max_width:
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
    
    def generate_report(self, analysis_results: Dict[str, Any], 
                       chart_files: List[str] = None, 
                       output_path: str = "analysis_report.pdf") -> str:
        """יצירת הדוח המלא"""
        try:
            # דף כותרת
            self.create_title_page(
                title="דוח ניתוח נתונים",
                subtitle="סיכום מקיף של הניתוח והתובנות",
                date=datetime.now().strftime("%d/%m/%Y %H:%M")
            )
            
            # תוכן עניינים
            self.add_section_header("תוכן עניינים", 1)
            self.add_text("1. סיכום נתונים", 12, bold=True)
            self.add_text("2. פרטי עמודות", 12, bold=True)
            self.add_text("3. תובנות עיקריות", 12, bold=True)
            self.add_text("4. ניתוח קורלציה", 12, bold=True)
            self.add_text("5. ניתוח מגמות", 12, bold=True)
            self.add_text("6. ניתוח פילוח", 12, bold=True)
            self.add_text("7. המלצות", 12, bold=True)
            self.add_text("8. תרשימים", 12, bold=True)
            
            # הוספת תוכן הדוח
            if 'basic_info' in analysis_results:
                self.add_data_summary(analysis_results['basic_info'])
                
                if 'column_details' in analysis_results['basic_info']:
                    self.add_column_details(analysis_results['basic_info']['column_details'])
            
            if 'insights' in analysis_results:
                self.add_insights(analysis_results['insights'])
            
            if 'correlation_matrix' in analysis_results:
                self.add_correlation_analysis(analysis_results)
            
            if 'trends' in analysis_results:
                self.add_trend_analysis(analysis_results['trends'])
            
            if 'segmentation' in analysis_results:
                self.add_segmentation_analysis(analysis_results['segmentation'])
            
            # הוספת המלצות
            self.add_recommendations(analysis_results)
            
            # הוספת תרשימים
            if chart_files:
                self.add_section_header("תרשימים", 1)
                for i, chart_file in enumerate(chart_files):
                    caption = f"תרשים {i+1}"
                    self.add_chart(chart_file, caption)
            
            # שמירת הדוח
            self.pdf.output(output_path)
            logger.info(f"PDF report generated successfully: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return None

def generate_hebrew_pdf_report(analysis_results: Dict[str, Any], 
                              chart_files: List[str] = None,
                              output_path: str = "analysis_report.pdf") -> str:
    """פונקציה עזר ליצירת דוח PDF בעברית"""
    try:
        report_generator = HebrewPDFReport()
        return report_generator.generate_report(analysis_results, chart_files, output_path)
    except Exception as e:
        logger.error(f"Error in generate_hebrew_pdf_report: {e}")
        return None
