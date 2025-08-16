# -*- coding: utf-8 -*-
"""
Data preprocessing utilities module
Provides robust data cleaning, normalization, and parsing functions
"""

import pandas as pd
import numpy as np
import re
from typing import Optional, Union, Any
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


def normalize_column_name(name: str) -> str:
    """
    Normalize column name by stripping whitespace, unifying spaces/underscores, and converting to lowercase
    
    Args:
        name: Original column name
        
    Returns:
        str: Normalized column name
    """
    if not isinstance(name, str):
        name = str(name)
    
    # Strip and trim whitespace
    normalized = name.strip()
    
    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Replace spaces with underscores
    normalized = normalized.replace(' ', '_')
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Remove special characters except underscores and alphanumeric
    normalized = re.sub(r'[^a-z0-9_]', '_', normalized)
    
    # Remove multiple underscores
    normalized = re.sub(r'_+', '_', normalized)
    
    # Remove leading/trailing underscores
    normalized = normalized.strip('_')
    
    # Ensure name is not empty
    if not normalized:
        normalized = 'unnamed_column'
    
    logger.debug(f"Column name normalized: '{name}' -> '{normalized}'")
    return normalized


def coerce_numeric(series: pd.Series) -> pd.Series:
    """
    Convert number-like strings to numeric with support for:
    - Currencies (₪, $, €, £, ¥)
    - Percent symbol (%)
    - Leading '+' sign
    - Parentheses for negatives: (123) -> -123
    - Thousand separators and mixed decimal styles: "1 234", "12,5", "1,234.56", "1.234,56"
    
    Args:
        series: Pandas series to convert
        
    Returns:
        pd.Series: Series with numeric values where possible, original values otherwise
    """
    if series.dtype in ['int64', 'float64']:
        return series
    
    converted_series = series.copy()
    
    try:
        # Track conversions for logging
        conversions = 0
        
        for idx, value in series.items():
            if pd.isna(value):
                continue
                
            original_value = str(value).strip()
            if not original_value:
                continue
                
            cleaned_value = original_value
            is_negative = False
            is_percentage = False
            
            # Handle parentheses for negatives
            if cleaned_value.startswith('(') and cleaned_value.endswith(')'):
                is_negative = True
                cleaned_value = cleaned_value[1:-1]
            
            # Handle percentage
            if cleaned_value.endswith('%'):
                is_percentage = True
                cleaned_value = cleaned_value[:-1]
            
            # Remove currency symbols
            currency_symbols = ['₪', '$', '€', '£', '¥', '¢', '₽', '¥', '₹']
            for symbol in currency_symbols:
                cleaned_value = cleaned_value.replace(symbol, '')
            
            # Remove leading '+' sign
            if cleaned_value.startswith('+'):
                cleaned_value = cleaned_value[1:]
            
            # Handle thousand separators and decimal points
            # Common patterns: "1,234.56", "1.234,56", "1 234.5", "1234,5"
            cleaned_value = cleaned_value.strip()
            
            # Check if it's already a valid number
            if re.match(r'^-?\d+\.?\d*$', cleaned_value):
                num_value = float(cleaned_value)
            else:
                # Handle complex formatting
                # Remove spaces (thousand separator)
                cleaned_value = re.sub(r'\s', '', cleaned_value)
                
                # Determine decimal separator
                # If there are multiple commas or dots, the last one is likely decimal
                comma_count = cleaned_value.count(',')
                dot_count = cleaned_value.count('.')
                
                if comma_count > 0 and dot_count > 0:
                    # Both present - last one is decimal separator
                    last_comma = cleaned_value.rfind(',')
                    last_dot = cleaned_value.rfind('.')
                    
                    if last_comma > last_dot:
                        # Comma is decimal separator
                        cleaned_value = cleaned_value.replace('.', '').replace(',', '.')
                    else:
                        # Dot is decimal separator
                        cleaned_value = cleaned_value.replace(',', '')
                        
                elif comma_count > 0 and dot_count == 0:
                    # Only commas - check if it's decimal or thousand separator
                    if comma_count == 1 and len(cleaned_value.split(',')[1]) <= 2:
                        # Likely decimal separator
                        cleaned_value = cleaned_value.replace(',', '.')
                    else:
                        # Thousand separators
                        cleaned_value = cleaned_value.replace(',', '')
                        
                elif dot_count > 1:
                    # Multiple dots - all but last are thousand separators
                    parts = cleaned_value.split('.')
                    cleaned_value = ''.join(parts[:-1]) + '.' + parts[-1]
                
                # Try to convert to float
                try:
                    num_value = float(cleaned_value)
                except ValueError:
                    continue  # Skip this value if conversion fails
            
            # Apply negative sign
            if is_negative:
                num_value = -num_value
            
            # Apply percentage conversion
            if is_percentage:
                num_value = num_value / 100
            
            converted_series.iloc[idx] = num_value
            conversions += 1
            
        if conversions > 0:
            logger.info(f"Converted {conversions} values to numeric in series '{series.name}'")
            
    except Exception as e:
        logger.warning(f"Error in numeric coercion for series '{series.name}': {e}")
        
    return converted_series


