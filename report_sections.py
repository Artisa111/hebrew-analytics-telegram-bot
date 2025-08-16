# -*- coding: utf-8 -*-
"""
מודול קטעי דוח מובטחים - Guaranteed report sections module
יצירת קטעים שתמיד יופיעו בדוח, גם עם נתונים מבולגנים
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple
import logging
import os
from PIL import Image, ImageDraw, ImageFont
import io
import warnings
from i18n import t, get_chart_labels

warnings.filterwarnings('ignore')
matplotlib.use('Agg')  # Ensure headless backend

logger = logging.getLogger(__name__)

# Set up matplotlib for Hebrew support
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False


def add_guaranteed_sections(pdf_report, df: pd.DataFrame, charts_dir: str = "charts"):
    """
    הוספת קטעי דוח מובטחים
    Add guaranteed sections to the PDF report
    
    Args:
        pdf_report: HebrewPDFReport instance
        df: DataFrame with data
        charts_dir: Directory to save charts
    """
    try:
        logger.info("Adding guaranteed report sections...")
        
        # Ensure charts directory exists
        os.makedirs(charts_dir, exist_ok=True)
        
        # 1. Data Preview Section (always included)
        add_data_preview_section(pdf_report, df, charts_dir)
        
        # 2. Missing Values Analysis (always included)
        add_missing_values_section(pdf_report, df, charts_dir)
        
        # 3. Categorical Frequencies (if categorical columns exist)
        add_categorical_frequencies_section(pdf_report, df, charts_dir)
        
        # 4. Numeric Distributions (if numeric columns exist)
        add_numeric_distributions_section(pdf_report, df, charts_dir)
        
        logger.info("Guaranteed sections added successfully")
        
    except Exception as e:
        logger.error(f"Error adding guaranteed sections: {e}")


def add_data_preview_section(pdf_report, df: pd.DataFrame, charts_dir: str):
    """
    הוספת קטע תצוגה מקדימה של הנתונים
    Add data preview section with table image
    """
    try:
        logger.info("Adding data preview section...")
        
        # Add section header
        pdf_report.add_section_header(t('data_preview'), 1)
        pdf_report.add_text(t('data_preview_subtitle'), 12, indent=5)
        
        # Show data shape
        rows, cols = df.shape
        shape_text = f"{t('data_shape')}: {rows} {t('rows')}, {cols} {t('columns')}"
        pdf_report.add_text(shape_text, 11, indent=5)
        
        # Create table image from df.head()
        preview_data = df.head(10)  # Show first 10 rows
        table_image_path = create_table_image(preview_data, charts_dir, "data_preview")
        
        if table_image_path and os.path.exists(table_image_path):
            pdf_report.add_chart(table_image_path)
        else:
            # Fallback: add text representation
            pdf_report.add_text("נתוני תצוגה מקדימה:", 11, bold=True, indent=5)
            
            # Show column names
            col_text = "עמודות: " + ", ".join(df.columns[:10])
            if len(df.columns) > 10:
                col_text += f" ועוד {len(df.columns) - 10} עמודות..."
            pdf_report.add_text(col_text, 10, indent=10)
        
        logger.info("Data preview section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding data preview section: {e}")


def add_missing_values_section(pdf_report, df: pd.DataFrame, charts_dir: str):
    """
    הוספת קטע ניתוח ערכים חסרים
    Add missing values analysis section
    """
    try:
        logger.info("Adding missing values section...")
        
        # Add section header
        pdf_report.add_section_header(t('missing_values'), 1)
        pdf_report.add_text(t('missing_values_subtitle'), 12, indent=5)
        
        # Calculate missing values
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Filter columns with any missing values
        missing_data = missing_percentages[missing_percentages > 0].sort_values(ascending=False)
        
        if len(missing_data) == 0:
            # No missing values - show positive message
            pdf_report.add_text(t('no_missing_values'), 12, indent=5)
        else:
            # Create missing values chart
            chart_path = create_missing_values_chart(missing_data, charts_dir)
            
            if chart_path and os.path.exists(chart_path):
                pdf_report.add_chart(chart_path)
            else:
                # Fallback: text representation
                pdf_report.add_text("עמודות עם ערכים חסרים:", 11, bold=True, indent=5)
                for col, pct in missing_data.head(10).items():
                    pdf_report.add_text(f"• {col}: {pct:.1f}%", 10, indent=10)
        
        logger.info("Missing values section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding missing values section: {e}")


def add_categorical_frequencies_section(pdf_report, df: pd.DataFrame, charts_dir: str):
    """
    הוספת קטע התפלגות קטגוריות
    Add categorical frequencies section
    """
    try:
        logger.info("Adding categorical frequencies section...")
        
        # Find categorical columns
        categorical_cols = get_categorical_columns(df)
        
        if not categorical_cols:
            logger.info("No categorical columns found, skipping categorical section")
            return
        
        # Add section header
        pdf_report.add_section_header(t('categorical_distributions'), 1)
        pdf_report.add_text(t('categorical_distributions_subtitle'), 12, indent=5)
        
        # Process each categorical column (limit to top 5 columns)
        for i, col in enumerate(categorical_cols[:5]):
            try:
                # Get top values
                value_counts = df[col].value_counts().head(10)
                
                if len(value_counts) > 0:
                    # Create chart for this column
                    chart_path = create_categorical_chart(col, value_counts, charts_dir, f"categorical_{i}")
                    
                    if chart_path and os.path.exists(chart_path):
                        pdf_report.add_chart(chart_path)
                    else:
                        # Fallback: text representation
                        pdf_report.add_text(f"עמודה: {col}", 11, bold=True, indent=5)
                        for value, count in value_counts.head(5).items():
                            pdf_report.add_text(f"• {value}: {count}", 10, indent=10)
                            
            except Exception as e:
                logger.warning(f"Error processing categorical column {col}: {e}")
                continue
        
        logger.info("Categorical frequencies section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding categorical frequencies section: {e}")


def add_numeric_distributions_section(pdf_report, df: pd.DataFrame, charts_dir: str):
    """
    הוספת קטע התפלגות מספרית
    Add numeric distributions section
    """
    try:
        logger.info("Adding numeric distributions section...")
        
        # Find numeric columns
        numeric_cols = get_numeric_columns(df)
        
        if not numeric_cols:
            logger.info("No numeric columns found, skipping numeric section")
            return
        
        # Add section header
        pdf_report.add_section_header(t('numeric_distributions'), 1)
        pdf_report.add_text(t('numeric_distributions_subtitle'), 12, indent=5)
        
        # Process each numeric column (limit to top 5 columns)
        for i, col in enumerate(numeric_cols[:5]):
            try:
                # Skip if column has no valid data
                valid_data = df[col].dropna()
                if len(valid_data) == 0:
                    continue
                
                # Create histogram and boxplot
                chart_path = create_numeric_distribution_chart(col, valid_data, charts_dir, f"numeric_{i}")
                
                if chart_path and os.path.exists(chart_path):
                    pdf_report.add_chart(chart_path)
                else:
                    # Fallback: basic statistics
                    pdf_report.add_text(f"עמודה: {col}", 11, bold=True, indent=5)
                    stats = valid_data.describe()
                    pdf_report.add_text(f"• {t('mean')}: {stats['mean']:.2f}", 10, indent=10)
                    pdf_report.add_text(f"• {t('median')}: {stats['50%']:.2f}", 10, indent=10)
                    pdf_report.add_text(f"• {t('min')}: {stats['min']:.2f}", 10, indent=10)
                    pdf_report.add_text(f"• {t('max')}: {stats['max']:.2f}", 10, indent=10)
                    
            except Exception as e:
                logger.warning(f"Error processing numeric column {col}: {e}")
                continue
        
        logger.info("Numeric distributions section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding numeric distributions section: {e}")


def add_statistical_summary_section(pdf_report, df: pd.DataFrame, output_dir: str = "charts"):
    """
    הוספת קטע סיכום סטטיסטי
    Add statistical summary section
    """
    try:
        logger.info("Adding statistical summary section...")
        
        # Find numeric columns
        numeric_cols = get_numeric_columns(df)
        
        if not numeric_cols:
            logger.info("No numeric columns for statistical summary")
            return
        
        # Add section header
        pdf_report.add_section_header(t('statistical_summary'), 1)
        pdf_report.add_text(t('statistical_summary_subtitle'), 12, indent=5)
        
        # Get descriptive statistics
        stats_df = df[numeric_cols].describe()
        
        # Create statistics table image
        table_image_path = create_statistics_table_image(stats_df, output_dir, "statistical_summary")
        
        if table_image_path and os.path.exists(table_image_path):
            pdf_report.add_chart(table_image_path)
        else:
            # Fallback: text representation
            for col in numeric_cols[:10]:  # Limit to prevent overflow
                try:
                    col_stats = df[col].describe()
                    pdf_report.add_text(f"עמודה: {col}", 11, bold=True, indent=5)
                    pdf_report.add_text(f"• {t('count_stat')}: {int(col_stats['count'])}", 10, indent=10)
                    pdf_report.add_text(f"• {t('mean')}: {col_stats['mean']:.3f}", 10, indent=10)
                    pdf_report.add_text(f"• {t('std')}: {col_stats['std']:.3f}", 10, indent=10)
                    pdf_report.add_text(f"• {t('min')}: {col_stats['min']:.3f}", 10, indent=10)
                    pdf_report.add_text(f"• {t('max')}: {col_stats['max']:.3f}", 10, indent=10)
                except Exception as e:
                    logger.warning(f"Error processing column {col}: {e}")
                    continue
        
        logger.info("Statistical summary section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding statistical summary section: {e}")


def get_categorical_columns(df: pd.DataFrame, max_unique_values: int = 20) -> List[str]:
    """
    זיהוי עמודות קטגוריות
    Identify categorical columns
    """
    categorical_cols = []
    
    for col in df.columns:
        try:
            # Check if column is object/string type or has low cardinality
            if (df[col].dtype == 'object' or 
                df[col].dtype.name == 'category' or 
                (df[col].nunique() <= max_unique_values and not pd.api.types.is_numeric_dtype(df[col]))):
                
                # Skip if too many nulls
                if df[col].isnull().sum() / len(df) < 0.8:
                    categorical_cols.append(col)
                    
        except Exception as e:
            logger.warning(f"Error checking column {col}: {e}")
            
    return categorical_cols


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    זיהוי עמודות מספריות
    Identify numeric columns
    """
    numeric_cols = []
    
    for col in df.columns:
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Skip if too many nulls
                if df[col].isnull().sum() / len(df) < 0.9:
                    numeric_cols.append(col)
                    
        except Exception as e:
            logger.warning(f"Error checking numeric column {col}: {e}")
            
    return numeric_cols


