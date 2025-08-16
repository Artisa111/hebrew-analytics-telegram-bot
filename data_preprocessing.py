# -*- coding: utf-8 -*-
"""
Robust data preprocessing module for messy CSV/Excel data
"""

import pandas as pd
import numpy as np
import re
from typing import Any, Union
import logging
from dateutil import parser
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Robust data preprocessing that ensures data is always usable for analysis
    
    Handles:
    - Column name cleaning
    - Number-like strings with currency symbols, percentages, parentheses 
    - Thousand separators and decimal variations
    - Date parsing with dayfirst heuristic
    
    Args:
        df: Input DataFrame (potentially messy)
        
    Returns:
        Cleaned DataFrame ready for analysis
    """
    try:
        logger.info("Starting robust data preprocessing")
        df_processed = df.copy()
        
        # 1. Clean column names
        df_processed = _clean_column_names(df_processed)
        
        # 2. Process each column for data type conversion
        for col in df_processed.columns:
            df_processed[col] = _process_column(df_processed[col])
        
        logger.info(f"Data preprocessing completed. Shape: {df_processed.shape}")
        return df_processed
        
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}")
        # Return original DataFrame if preprocessing fails
        return df


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize column names"""
    try:
        # Remove extra whitespace and normalize
        df.columns = df.columns.astype(str).str.strip()
        
        # Replace problematic characters
        df.columns = df.columns.str.replace(r'[^\w\s\u0590-\u05FF]', '_', regex=True)
        df.columns = df.columns.str.replace(r'\s+', '_', regex=True)
        
        # Ensure no duplicate column names
        cols = df.columns.tolist()
        seen = {}
        for i, col in enumerate(cols):
            if col in seen:
                seen[col] += 1
                cols[i] = f"{col}_{seen[col]}"
            else:
                seen[col] = 0
        
        df.columns = cols
        logger.info("Column names cleaned successfully")
        return df
        
    except Exception as e:
        logger.warning(f"Error cleaning column names: {e}")
        return df


def _process_column(series: pd.Series) -> pd.Series:
    """
    Process a single column to detect and convert appropriate data types
    """
    try:
        # Skip if all NaN
        if series.isna().all():
            return series
        
        # Try to convert to numeric first
        numeric_series = _try_convert_to_numeric(series)
        if numeric_series is not None:
            return numeric_series
        
        # Try to convert to datetime
        datetime_series = _try_convert_to_datetime(series)
        if datetime_series is not None:
            return datetime_series
        
        # Keep as string but clean it
        return _clean_string_column(series)
        
    except Exception as e:
        logger.debug(f"Error processing column {series.name}: {e}")
        return series


def _try_convert_to_numeric(series: pd.Series) -> Union[pd.Series, None]:
    """
    Try to convert series to numeric, handling various formats
    """
    try:
        # First try pandas default conversion
        numeric = pd.to_numeric(series, errors='coerce')
        if not numeric.isna().all():
            # If some values converted successfully, check if worth keeping
            conversion_rate = (~numeric.isna()).sum() / len(series)
            if conversion_rate > 0.5:  # More than 50% convertible
                return numeric
        
        # Try custom numeric conversion for messy formats
        cleaned_series = series.astype(str).apply(_clean_numeric_string)
        numeric = pd.to_numeric(cleaned_series, errors='coerce')
        
        # Check conversion success rate
        conversion_rate = (~numeric.isna()).sum() / len(series)
        if conversion_rate > 0.3:  # At least 30% convertible for messy data
            logger.info(f"Converted column '{series.name}' to numeric (success rate: {conversion_rate:.1%})")
            return numeric
        
        return None
        
    except Exception as e:
        logger.debug(f"Numeric conversion failed for column {series.name}: {e}")
        return None