def detect_and_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse obvious date columns with dayfirst heuristic; keep original on failure
    
    Args:
        df: Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with parsed date columns where possible
    """
    df_copy = df.copy()
    date_columns_parsed = 0
    
    try:
        for col in df.columns:
            # Skip if already datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
                
            # Skip if numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            # Look for date-like column names
            date_indicators = ['date', 'time', 'created', 'updated', 'modified', 'birth', 'תאריך', 'זמן']
            col_lower = str(col).lower()
            
            is_date_column = any(indicator in col_lower for indicator in date_indicators)
            
            if not is_date_column:
                # Sample some values to see if they look like dates
                sample_size = min(100, len(df))
                sample_values = df[col].dropna().astype(str).head(sample_size)
                
                if len(sample_values) == 0:
                    continue
                
                # Check for date-like patterns
                date_patterns = [
                    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or DD-MM-YYYY
                    r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD or YYYY-MM-DD
                    r'\d{1,2}\.\d{1,2}\.\d{2,4}',      # DD.MM.YYYY
                    r'\d{2,4}\.\d{1,2}\.\d{1,2}',      # YYYY.MM.DD
                ]
                
                date_like_count = 0
                for value in sample_values:
                    value_str = str(value).strip()
                    if any(re.search(pattern, value_str) for pattern in date_patterns):
                        date_like_count += 1
                
                # If more than 50% look like dates, try to parse
                if date_like_count / len(sample_values) < 0.5:
                    continue
            
            # Try to parse dates with dayfirst=True (European format)
            try:
                original_series = df[col].copy()
                
                # First attempt with dayfirst=True
                parsed_series = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
                
                # Check if parsing was successful (not too many NaT values)
                valid_dates = parsed_series.notna().sum()
                total_non_null = df[col].notna().sum()
                
                if total_non_null > 0 and valid_dates / total_non_null >= 0.7:
                    df_copy[col] = parsed_series
                    date_columns_parsed += 1
                    logger.info(f"Parsed {valid_dates}/{total_non_null} dates in column '{col}'")
                else:
                    # Try without dayfirst if that didn't work well
                    parsed_series_alt = pd.to_datetime(df[col], dayfirst=False, errors='coerce')
                    valid_dates_alt = parsed_series_alt.notna().sum()
                    
                    if valid_dates_alt > valid_dates and valid_dates_alt / total_non_null >= 0.7:
                        df_copy[col] = parsed_series_alt
                        date_columns_parsed += 1
                        logger.info(f"Parsed {valid_dates_alt}/{total_non_null} dates in column '{col}' (US format)")
                    
            except Exception as e:
                logger.debug(f"Failed to parse dates in column '{col}': {e}")
                continue
                
    except Exception as e:
        logger.warning(f"Error in date parsing: {e}")
        
    if date_columns_parsed > 0:
        logger.info(f"Successfully parsed dates in {date_columns_parsed} columns")
        
    return df_copy


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply comprehensive preprocessing: column renaming and type coercions
    
    Args:
        df: Input DataFrame
        
    Returns:
        pd.DataFrame: Preprocessed DataFrame
    """
    logger.info(f"Starting preprocessing of DataFrame with shape {df.shape}")
    
    # Start with a copy
    processed_df = df.copy()
    
    # 1. Normalize column names
    logger.info("Normalizing column names...")
    original_columns = list(processed_df.columns)
    new_columns = [normalize_column_name(col) for col in original_columns]
    
    # Handle duplicate column names
    seen_columns = set()
    final_columns = []
    for col in new_columns:
        if col in seen_columns:
            counter = 2
            while f"{col}_{counter}" in seen_columns:
                counter += 1
            col = f"{col}_{counter}"
        seen_columns.add(col)
        final_columns.append(col)
    
    processed_df.columns = final_columns
    
    renamed_count = sum(1 for i, (old, new) in enumerate(zip(original_columns, final_columns)) if old != new)
    if renamed_count > 0:
        logger.info(f"Renamed {renamed_count} columns")
    
    # 2. Parse dates
    logger.info("Detecting and parsing date columns...")
    processed_df = detect_and_parse_dates(processed_df)
    
    # 3. Coerce numeric values
    logger.info("Converting numeric columns...")
    numeric_conversions = 0
    
    for col in processed_df.columns:
        # Skip datetime columns
        if pd.api.types.is_datetime64_any_dtype(processed_df[col]):
            continue
            
        # Skip if already numeric
        if pd.api.types.is_numeric_dtype(processed_df[col]):
            continue
            
        # Try to convert to numeric
        original_series = processed_df[col].copy()
        converted_series = coerce_numeric(original_series)
        
        # Check if conversion was successful
        if not converted_series.equals(original_series):
            processed_df[col] = pd.to_numeric(converted_series, errors='ignore')
            if pd.api.types.is_numeric_dtype(processed_df[col]):
                numeric_conversions += 1
    
    if numeric_conversions > 0:
        logger.info(f"Converted {numeric_conversions} columns to numeric type")
    
    logger.info(f"Preprocessing completed. Final shape: {processed_df.shape}")
    return processed_df


