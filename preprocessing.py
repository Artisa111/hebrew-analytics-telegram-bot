# -*- coding: utf-8 -*-
"""
מודול עיבוד מקדים לנתונים - Robust data preprocessing module
מספק ניקוי וטיפול מתקדם בנתונים מבולגנים כולל מטבעות, פורמטי מספרים ותאריכים
"""

import pandas as pd
import numpy as np
import re
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    עיבוד מקדים מקיף של DataFrame עם תמיכה בנתונים מבולגנים
    Comprehensive DataFrame preprocessing with support for messy data
    
    Args:
        df: Input DataFrame with potentially messy data
        
    Returns:
        pd.DataFrame: Cleaned and processed DataFrame
    """
    try:
        logger.info("Starting robust data preprocessing...")
        
        # Create a copy to avoid modifying the original
        processed_df = df.copy()
        
        # 1. Normalize column names
        processed_df = _normalize_column_names(processed_df)
        
        # 2. Process each column for numeric conversion
        for col in processed_df.columns:
            processed_df[col] = _process_column_values(processed_df[col], col)
        
        # 3. Parse obvious dates
        processed_df = _parse_dates_columns(processed_df)
        
        # 4. Basic cleaning (remove completely empty rows/columns)
        processed_df = _basic_cleanup(processed_df)
        
        logger.info(f"Preprocessing completed. Shape: {processed_df.shape}")
        return processed_df
        
    except Exception as e:
        logger.error(f"Error in preprocessing: {e}")
        return df


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """נרמול שמות עמודות - Normalize column names"""
    try:
        # Strip whitespace and replace spaces with underscores
        df.columns = df.columns.str.strip().str.replace(' ', '_', regex=False)
        
        # Remove special characters but keep Hebrew
        df.columns = df.columns.str.replace(r'[^\w\u0590-\u05FF]', '_', regex=True)
        
        # Remove multiple underscores
        df.columns = df.columns.str.replace(r'_+', '_', regex=True)
        
        # Remove leading/trailing underscores
        df.columns = df.columns.str.strip('_')
        
        return df
    except Exception as e:
        logger.warning(f"Error normalizing column names: {e}")
        return df


def _process_column_values(series: pd.Series, col_name: str) -> pd.Series:
    """עיבוד ערכים בעמודה - Process column values for numeric conversion"""
    try:
        # Skip if already numeric
        if pd.api.types.is_numeric_dtype(series):
            return series
        
        # Convert to string and process
        str_series = series.astype(str)
        
        # Check if this looks like numeric data
        if _is_likely_numeric_column(str_series):
            return _convert_to_numeric(str_series, col_name)
        
        return series
        
    except Exception as e:
        logger.warning(f"Error processing column {col_name}: {e}")
        return series


def _is_likely_numeric_column(series: pd.Series) -> bool:
    """בדיקה האם עמודה נראית מספרית - Check if column looks numeric"""
    # Sample up to 100 non-null values
    sample = series.dropna().head(100)
    if len(sample) == 0:
        return False
    
    numeric_count = 0
    for value in sample:
        if _looks_like_number(str(value)):
            numeric_count += 1
    
    # If more than 70% look like numbers, treat as numeric
    return (numeric_count / len(sample)) > 0.7


def _looks_like_number(value: str) -> bool:
    """בדיקה האם ערך נראה כמו מספר - Check if value looks like a number"""
    # Clean the value first
    cleaned = _clean_numeric_string(value)
    
    # Try to convert
    try:
        float(cleaned)
        return True
    except (ValueError, TypeError):
        return False


def _clean_numeric_string(value: str) -> str:
    """ניקוי מחרוזת מספרית - Clean numeric string"""
    if pd.isna(value) or value in ['nan', 'NaN', 'None', '']:
        return ''
    
    value = str(value).strip()
    
    # Handle parentheses as negatives: (123) -> -123
    if value.startswith('(') and value.endswith(')'):
        value = '-' + value[1:-1]
    
    # Remove currency symbols
    currency_symbols = ['₪', '$', '€', '£', '¥', '¢', '₹', '₽']
    for symbol in currency_symbols:
        value = value.replace(symbol, '')
    
    # Handle percentage
    is_percentage = False
    if '%' in value:
        is_percentage = True
        value = value.replace('%', '')
    
    # Remove plus sign
    if value.startswith('+'):
        value = value[1:]
    
    # Handle thousand separators and decimal styles
    value = _normalize_number_format(value)
    
    # Apply percentage conversion
    if is_percentage:
        try:
            num_val = float(value)
            value = str(num_val / 100)  # Convert percentage to decimal
        except ValueError:
            pass
    
    return value


def _normalize_number_format(value: str) -> str:
    """נרמול פורמט מספרים - Normalize number format"""
    # Remove any remaining non-numeric characters except . , - and whitespace
    cleaned = re.sub(r'[^\d.,-\s]', '', value)
    
    # Remove whitespace
    cleaned = cleaned.replace(' ', '')
    
    # Handle different decimal/thousand separator styles
    
    # Case 1: European style - 1.234,56 (dot for thousands, comma for decimal)
    if '.' in cleaned and ',' in cleaned:
        last_dot = cleaned.rfind('.')
        last_comma = cleaned.rfind(',')
        
        if last_comma > last_dot:
            # European style: 1.234,56
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # US style: 1,234.56
            cleaned = cleaned.replace(',', '')
    
    # Case 2: Only commas - could be thousands or decimal
    elif ',' in cleaned and '.' not in cleaned:
        # If comma is in last 3 positions, likely decimal
        comma_pos = cleaned.rfind(',')
        if len(cleaned) - comma_pos <= 3:
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
    
    # Case 3: Only dots - could be thousands or decimal
    elif '.' in cleaned and ',' not in cleaned:
        # Count dots
        dot_count = cleaned.count('.')
        if dot_count > 1:
            # Multiple dots - likely thousands separator except the last one
            parts = cleaned.split('.')
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
    
    return cleaned


def _convert_to_numeric(series: pd.Series, col_name: str) -> pd.Series:
    """המרת עמודה למספרית - Convert column to numeric"""
    try:
        # Clean all values
        cleaned_series = series.apply(_clean_numeric_string)
        
        # Convert to numeric
        numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
        
        # Log conversion stats
        converted_count = numeric_series.notna().sum()
        total_count = series.notna().sum()
        
        if converted_count > 0:
            logger.info(f"Column '{col_name}': converted {converted_count}/{total_count} values to numeric")
            return numeric_series
        else:
            logger.info(f"Column '{col_name}': no numeric values found, keeping original")
            return series
            
    except Exception as e:
        logger.warning(f"Error converting column {col_name} to numeric: {e}")
        return series


def _parse_dates_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ניתוח עמודות תאריך - Parse date columns"""
    try:
        for col in df.columns:
            if _is_likely_date_column(df[col]):
                df[col] = _convert_to_date(df[col], col)
        return df
    except Exception as e:
        logger.warning(f"Error parsing dates: {e}")
        return df