def create_table_image(df: pd.DataFrame, output_dir: str, filename: str) -> Optional[str]:
    """
    יצירת תמונה של טבלה
    Create table image from DataFrame
    """
    try:
        # Limit data size for image
        display_df = df.head(10).copy()
        
        # Limit column width
        for col in display_df.columns:
            display_df[col] = display_df[col].astype(str).str[:30]
        
        # Create matplotlib table
        fig, ax = plt.subplots(figsize=(12, min(8, len(display_df) * 0.5 + 2)))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table
        table = ax.table(cellText=display_df.values,
                        colLabels=display_df.columns,
                        cellLoc='center',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.5)
        
        # Style the table
        for i in range(len(display_df.columns)):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        output_path = os.path.join(output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating table image: {e}")
        return None


def create_missing_values_chart(missing_data: pd.Series, output_dir: str) -> Optional[str]:
    """
    יצירת תרשים ערכים חסרים
    Create missing values chart
    """
    try:
        if len(missing_data) == 0:
            return None
            
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        bars = plt.bar(range(len(missing_data)), missing_data.values, 
                      color='#ff7f7f', alpha=0.7)
        
        # Customize chart
        labels = get_chart_labels('missing_values')
        plt.title(labels['title'], fontsize=14, fontweight='bold')
        plt.xlabel(labels['xlabel'], fontsize=12)
        plt.ylabel(labels['ylabel'], fontsize=12)
        
        # Set x-axis labels
        plt.xticks(range(len(missing_data)), 
                  [col[:20] + '...' if len(col) > 20 else col for col in missing_data.index], 
                  rotation=45, ha='right')
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, missing_data.values)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, "missing_values.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating missing values chart: {e}")
        return None