def _clean_numeric_string(value: Any) -> str:
    """
    Clean a single value to extract numeric content
    """
    if pd.isna(value):
        return ""
    
    value_str = str(value).strip()
    
    # Handle empty or whitespace
    if not value_str or value_str.isspace():
        return ""
    
    # Currency symbols to remove
    currency_symbols = ['₪', '$', '€', '£', '¥', '¢', '₹', '₽', '₩', '₡', '₨']
    
    # Remove currency symbols
    for symbol in currency_symbols:
        value_str = value_str.replace(symbol, '')
    
    # Handle percentage
    is_percentage = '%' in value_str
    value_str = value_str.replace('%', '')
    
    # Handle parentheses as negative (accounting format)
    is_negative = False
    if value_str.startswith('(') and value_str.endswith(')'):
        is_negative = True
        value_str = value_str[1:-1]
    
    # Handle explicit positive sign
    value_str = value_str.replace('+', '')
    
    # Remove common thousand separators but preserve decimals
    # Handle different decimal conventions
    if ',' in value_str and '.' in value_str:
        # Both comma and dot - determine which is decimal
        last_comma = value_str.rfind(',')
        last_dot = value_str.rfind('.')
        
        if last_dot > last_comma:
            # Dot is decimal separator
            value_str = value_str.replace(',', '')
        else:
            # Comma is decimal separator
            value_str = value_str.replace('.', '').replace(',', '.')
    elif ',' in value_str:
        # Only comma - could be thousands or decimal
        comma_pos = value_str.rfind(',')
        digits_after_comma = len(value_str) - comma_pos - 1
        
        if digits_after_comma <= 2:
            # Likely decimal separator
            value_str = value_str.replace(',', '.')
        else:
            # Likely thousands separator
            value_str = value_str.replace(',', '')
    
    # Remove spaces (thousand separators in some locales)
    value_str = re.sub(r'\s+', '', value_str)
    
    # Extract numeric part using regex
    numeric_pattern = r'^-?(\d+\.?\d*)$'
    match = re.match(numeric_pattern, value_str)
    
    if match:
        numeric_value = match.group(1)
        
        # Apply negative if parentheses were used
        if is_negative:
            numeric_value = '-' + numeric_value
        
        # Apply percentage conversion
        if is_percentage:
            try:
                numeric_value = str(float(numeric_value) / 100)
            except ValueError:
                pass
        
        return numeric_value
    
    return ""


def _try_convert_to_datetime(series: pd.Series) -> Union[pd.Series, None]:
    """
    Try to convert series to datetime with dayfirst heuristic
    """
    try:
        # Skip if obviously not dates
        sample_values = series.dropna().astype(str).head(10)
        if sample_values.empty:
            return None
        
        # Check if values look like dates
        date_indicators = ['-', '/', '.', ':', ' ']
        has_date_chars = any(any(char in str(val) for char in date_indicators) for val in sample_values)
        
        if not has_date_chars:
            return None
        
        # Try pandas datetime conversion with dayfirst
        datetime_series = pd.to_datetime(series, errors='coerce', dayfirst=True, infer_datetime_format=True)
        
        # Check conversion success rate
        conversion_rate = (~datetime_series.isna()).sum() / len(series)
        if conversion_rate > 0.5:  # More than 50% convertible
            logger.info(f"Converted column '{series.name}' to datetime (success rate: {conversion_rate:.1%})")
            return datetime_series
        
        return None
        
    except Exception as e:
        logger.debug(f"Datetime conversion failed for column {series.name}: {e}")
        return None


def _clean_string_column(series: pd.Series) -> pd.Series:
    """
    Clean string column by removing excess whitespace
    """
    try:
        return series.astype(str).str.strip()
    except Exception as e:
        logger.debug(f"String cleaning failed for column {series.name}: {e}")
        return series


def load_csv_robust(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Robust CSV loading with automatic delimiter detection
    
    Args:
        file_path: Path to CSV file
        **kwargs: Additional arguments for pandas.read_csv
        
    Returns:
        DataFrame with loaded data
    """
    try:
        logger.info(f"Loading CSV file: {file_path}")
        
        # Use sep=None with python engine for auto-detection
        kwargs.setdefault('sep', None)
        kwargs.setdefault('engine', 'python')
        kwargs.setdefault('encoding', 'utf-8')
        
        # Try loading with auto-detection
        try:
            df = pd.read_csv(file_path, **kwargs)
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin1', 'iso-8859-1', 'cp1252']:
                try:
                    kwargs['encoding'] = encoding
                    df = pd.read_csv(file_path, **kwargs)
                    logger.info(f"Successfully loaded with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not determine file encoding")
        
        logger.info(f"CSV loaded successfully. Shape: {df.shape}")
        
        # Apply robust preprocessing
        return preprocess_df(df)
        
    except Exception as e:
        logger.error(f"Error loading CSV file {file_path}: {e}")
        raise