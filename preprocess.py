# -*- coding: utf-8 -*-
"""
Robust preprocessing utilities for messy data inputs
Handles currencies, dates, mixed formats with safe fallbacks
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Optional, Union, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_column_name(name: str) -> str:
    """Normalize column names to be consistent and safe"""
    if not isinstance(name, str):
        name = str(name)
    
    # Remove extra whitespace
    name = name.strip()
    
    # Replace problematic characters
    name = re.sub(r'[^\w\s\u0590-\u05FF]', '_', name)  # Keep Hebrew, ASCII, underscore
    name = re.sub(r'\s+', '_', name)  # Replace spaces with underscore
    name = re.sub(r'_+', '_', name)  # Replace multiple underscores with single
    name = name.strip('_')  # Remove leading/trailing underscores
    
    # Ensure not empty
    if not name:
        name = "column"
    
    return name


def coerce_numeric(series: pd.Series) -> pd.Series:
    """
    Handle currencies, percentages, mixed decimal formats, thousands separators
    Examples: ₪1,234.56, $1 234, €12,5, (1,000), 50%, +1.5
    """
    if not isinstance(series, pd.Series):
        return series
    
    # If already numeric, return as-is
    if pd.api.types.is_numeric_dtype(series):
        return series
    
    logger.debug(f"Converting column '{series.name}' to numeric")
    
    # Create a copy to work with
    clean_series = series.copy()
    
    # Convert to string and handle NaN
    clean_series = clean_series.astype(str)
    clean_series = clean_series.replace(['nan', 'NaN', 'None', 'null', ''], np.nan)
    
    def clean_numeric_value(val):
        if pd.isna(val) or val == 'nan':
            return np.nan
            
        val_str = str(val).strip()
        if not val_str:
            return np.nan
            
        # Handle percentage - extract number and convert
        if '%' in val_str:
            percent_match = re.search(r'([-+]?\d*\.?\d+)', val_str)
            if percent_match:
                return float(percent_match.group(1)) / 100
        
        # Handle parentheses as negative
        is_negative = '(' in val_str and ')' in val_str
        
        # Remove currency symbols, spaces, and other non-numeric chars except decimal separators
        # Keep: digits, +/-, decimal points and commas (for now)
        cleaned = re.sub(r'[^\d\.,+-]', '', val_str)
        
        if not cleaned:
            return np.nan
            
        # Handle different decimal separator formats
        # Format like "1,234.56" (US format)
        if ',' in cleaned and '.' in cleaned:
            # If comma comes before dot, treat comma as thousands separator
            if cleaned.find(',') < cleaned.find('.'):
                cleaned = cleaned.replace(',', '')
            # If dot comes before comma, treat dot as thousands separator (European)
            else:
                cleaned = cleaned.replace('.', '').replace(',', '.')
        
        # Format like "1,234" or "12,5" (need to determine if comma is thousands or decimal)
        elif ',' in cleaned:
            comma_parts = cleaned.split(',')
            # If last part after comma is 3 digits, likely thousands separator
            if len(comma_parts) == 2 and len(comma_parts[1]) == 3:
                cleaned = cleaned.replace(',', '')
            # If last part is 1-2 digits, likely decimal separator
            elif len(comma_parts) == 2 and len(comma_parts[1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            # Multiple commas, treat as thousands separators
            else:
                cleaned = cleaned.replace(',', '')
        
        # Handle multiple dots (treat as thousands separator except last one)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
        
        # Handle + sign
        cleaned = cleaned.lstrip('+')
        
        try:
            result = float(cleaned)
            return -result if is_negative else result
        except (ValueError, TypeError):
            logger.debug(f"Could not convert '{val_str}' to numeric")
            return np.nan
    
    # Apply the cleaning function
    numeric_series = clean_series.apply(clean_numeric_value)
    
    # If most values converted successfully, return numeric series
    non_null_count = numeric_series.notna().sum()
    original_non_null = series.notna().sum()
    
    if original_non_null > 0:
        conversion_rate = non_null_count / original_non_null
        if conversion_rate >= 0.5:  # If at least 50% converted successfully
            logger.debug(f"Successfully converted {conversion_rate:.1%} of values to numeric")
            return numeric_series
    
    # Otherwise return original series
    logger.debug(f"Conversion rate too low ({non_null_count}/{original_non_null}), keeping original")
    return series


def detect_and_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect and parse date columns with dayfirst heuristic
    Preserves original column on failure
    """
    df_result = df.copy()
    
    for col in df.columns:
        if df[col].dtype == 'object':  # Only try on string columns
            # Sample a few values to check if they might be dates
            sample_values = df[col].dropna().head(10)
            if len(sample_values) == 0:
                continue
                
            date_indicators = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
                r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD
                r'\d{1,2}\.\d{1,2}\.\d{2,4}',      # DD.MM.YYYY
                r'\d{4}\.\d{1,2}\.\d{1,2}',        # YYYY.MM.DD
            ]
            
            # Check if any sample values match date patterns
            might_be_dates = 0
            for val in sample_values:
                val_str = str(val).strip()
                for pattern in date_indicators:
                    if re.search(pattern, val_str):
                        might_be_dates += 1
                        break
            
            # If more than 30% of samples look like dates, try conversion
            if might_be_dates / len(sample_values) > 0.3:
                logger.debug(f"Attempting date conversion for column '{col}'")
                
                try:
                    # Try dayfirst=True first (common in many regions)
                    parsed_dates = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
                    
                    # Check conversion success rate
                    non_null_original = df[col].notna().sum()
                    non_null_parsed = parsed_dates.notna().sum()
                    
                    if non_null_original > 0:
                        success_rate = non_null_parsed / non_null_original
                        
                        if success_rate >= 0.6:  # At least 60% successfully parsed
                            df_result[col] = parsed_dates
                            logger.info(f"Successfully converted column '{col}' to datetime ({success_rate:.1%} success)")
                        else:
                            logger.debug(f"Date conversion for '{col}' had low success rate ({success_rate:.1%})")
                            
                except Exception as e:
                    logger.debug(f"Date parsing failed for column '{col}': {e}")
    
    return df_result


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply comprehensive preprocessing to DataFrame
    Logs all actions taken
    """
    if df is None or df.empty:
        logger.warning("Empty or None DataFrame provided to preprocess_df")
        return df
        
    logger.info(f"Starting preprocessing of DataFrame with shape {df.shape}")
    
    # Create copy to avoid modifying original
    result_df = df.copy()
    
    # 1. Normalize column names
    logger.debug("Normalizing column names")
    original_columns = result_df.columns.tolist()
    result_df.columns = [normalize_column_name(col) for col in result_df.columns]
    
    # Log column name changes
    for orig, new in zip(original_columns, result_df.columns):
        if orig != new:
            logger.debug(f"Renamed column: '{orig}' -> '{new}'")
    
    # 2. Detect and parse dates
    logger.debug("Detecting and parsing date columns")
    result_df = detect_and_parse_dates(result_df)
    
    # 3. Coerce numeric columns
    logger.debug("Attempting numeric coercion on object columns")
    for col in result_df.columns:
        if result_df[col].dtype == 'object':
            # Only try numeric conversion if it looks promising
            sample_vals = result_df[col].dropna().head(20)
            if len(sample_vals) > 0:
                numeric_looking = 0
                for val in sample_vals:
                    val_str = str(val).strip()
                    # Check for numeric indicators
                    if re.search(r'[\d₪$€£¥%,.\-+()]', val_str):
                        numeric_looking += 1
                
                # If more than 40% look numeric, try conversion
                if numeric_looking / len(sample_vals) > 0.4:
                    original_dtype = result_df[col].dtype
                    result_df[col] = coerce_numeric(result_df[col])
                    
                    if pd.api.types.is_numeric_dtype(result_df[col]):
                        logger.debug(f"Converted column '{col}' from {original_dtype} to numeric")
    
    # 4. Drop completely empty rows and columns
    original_shape = result_df.shape
    result_df = result_df.dropna(how='all')  # Drop rows that are all NaN
    result_df = result_df.loc[:, result_df.notna().any()]  # Drop columns that are all NaN
    
    if result_df.shape != original_shape:
        logger.info(f"Dropped empty rows/columns: {original_shape} -> {result_df.shape}")
    
    logger.info(f"Preprocessing complete. Final shape: {result_df.shape}")
    return result_df


def read_table_auto(path: str) -> pd.DataFrame:
    """
    Auto-detect and read CSV/Excel files with robust error handling
    CSV autodetects separator using engine="python"
    """
    if not isinstance(path, str) or not path:
        raise ValueError("Path must be a non-empty string")
    
    logger.info(f"Auto-reading file: {path}")
    
    # Determine file type from extension
    file_ext = path.lower().split('.')[-1] if '.' in path else ''
    
    try:
        if file_ext == 'csv':
            # Try to auto-detect CSV parameters
            try:
                # First, try with engine='python' for better separator detection
                df = pd.read_csv(path, engine='python', encoding='utf-8', sep=None)
                logger.debug(f"Successfully read CSV with auto-detected separator")
            except Exception as e1:
                logger.debug(f"Auto-detection failed: {e1}")
                
                # Try common encodings and separators
                encodings = ['utf-8', 'latin-1', 'cp1255', 'iso-8859-8']
                separators = [',', ';', '\t', '|']
                
                df = None
                for encoding in encodings:
                    for sep in separators:
                        try:
                            df = pd.read_csv(path, encoding=encoding, sep=sep)
                            if not df.empty and len(df.columns) > 1:
                                logger.debug(f"Successfully read CSV with encoding={encoding}, sep='{sep}'")
                                break
                        except Exception:
                            continue
                    if df is not None:
                        break
                
                if df is None:
                    raise Exception("Could not read CSV with any encoding/separator combination")
        
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(path)
            logger.debug(f"Successfully read Excel file")
            
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")
        
        if df.empty:
            logger.warning("File was read but DataFrame is empty")
            
        logger.info(f"Successfully loaded file with shape {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        raise


# Convenience function for backward compatibility
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Alias for preprocess_df"""
    return preprocess_df(df)