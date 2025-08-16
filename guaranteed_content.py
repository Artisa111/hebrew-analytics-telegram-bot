# -*- coding: utf-8 -*-
"""
Guaranteed content sections for PDF reports - ensures reports are never empty
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, List, Any, Optional
import logging
from config import t

logger = logging.getLogger(__name__)

# Configure matplotlib for Hebrew
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False


def add_guaranteed_sections(pdf_report, df: pd.DataFrame, charts_dir: str = "charts") -> None:
    """
    Add guaranteed content sections that ensure the report is never empty
    
    Args:
        pdf_report: HebrewPDFReport instance
        df: DataFrame to analyze
        charts_dir: Directory to save chart images
    """
    try:
        logger.info("Adding guaranteed content sections to PDF report")
        
        # Ensure charts directory exists
        os.makedirs(charts_dir, exist_ok=True)
        
        # 1. Data Preview Section
        add_data_preview_section(pdf_report, df, charts_dir)
        
        # 2. Missing Values Section
        add_missing_values_section(pdf_report, df, charts_dir)
        
        # 3. Categorical Frequencies Section
        add_categorical_frequencies_section(pdf_report, df, charts_dir)
        
        # 4. Numeric Distributions Section
        add_numeric_distributions_section(pdf_report, df, charts_dir)
        
        logger.info("All guaranteed sections added successfully")
        
    except Exception as e:
        logger.error(f"Error adding guaranteed sections: {e}")


def add_data_preview_section(pdf_report, df: pd.DataFrame, charts_dir: str) -> None:
    """
    Add data preview section with df.head() as a table image
    """
    try:
        pdf_report.add_section_header(t("data_preview"), 1)
        
        # Create preview data (first 5 rows)
        preview_df = df.head()
        
        # Create table visualization
        fig, ax = plt.subplots(figsize=(12, max(3, len(preview_df) * 0.5)))
        ax.axis('tight')
        ax.axis('off')
        
        # Create table
        table_data = []
        # Add headers
        headers = [str(col)[:20] for col in preview_df.columns]  # Truncate long headers
        table_data.append(headers)
        
        # Add data rows
        for _, row in preview_df.iterrows():
            row_data = []
            for val in row:
                if pd.isna(val):
                    row_data.append('NaN')
                else:
                    # Truncate long values and format
                    str_val = str(val)
                    if len(str_val) > 15:
                        str_val = str_val[:12] + '...'
                    row_data.append(str_val)
            table_data.append(row_data)
        
        # Create the table
        table = ax.table(cellText=table_data[1:], 
                        colLabels=table_data[0],
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        
        # Color header
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.title(f'{t("data_preview")} - {len(df)} רשומות, {len(df.columns)} עמודות', 
                 fontsize=12, fontweight='bold', pad=20)
        
        # Save chart
        chart_path = os.path.join(charts_dir, 'data_preview.png')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Add to PDF
        pdf_report.add_chart(chart_path)
        
        logger.info("Data preview section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding data preview section: {e}")


def add_missing_values_section(pdf_report, df: pd.DataFrame, charts_dir: str) -> None:
    """
    Add missing values analysis section
    """
    try:
        pdf_report.add_section_header(t("missing_values"), 1)
        
        # Calculate missing values
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Filter columns with missing values
        missing_data = missing_percentages[missing_percentages > 0].sort_values(ascending=False)
        
        if missing_data.empty:
            # No missing values
            pdf_report.add_text(f"✅ {t('no_missing_values')}", 12, bold=True)
        else:
            # Create bar chart of missing values
            fig, ax = plt.subplots(figsize=(10, max(4, len(missing_data) * 0.4)))
            
            bars = ax.barh(range(len(missing_data)), missing_data.values, 
                          color='lightcoral', alpha=0.7)
            
            # Add percentage labels
            for i, (col, pct) in enumerate(missing_data.items()):
                ax.text(pct + max(missing_data) * 0.01, i, 
                       f'{pct:.1f}%', va='center', fontweight='bold')
            
            ax.set_yticks(range(len(missing_data)))
            ax.set_yticklabels([col[:25] for col in missing_data.index])
            ax.set_xlabel('אחוז ערכים חסרים (%)')
            ax.set_title('ערכים חסרים לפי עמודה', fontweight='bold', fontsize=12)
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(charts_dir, 'missing_values.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            # Add to PDF
            pdf_report.add_chart(chart_path)
            
            # Add summary text
            total_missing = missing_counts.sum()
            total_cells = len(df) * len(df.columns)
            overall_pct = (total_missing / total_cells) * 100
            
            pdf_report.add_text(f"סיכום: {total_missing:,} ערכים חסרים מתוך {total_cells:,} ({overall_pct:.1f}%)", 
                               11, bold=True)
        
        logger.info("Missing values section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding missing values section: {e}")


def add_categorical_frequencies_section(pdf_report, df: pd.DataFrame, charts_dir: str) -> None:
    """
    Add categorical frequencies section with bar charts
    """
    try:
        # Find categorical/low-cardinality columns
        categorical_cols = []
        
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                unique_count = df[col].nunique()
                if 2 <= unique_count <= 20:  # Reasonable range for categorical
                    categorical_cols.append(col)
        
        if not categorical_cols:
            # Look for numeric columns with low cardinality
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    unique_count = df[col].nunique()
                    if 2 <= unique_count <= 15:
                        categorical_cols.append(col)
        
        if categorical_cols:
            pdf_report.add_section_header(t("categorical_frequencies"), 1)
            
            # Create charts for top categorical columns (max 4)
            for col in categorical_cols[:4]:
                try:
                    value_counts = df[col].value_counts().head(10)  # Top 10 values
                    
                    if len(value_counts) > 1:
                        fig, ax = plt.subplots(figsize=(10, max(4, len(value_counts) * 0.4)))
                        
                        bars = ax.barh(range(len(value_counts)), value_counts.values,
                                      color='skyblue', alpha=0.7)
                        
                        # Add count labels
                        for i, count in enumerate(value_counts.values):
                            ax.text(count + max(value_counts) * 0.01, i,
                                   f'{count:,}', va='center', fontweight='bold')
                        
                        ax.set_yticks(range(len(value_counts)))
                        labels = [str(label)[:30] for label in value_counts.index]  # Truncate long labels
                        ax.set_yticklabels(labels)
                        ax.set_xlabel('תדירות')
                        ax.set_title(f'תדירויות - {col}', fontweight='bold', fontsize=12)
                        ax.grid(axis='x', alpha=0.3)
                        
                        plt.tight_layout()
                        
                        # Save chart
                        chart_path = os.path.join(charts_dir, f'categorical_freq_{col[:20]}.png')
                        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                        plt.close()
                        
                        # Add to PDF
                        pdf_report.add_chart(chart_path)
                        
                except Exception as e:
                    logger.warning(f"Error creating chart for column {col}: {e}")
                    continue
        
        logger.info(f"Categorical frequencies section added for {len(categorical_cols)} columns")
        
    except Exception as e:
        logger.error(f"Error adding categorical frequencies section: {e}")


def add_numeric_distributions_section(pdf_report, df: pd.DataFrame, charts_dir: str) -> None:
    """
    Add numeric distributions section with histograms and boxplots
    """
    try:
        # Find numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            pdf_report.add_section_header(t("numeric_distributions"), 1)
            
            # Create distributions for top numeric columns (max 4)
            for col in numeric_cols[:4]:
                try:
                    # Skip if all NaN
                    if df[col].isna().all():
                        continue
                    
                    # Create subplot with histogram and boxplot
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                    
                    # Histogram
                    df[col].dropna().hist(bins=30, ax=ax1, color='lightgreen', alpha=0.7, edgecolor='black')
                    ax1.set_title(f'התפלגות - {col}', fontweight='bold')
                    ax1.set_ylabel('תדירות')
                    ax1.grid(alpha=0.3)
                    
                    # Add statistics text
                    stats = df[col].describe()
                    stats_text = f'ממוצע: {stats["mean"]:.2f}\nחציון: {stats["50%"]:.2f}\nסטיית תקן: {stats["std"]:.2f}'
                    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    
                    # Boxplot
                    df[col].dropna().plot(kind='box', ax=ax2, vert=False, patch_artist=True,
                                         boxprops=dict(facecolor='lightblue', alpha=0.7))
                    ax2.set_xlabel(col)
                    ax2.set_title(f'תרשים קופסה - {col}', fontweight='bold')
                    ax2.grid(alpha=0.3)
                    
                    plt.tight_layout()
                    
                    # Save chart
                    chart_path = os.path.join(charts_dir, f'numeric_dist_{col[:20]}.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()
                    
                    # Add to PDF
                    pdf_report.add_chart(chart_path)
                    
                except Exception as e:
                    logger.warning(f"Error creating distribution chart for column {col}: {e}")
                    continue
        
        logger.info(f"Numeric distributions section added for {len(numeric_cols)} columns")
        
    except Exception as e:
        logger.error(f"Error adding numeric distributions section: {e}")


def add_statistical_summary_section(pdf_report, df: pd.DataFrame, charts_dir: str = "charts") -> None:
    """
    Add statistical summary section with describe() table at the end
    """
    try:
        pdf_report.add_section_header(t("statistical_summary"), 1)
        
        # Get numeric columns only
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            pdf_report.add_text("אין עמודות מספריות לסיכום סטטיסטי", 12, bold=True)
            return
        
        # Create statistical summary
        summary = numeric_df.describe()
        
        # Create table visualization
        fig, ax = plt.subplots(figsize=(14, max(4, len(summary.columns) * 0.3)))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        table_data = []
        
        # Row headers (statistics)
        row_labels = ['Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']
        hebrew_labels = ['כמות', 'ממוצע', 'סטיית תקן', 'מינימום', 'רבעון ראשון', 'חציון', 'רבעון שלישי', 'מקסימום']
        
        # Add data
        for i, stat in enumerate(summary.index):
            row = [hebrew_labels[i]]
            for col in summary.columns:
                val = summary.loc[stat, col]
                if pd.isna(val):
                    row.append('N/A')
                else:
                    # Format numbers appropriately
                    if stat == 'count':
                        row.append(f'{int(val):,}')
                    else:
                        row.append(f'{val:.2f}')
            table_data.append(row)
        
        # Column headers
        col_headers = ['סטטיסטיקה'] + [str(col)[:15] for col in summary.columns]
        
        # Create table
        table = ax.table(cellText=table_data,
                        colLabels=col_headers,
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        # Color header and first column
        for j in range(len(col_headers)):
            table[(0, j)].set_facecolor('#40466e')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        for i in range(1, len(table_data) + 1):
            table[(i, 0)].set_facecolor('#f0f0f0')
            table[(i, 0)].set_text_props(weight='bold')
        
        plt.title('סיכום סטטיסטי של עמודות מספריות', fontsize=14, fontweight='bold', pad=20)
        
        # Save chart
        chart_path = os.path.join(charts_dir, 'statistical_summary.png')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Add to PDF
        pdf_report.add_chart(chart_path)
        
        logger.info("Statistical summary section added successfully")
        
    except Exception as e:
        logger.error(f"Error adding statistical summary section: {e}")