def create_categorical_chart(column_name: str, value_counts: pd.Series, 
                           output_dir: str, filename: str) -> Optional[str]:
    """
    יצירת תרשים קטגוריה
    Create categorical chart
    """
    try:
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        bars = plt.bar(range(len(value_counts)), value_counts.values,
                      color='#4CAF50', alpha=0.7)
        
        # Customize chart
        plt.title(f"{t('categorical_distributions')}: {column_name}", 
                 fontsize=14, fontweight='bold')
        plt.xlabel(t('value'), fontsize=12)
        plt.ylabel(t('count'), fontsize=12)
        
        # Set x-axis labels
        labels = [str(val)[:15] + '...' if len(str(val)) > 15 else str(val) 
                 for val in value_counts.index]
        plt.xticks(range(len(value_counts)), labels, rotation=45, ha='right')
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, value_counts.values)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(value_counts) * 0.01, 
                    str(value), ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating categorical chart: {e}")
        return None


def create_numeric_distribution_chart(column_name: str, data: pd.Series, 
                                    output_dir: str, filename: str) -> Optional[str]:
    """
    יצירת תרשים התפלגות מספרית
    Create numeric distribution chart (histogram + boxplot)
    """
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Histogram
        ax1.hist(data, bins=min(30, int(len(data)/10)), alpha=0.7, color='#2196F3', edgecolor='black')
        ax1.set_title(f"{t('histogram')}: {column_name}", fontweight='bold')
        ax1.set_xlabel(t('value'))
        ax1.set_ylabel(t('frequency'))
        ax1.grid(True, alpha=0.3)
        
        # Boxplot
        ax2.boxplot(data, vert=False, patch_artist=True, 
                   boxprops=dict(facecolor='#FF9800', alpha=0.7))
        ax2.set_title(f"{t('boxplot')}: {column_name}", fontweight='bold')
        ax2.set_xlabel(t('value'))
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating numeric distribution chart: {e}")
        return None


def create_statistics_table_image(stats_df: pd.DataFrame, output_dir: str, filename: str) -> Optional[str]:
    """
    יצירת תמונה של טבלת סטטיסטיקות
    Create statistics table image
    """
    try:
        # Round values for display
        display_stats = stats_df.round(3)
        
        # Limit columns to prevent overflow
        if len(display_stats.columns) > 8:
            display_stats = display_stats.iloc[:, :8]
        
        # Create matplotlib table
        fig, ax = plt.subplots(figsize=(min(14, len(display_stats.columns) * 1.5), 
                                       min(10, len(display_stats.index) * 0.8 + 2)))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table
        table = ax.table(cellText=display_stats.values,
                        rowLabels=display_stats.index,
                        colLabels=display_stats.columns,
                        cellLoc='center',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        
        # Style the table
        for i in range(len(display_stats.columns)):
            table[(0, i)].set_facecolor('#2196F3')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(len(display_stats.index)):
            table[(i+1, -1)].set_facecolor('#E3F2FD')
            table[(i+1, -1)].set_text_props(weight='bold')
        
        plt.title(t('statistical_summary'), fontsize=16, fontweight='bold', pad=20)
        
        output_path = os.path.join(output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating statistics table image: {e}")
        return None