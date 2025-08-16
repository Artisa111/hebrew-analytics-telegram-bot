#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the improved PDF generation system
Tests guaranteed content generation with messy data
"""

import sys
import os
import pandas as pd
import numpy as np
import tempfile

# Add the repository root to sys.path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_root)

# Initialize logging early
from logging_config import setup_logging
logger = setup_logging()

logger.info("Starting guaranteed PDF content test")

def create_messy_test_data():
    """Create messy data to test robust preprocessing and guaranteed content"""
    
    logger.info("Creating messy test data")
    
    # Create problematic data that might cause issues
    data = {
        # Mixed Hebrew and English column names
        'שם': ['דוד כהן', 'שרה לוי', None, 'משה ישראלי', ''],
        'Name (English)': ['David', None, 'Rachel', 'Moses', 'Sarah'],
        
        # Messy numeric data with currencies and formats
        'משכורת_₪': ['₪8,500', '$1,200', '€900', None, '10500'],
        'Sales ($)': ['$15,000.50', '12,300', '(500)', '+2,500.75', 'N/A'],
        'Percentage': ['15%', '8.5%', None, '120%', '0.5'],
        
        # Mixed date formats
        'תאריך_העסקה': ['15/01/2020', '2019-08-22', '10.03.2018', None, 'invalid'],
        'Birth_Date': ['1990-05-15', '25/12/1985', None, '15.7.1992', 'unknown'],
        
        # Categories with Hebrew
        'מחלקה': ['מכירות', 'פיתוח', 'מכירות', None, 'משאבי אנוש'],
        'Status': ['Active', 'Inactive', 'Active', None, 'Pending'],
        
        # Very messy numeric column
        'Mixed_Numbers': ['1,234.56', 'abc', None, '-500', '1 000,5'],
    }
    
    df = pd.DataFrame(data)
    
    # Add some completely empty rows and columns
    df.loc[5] = [None] * len(df.columns)
    df.loc[6] = [None] * len(df.columns)
    df['Empty_Column'] = [None] * len(df)
    df['Another_Empty'] = [''] * len(df)
    
    logger.info(f"Created messy DataFrame with shape: {df.shape}")
    logger.info(f"Data types: {df.dtypes.to_dict()}")
    
    return df


def test_guaranteed_pdf_generation():
    """Test PDF generation with guaranteed content"""
    
    try:
        logger.info("=== Testing Guaranteed PDF Generation ===")
        
        # Create messy test data
        df = create_messy_test_data()
        
        # Try to generate PDF report
        from pdf_report import generate_complete_data_report
        
        # Create temporary output path
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        logger.info(f"Generating PDF report to: {output_path}")
        
        # This should work even with messy data and guarantee content in all sections
        result_path = generate_complete_data_report(df, output_path, include_charts=True)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            logger.info(f"✅ PDF generated successfully!")
            logger.info(f"   File: {result_path}")
            logger.info(f"   Size: {file_size:,} bytes")
            
            # Basic validation - file should be reasonably sized
            if file_size > 10000:  # At least 10KB
                logger.info("✅ PDF file size looks reasonable - likely contains content")
                return True
            else:
                logger.warning(f"⚠️  PDF file size ({file_size} bytes) seems too small")
                return False
        else:
            logger.error("❌ PDF generation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if 'output_path' in locals() and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Cleaned up test file: {output_path}")
            except:
                pass


def test_preprocessing():
    """Test the preprocessing utilities"""
    
    try:
        logger.info("=== Testing Preprocessing Utilities ===")
        
        from preprocess import preprocess_df, coerce_numeric, normalize_column_name
        
        # Test column name normalization
        test_names = [
            "שם מלא",  # Hebrew with space
            "Name (English)",  # English with parentheses
            "  Mixed  Name  ",  # Extra spaces
            "Column@#$%With&*Special()",  # Special characters
        ]
        
        logger.info("Testing column name normalization:")
        for name in test_names:
            normalized = normalize_column_name(name)
            logger.info(f"  '{name}' -> '{normalized}'")
        
        # Test numeric coercion
        test_series = pd.Series([
            '₪1,234.56',
            '$500',
            '15%', 
            '(200)',
            '+150.75',
            'N/A',
            None
        ])
        
        logger.info("Testing numeric coercion:")
        logger.info(f"Original: {test_series.tolist()}")
        
        numeric_result = coerce_numeric(test_series)
        logger.info(f"Coerced: {numeric_result.tolist()}")
        
        # Test full preprocessing
        df = create_messy_test_data()
        logger.info(f"Original DataFrame shape: {df.shape}")
        logger.info(f"Original dtypes: {df.dtypes.to_dict()}")
        
        processed_df = preprocess_df(df)
        logger.info(f"Processed DataFrame shape: {processed_df.shape}")
        logger.info(f"Processed dtypes: {processed_df.dtypes.to_dict()}")
        
        logger.info("✅ Preprocessing tests completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Preprocessing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_i18n():
    """Test the i18n module"""
    
    try:
        logger.info("=== Testing i18n Module ===")
        
        from i18n import t, format_date_time
        
        # Test text translation
        test_keys = [
            "report_title",
            "missing_values_title", 
            "no_missing_values",
            "error_no_data",
            "nonexistent_key"  # Should fallback to key itself
        ]
        
        logger.info("Testing translations:")
        for key in test_keys:
            text = t(key)
            logger.info(f"  {key}: {text}")
        
        # Test formatting
        formatted_text = t("high_missing_data", pct=25.5)
        logger.info(f"Formatted text: {formatted_text}")
        
        # Test date formatting
        date_str = format_date_time()
        logger.info(f"Formatted date: {date_str}")
        
        logger.info("✅ i18n tests completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ i18n test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    
    logger.info("🚀 Starting Guaranteed PDF Content Tests")
    logger.info("="*60)
    
    tests = [
        ("Preprocessing", test_preprocessing),
        ("i18n", test_i18n),
        ("PDF Generation", test_guaranteed_pdf_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Starting {test_name} Test ---")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASSED" if result else "FAILED"
            logger.info(f"--- {test_name} Test {status} ---\n")
        except Exception as e:
            logger.error(f"--- {test_name} Test FAILED with exception: {e} ---\n")
            results.append((test_name, False))
    
    # Summary
    logger.info("="*60)
    logger.info("📊 TEST RESULTS SUMMARY:")
    logger.info("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    logger.info("="*60)
    logger.info(f"FINAL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Guaranteed PDF content system is working!")
        return True
    else:
        logger.info(f"⚠️  {total-passed} tests failed. Check logs above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)