def _is_likely_date_column(series: pd.Series) -> bool:
    """בדיקה האם עמודה נראית כמו תאריכים - Check if column looks like dates"""
    if pd.api.types.is_numeric_dtype(series):
        return False
    
    # Sample non-null values
    sample = series.dropna().head(50)
    if len(sample) < 2:
        return False
    
    date_count = 0
    for value in sample:
        if _looks_like_date(str(value)):
            date_count += 1
    
    # If more than 60% look like dates, treat as date column
    return (date_count / len(sample)) > 0.6


def _looks_like_date(value: str) -> bool:
    """בדיקה האם ערך נראה כמו תאריך - Check if value looks like a date"""
    # Common date patterns
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or DD-MM-YYYY
        r'\d{2,4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD or YYYY-MM-DD
        r'\d{1,2}\.\d{1,2}\.\d{2,4}',      # DD.MM.YYYY
        r'\d{4}\d{2}\d{2}',                # YYYYMMDD
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, str(value)):
            return True
    return False


def _convert_to_date(series: pd.Series, col_name: str) -> pd.Series:
    """המרת עמודה לתאריכים - Convert column to dates"""
    try:
        # Try different parsing approaches with dayfirst heuristic
        converted_series = None
        
        # Method 1: pd.to_datetime with dayfirst=True (Israeli format)
        try:
            converted_series = pd.to_datetime(series, dayfirst=True, errors='coerce')
            if converted_series.notna().sum() > 0:
                logger.info(f"Column '{col_name}': converted to dates using dayfirst=True")
                return converted_series
        except:
            pass
        
        # Method 2: pd.to_datetime with automatic inference
        try:
            converted_series = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            if converted_series.notna().sum() > 0:
                logger.info(f"Column '{col_name}': converted to dates using automatic inference")
                return converted_series
        except:
            pass
        
        # If no conversion worked, keep original
        logger.info(f"Column '{col_name}': could not convert to dates, keeping original")
        return series
        
    except Exception as e:
        logger.warning(f"Error converting column {col_name} to date: {e}")
        return series


def _basic_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """ניקוי בסיסי - Basic cleanup"""
    try:
        # Remove completely empty rows and columns
        df = df.dropna(how='all', axis=0)  # Remove empty rows
        df = df.dropna(how='all', axis=1)  # Remove empty columns
        
        # Remove duplicate rows
        initial_rows = len(df)
        df = df.drop_duplicates()
        removed_duplicates = initial_rows - len(df)
        
        if removed_duplicates > 0:
            logger.info(f"Removed {removed_duplicates} duplicate rows")
        
        return df
    except Exception as e:
        logger.warning(f"Error in basic cleanup: {e}")
        return df


def read_csv_robust(file_path: str, **kwargs) -> pd.DataFrame:
    """
    קריאת CSV עם זיהוי אוטומטי של מפרידים
    Robust CSV reading with automatic delimiter detection
    """
    try:
        # Use pandas auto-detection for separators
        df = pd.read_csv(file_path, sep=None, engine="python", encoding='utf-8', **kwargs)
        logger.info(f"CSV file read successfully: {df.shape}")
        return df
    except UnicodeDecodeError:
        # Try different encodings
        encodings = ['cp1255', 'iso-8859-8', 'windows-1255', 'latin-1']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, sep=None, engine="python", encoding=encoding, **kwargs)
                logger.info(f"CSV file read with {encoding} encoding: {df.shape}")
                return df
            except:
                continue
        raise
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise


def read_excel_robust(file_path: str, **kwargs) -> pd.DataFrame:
    """
    קריאת Excel מחוזקת
    Robust Excel reading
    """
    try:
        df = pd.read_excel(file_path, **kwargs)
        logger.info(f"Excel file read successfully: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise