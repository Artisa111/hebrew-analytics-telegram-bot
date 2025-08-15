# -*- coding: utf-8 -*-
"""
מודול הויזואליזציה - Visualization module for creating charts and graphs with Hebrew support
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from config import CHART_CONFIG
import matplotlib.font_manager as fm

logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        self.setup_hebrew_fonts()
        self.chart_count = 0
    
    def setup_hebrew_fonts(self):
        """הגדרת פונטים עבריים לתרשימים"""
        try:
            # ניסיון להשתמש בפונט עברי
            hebrew_fonts = ['Arial', 'David', 'DejaVu Sans', 'Liberation Sans']
            
            for font in hebrew_fonts:
                try:
                    plt.rcParams['font.family'] = font
                    # בדיקה אם הפונט עובד
                    test_fig, test_ax = plt.subplots()
                    test_ax.text(0.5, 0.5, 'אבג', fontsize=12)
                    plt.close(test_fig)
                    logger.info(f"Hebrew font {font} set successfully")
                    break
                except:
                    continue
            
            # הגדרת סגנון התרשימים
            plt.style.use(CHART_CONFIG['style'])
            plt.rcParams['figure.figsize'] = CHART_CONFIG['figure_size']
            plt.rcParams['figure.dpi'] = CHART_CONFIG['dpi']
            
        except Exception as e:
            logger.warning(f"Could not set Hebrew fonts: {e}")
            # שימוש בפונט ברירת מחדל
            plt.rcParams['font.family'] = 'DejaVu Sans'
    
    def create_bar_chart(self, df: pd.DataFrame, x_column: str, y_column: str, 
                         title: str = "תרשים עמודות", max_bars: int = 20) -> str:
        """יצירת תרשים עמודות"""
        try:
            # הגבלת מספר העמודות אם יש יותר מדי
            if len(df) > max_bars:
                df_sorted = df.nlargest(max_bars, y_column)
                title += f" (Top {max_bars})"
            else:
                df_sorted = df.sort_values(y_column, ascending=False)
            
            plt.figure(figsize=CHART_CONFIG['figure_size'])
            
            # יצירת התרשים
            bars = plt.bar(range(len(df_sorted)), df_sorted[y_column], 
                          color=sns.color_palette("husl", len(df_sorted)))
            
            # הגדרת תוויות
            plt.xlabel(x_column, fontsize=12)
            plt.ylabel(y_column, fontsize=12)
            plt.title(title, fontsize=14, fontweight='bold')
            
            # הגדרת תוויות ציר X
            plt.xticks(range(len(df_sorted)), df_sorted[x_column], rotation=45, ha='right')
            
            # הוספת ערכים על העמודות
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{height:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # שמירת התרשים
            filename = self._save_chart("bar_chart")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            return None
    
    def create_line_chart(self, df: pd.DataFrame, x_column: str, y_column: str,
                         title: str = "תרשים קווי") -> str:
        """יצירת תרשים קווי"""
        try:
            plt.figure(figsize=CHART_CONFIG['figure_size'])
            
            # מיון לפי עמודת X
            df_sorted = df.sort_values(x_column)
            
            # יצירת התרשים
            plt.plot(df_sorted[x_column], df_sorted[y_column], 
                    marker='o', linewidth=2, markersize=6)
            
            # הגדרת תוויות
            plt.xlabel(x_column, fontsize=12)
            plt.ylabel(y_column, fontsize=12)
            plt.title(title, fontsize=14, fontweight='bold')
            
            # סיבוב תוויות ציר X אם יש צורך
            if len(df_sorted) > 10:
                plt.xticks(rotation=45, ha='right')
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            filename = self._save_chart("line_chart")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            return None
    
    def create_pie_chart(self, df: pd.DataFrame, value_column: str, 
                         label_column: str = None, title: str = "תרשים עוגה") -> str:
        """יצירת תרשים עוגה"""
        try:
            plt.figure(figsize=CHART_CONFIG['figure_size'])
            
            if label_column is None:
                # שימוש באינדקס כתוויות
                labels = df.index.astype(str)
            else:
                labels = df[label_column].astype(str)
            
            values = df[value_column]
            
            # הגבלה למספר קטגוריות אם יש יותר מדי
            if len(values) > 10:
                # שמירה על הקטגוריות הגדולות ביותר
                threshold = values.quantile(0.9)
                mask = values >= threshold
                values = values[mask]
                labels = labels[mask]
                title += " (Top Categories)"
            
            # יצירת התרשים
            colors = plt.cm.Set3(np.linspace(0, 1, len(values)))
            wedges, texts, autotexts = plt.pie(values, labels=labels, autopct='%1.1f%%',
                                              colors=colors, startangle=90)
            
            plt.title(title, fontsize=14, fontweight='bold')
            
            # הגדרת תוויות
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            filename = self._save_chart("pie_chart")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            return None
    
    def create_histogram(self, df: pd.DataFrame, column: str, 
                        title: str = "היסטוגרמה", bins: int = 20) -> str:
        """יצירת היסטוגרמה"""
        try:
            plt.figure(figsize=CHART_CONFIG['figure_size'])
            
            # יצירת ההיסטוגרמה
            plt.hist(df[column].dropna(), bins=bins, edgecolor='black', alpha=0.7, color='skyblue')
            
            # הוספת קו ממוצע
            mean_val = df[column].mean()
            plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                       label=f'ממוצע: {mean_val:.2f}')
            
            # הגדרת תוויות
            plt.xlabel(column, fontsize=12)
            plt.ylabel('תדירות', fontsize=12)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filename = self._save_chart("histogram")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating histogram: {e}")
            return None
    
    def create_scatter_plot(self, df: pd.DataFrame, x_column: str, y_column: str,
                           color_column: str = None, title: str = "תרשים פיזור") -> str:
        """יצירת תרשים פיזור"""
        try:
            plt.figure(figsize=CHART_CONFIG['figure_size'])
            
            if color_column and color_column in df.columns:
                # פיזור עם צבעים לפי עמודה שלישית
                scatter = plt.scatter(df[x_column], df[y_column], 
                                    c=df[color_column], cmap='viridis', alpha=0.7)
                plt.colorbar(scatter, label=color_column)
            else:
                # פיזור רגיל
                plt.scatter(df[x_column], df[y_column], alpha=0.7, color='blue')
            
            # הוספת קו מגמה
            if len(df) > 2:
                z = np.polyfit(df[x_column].dropna(), df[y_column].dropna(), 1)
                p = np.poly1d(z)
                plt.plot(df[x_column], p(df[x_column]), "r--", alpha=0.8, linewidth=2)
            
            # הגדרת תוויות
            plt.xlabel(x_column, fontsize=12)
            plt.ylabel(y_column, fontsize=12)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filename = self._save_chart("scatter_plot")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating scatter plot: {e}")
            return None
    
    def create_box_plot(self, df: pd.DataFrame, column: str, 
                        group_column: str = None, title: str = "תרשים קופסה") -> str:
        """יצירת תרשים קופסה"""
        try:
            plt.figure(figsize=CHART_CONFIG['figure_size'])
            
            if group_column and group_column in df.columns:
                # תרשים קופסה מקבוצע לפי קבוצה
                df.boxplot(column=column, by=group_column, ax=plt.gca())
                plt.title(f"{title} לפי {group_column}", fontsize=14, fontweight='bold')
            else:
                # תרשים קופסה פשוט
                plt.boxplot(df[column].dropna())
                plt.title(title, fontsize=14, fontweight='bold')
            
            plt.ylabel(column, fontsize=12)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filename = self._save_chart("box_plot")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating box plot: {e}")
            return None
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame, 
                                 title: str = "מפת קורלציה") -> str:
        """יצירת מפת קורלציה"""
        try:
            plt.figure(figsize=(10, 8))
            
            # יצירת מפת החום
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                       center=0, square=True, linewidths=0.5)
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            filename = self._save_chart("correlation_heatmap")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {e}")
            return None
    
    def create_insights_chart(self, insights: List[str], title: str = "תובנות עיקריות") -> str:
        """יצירת תרשים ויזואלי של התובנות"""
        try:
            plt.figure(figsize=(12, 8))
            
            # יצירת תרשים טקסטואלי
            y_positions = np.arange(len(insights))
            plt.barh(y_positions, [1] * len(insights), color='lightblue', alpha=0.7)
            
            # הוספת הטקסט
            for i, insight in enumerate(insights):
                plt.text(0.1, i, insight, fontsize=10, va='center', ha='left')
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('תובנות', fontsize=12)
            plt.yticks([])
            plt.xlim(0, 1.2)
            
            plt.tight_layout()
            
            filename = self._save_chart("insights_chart")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating insights chart: {e}")
            return None
    
    def create_comprehensive_dashboard(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> List[str]:
        """יצירת דשבורד מקיף עם מספר תרשימים"""
        try:
            chart_files = []
            
            # תרשים עמודות לעמודות מספריות
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                # תרשים עמודות לממוצעים
                means = df[numeric_cols].mean().sort_values(ascending=False)
                if len(means) > 0:
                    bar_file = self.create_bar_chart(
                        pd.DataFrame({'Column': means.index, 'Mean': means.values}),
                        'Column', 'Mean', "ממוצעים לפי עמודות"
                    )
                    if bar_file:
                        chart_files.append(bar_file)
            
            # היסטוגרמה לעמודה מספרית ראשונה
            if len(numeric_cols) > 0:
                hist_file = self.create_histogram(df, numeric_cols[0], f"היסטוגרמה של {numeric_cols[0]}")
                if hist_file:
                    chart_files.append(hist_file)
            
            # תרשים פיזור אם יש שתי עמודות מספריות
            if len(numeric_cols) >= 2:
                scatter_file = self.create_scatter_plot(
                    df, numeric_cols[0], numeric_cols[1], 
                    f"פיזור: {numeric_cols[0]} vs {numeric_cols[1]}"
                )
                if scatter_file:
                    chart_files.append(scatter_file)
            
            # מפת קורלציה
            if 'correlation_matrix' in analysis_results:
                corr_file = self.create_correlation_heatmap(
                    analysis_results['correlation_matrix']
                )
                if corr_file:
                    chart_files.append(corr_file)
            
            # תרשים תובנות
            if 'insights' in analysis_results:
                insights_file = self.create_insights_chart(
                    analysis_results['insights']
                )
                if insights_file:
                    chart_files.append(insights_file)
            
            return chart_files
            
        except Exception as e:
            logger.error(f"Error creating comprehensive dashboard: {e}")
            return []
    
    def _save_chart(self, chart_type: str) -> str:
        """שמירת התרשים לקובץ"""
        try:
            # יצירת תיקיית temp אם לא קיימת
            temp_dir = "temp_charts"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # שם קובץ ייחודי
            self.chart_count += 1
            filename = f"{temp_dir}/{chart_type}_{self.chart_count}.png"
            
            # שמירת התרשים
            plt.savefig(filename, dpi=CHART_CONFIG['dpi'], bbox_inches='tight')
            plt.close()  # סגירת התרשים לשחרור זיכרון
            
            logger.info(f"Chart saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving chart: {e}")
            return None
    
    def cleanup_temp_files(self):
        """ניקוי קבצי התרשימים הזמניים"""
        try:
            temp_dir = "temp_charts"
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    if file.endswith('.png'):
                        os.remove(os.path.join(temp_dir, file))
                logger.info("Temporary chart files cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

# יצירת מופע גלובלי
chart_generator = ChartGenerator()

def get_chart_generator() -> ChartGenerator:
    """קבלת מופע של מחולל התרשימים"""
    return chart_generator