def read_table_auto(path: str) -> pd.DataFrame:
    """
    Auto-detect file format and read table data
    - For CSV: use pandas.read_csv with auto-delimiter detection
    - For XLSX: use pandas.read_excel
    
    Args:
        path: Path to the file
        
    Returns:
        pd.DataFrame: Loaded DataFrame
        
    Raises:
        ValueError: If file format is not supported or file cannot be read
    """
    if not os.path.exists(path):
        raise ValueError(f"File not found: {path}")
    
    file_extension = os.path.splitext(path)[1].lower()
    
    try:
        if file_extension == '.csv':
            logger.info(f"Reading CSV file with auto-delimiter detection: {path}")
            # Use python engine with sep=None for auto-detection
            df = pd.read_csv(path, sep=None, engine='python', encoding='utf-8')
            
            # If that fails, try with different encodings
            if df.empty or len(df.columns) == 1:
                encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'cp1255']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(path, sep=None, engine='python', encoding=encoding)
                        if not df.empty and len(df.columns) > 1:
                            logger.info(f"Successfully read CSV with encoding: {encoding}")
                            break
                    except Exception:
                        continue
                        
        elif file_extension in ['.xlsx', '.xls']:
            logger.info(f"Reading Excel file: {path}")
            df = pd.read_excel(path)
            
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        logger.info(f"Successfully loaded file with shape {df.shape}: {path}")
        return df
        
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise ValueError(f"Failed to read file {path}: {e}")