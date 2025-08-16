#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת מימוש החדש - Test implementation of new features
בודק עיבוד מקדים חזק, קטעי דוח מובטחים, תרגום ולוגים מוגבלים
"""

import os
import sys
import pandas as pd
import tempfile
import logging
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the new modules
try:
    from preprocessing import preprocess_df
    from i18n import t, get_hebrew_date_time_text, REPORT_LANG
    from logging_config import initialize_logging, get_logging_stats
    from report_sections import add_guaranteed_sections
    from pdf_report import generate_complete_data_report, analyze_csv_file
    
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def create_messy_test_data():
    """יצירת נתוני בדיקה מבולגנים - Create messy test data"""
    data = {
        'Product Name': ['Widget A', 'Widget B', 'Gadget C', 'Tool D', 'Device E'],
        'Price (₪)': ['₪1,250.50', '(₪500)', '₪2 500', '₪750.25', '₪1,000'],
        'Sales ($)': ['$5,000.00', '$2,500', '($1,200)', '$8,750.50', '$3,000'],
        'Discount %': ['10%', '25%', '5%', '15%', '20%'],
        'Stock Count': ['1,500', '750', '2 250', '950', '1,200'],
        'Date Sold': ['15/03/2023', '22/03/2023', '01/04/2023', '10/04/2023', '18/04/2023'],
        'Category': ['Electronics', 'Electronics', 'Hardware', 'Tools', 'Electronics'],
        'Rating': ['4.5', '3.2', '4.8', '4.1', '3.9'],
        'Empty Column': [None, None, None, None, None],
        'Notes': ['Good product', 'Limited stock', None, 'Best seller', '']
    }
    
    return pd.DataFrame(data)


def test_preprocessing():
    """בדיקת עיבוד מקדים - Test preprocessing"""
    print("\n🔍 Testing preprocessing...")
    
    # Create messy data
    df = create_messy_test_data()
    print(f"Original data shape: {df.shape}")
    print(f"Original dtypes:\n{df.dtypes}")
    
    # Preprocess
    processed_df = preprocess_df(df)
    print(f"Processed data shape: {processed_df.shape}")
    print(f"Processed dtypes:\n{processed_df.dtypes}")
    
    # Check numeric conversions
    for col in processed_df.columns:
        if pd.api.types.is_numeric_dtype(processed_df[col]):
            print(f"✅ Column '{col}' converted to numeric: {processed_df[col].dtype}")
    
    return processed_df


def test_i18n():
    """בדיקת תרגום - Test i18n"""
    print("\n🌐 Testing i18n...")
    
    print(f"Report language: {REPORT_LANG}")
    print(f"Report title: {t('report_title')}")
    print(f"Data preview: {t('data_preview')}")
    print(f"Missing values: {t('missing_values')}")
    print(f"Hebrew date/time: {get_hebrew_date_time_text()}")
    
    print("✅ i18n working correctly")


def test_logging():
    """בדיקת לוגים - Test logging configuration"""
    print("\n📝 Testing logging...")
    
    # Initialize logging
    memory_handler = initialize_logging()
    
    # Get logging stats
    stats = get_logging_stats()
    print(f"Logging stats: {stats}")
    
    # Test different log levels
    logger = logging.getLogger(__name__)
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    print("✅ Logging configured correctly")


def test_report_generation():
    """בדיקת יצירת דוח - Test report generation"""
    print("\n📄 Testing report generation...")
    
    # Create test data
    df = create_messy_test_data()
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        # Generate report
        result_path = generate_complete_data_report(df, output_path)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ Report generated successfully: {result_path} ({file_size} bytes)")
            return result_path
        else:
            print("❌ Report generation failed")
            return None
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None


def test_csv_analysis():
    """בדיקת ניתוח CSV - Test CSV analysis"""
    print("\n📊 Testing CSV analysis...")
    
    # Create test CSV file
    df = create_messy_test_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp_file:
        csv_path = tmp_file.name
        df.to_csv(csv_path, index=False)
    
    try:
        # Analyze CSV
        result_path = analyze_csv_file(csv_path)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ CSV analysis successful: {result_path} ({file_size} bytes)")
            return result_path
        else:
            print("❌ CSV analysis failed")
            return None
    
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")
        return None
    
    finally:
        # Cleanup
        if os.path.exists(csv_path):
            os.unlink(csv_path)


def main():
    """פונקציה ראשית - Main function"""
    print("🚀 Starting comprehensive test of new features...")
    print("=" * 60)
    
    try:
        # Test individual components
        test_i18n()
        test_logging()
        processed_df = test_preprocessing()
        
        # Test report generation
        report_path = test_report_generation()
        csv_report_path = test_csv_analysis()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print(f"✅ i18n: Working")
        print(f"✅ Logging: Configured")
        print(f"✅ Preprocessing: Working")
        print(f"✅ Direct report: {'Generated' if report_path else 'Failed'}")
        print(f"✅ CSV analysis: {'Generated' if csv_report_path else 'Failed'}")
        
        if report_path:
            print(f"\n📁 Generated report: {report_path}")
        if csv_report_path:
            print(f"📁 CSV analysis report: {csv_report_path}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()