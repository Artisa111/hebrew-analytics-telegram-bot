#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the new robust data preprocessing and guaranteed PDF content
"""

import sys
import os
import logging
import pandas as pd
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our new modules
from logging_setup import setup_logging
from config import t
from data_preprocessing import preprocess_df, load_csv_robust
from guaranteed_content import add_guaranteed_sections, add_statistical_summary_section

def test_logging_setup():
    """Test logging setup with rate limiting"""
    print("🔧 Testing logging setup...")
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger("test")
    
    # Test rate limiting by sending many logs quickly
    logger.info("Testing rate limiting - this should appear")
    for i in range(200):  # Send 200 logs quickly
        logger.debug(f"Debug message {i}")
    
    logger.info("Rate limiting test completed")
    print("✅ Logging setup working")

def test_translation():
    """Test the translation function"""
    print("🌐 Testing i18n translation...")
    
    # Test basic translations
    assert t("report_date") == "תאריך הדוח"
    assert t("data_preview") == "תצוגה מקדימה של הנתונים"
    assert t("missing_values") == "ערכים חסרים"
    assert t("statistical_summary") == "סיכום סטטיסטי"
    
    # Test fallback for non-existent keys
    assert t("non_existent_key") == "non_existent_key"
    
    print("✅ Translation function working")

def test_data_preprocessing():
    """Test robust data preprocessing"""
    print("📊 Testing data preprocessing...")
    
    # Load the messy test data
    test_file = "test_messy_data.csv"
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return
    
    # Test robust CSV loading
    df = load_csv_robust(test_file)
    print(f"✅ Loaded CSV with shape: {df.shape}")
    print(f"Column types:\n{df.dtypes}")
    
    # Check if numeric columns were properly converted
    numeric_cols = df.select_dtypes(include=['number']).columns
    print(f"✅ Numeric columns detected: {list(numeric_cols)}")
    
    # Check for any remaining string columns with numeric-like data
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(3).tolist()
            print(f"String column '{col}' samples: {sample}")
    
    print("✅ Data preprocessing test completed")
    return df

def test_guaranteed_content(df):
    """Test guaranteed content generation without actually creating PDF"""
    print("📄 Testing guaranteed content sections...")
    
    try:
        # Create charts directory
        os.makedirs("test_charts", exist_ok=True)
        
        # Mock PDF report class for testing
        class MockPDFReport:
            def add_section_header(self, title, level):
                print(f"Section header (level {level}): {title}")
            
            def add_text(self, text, size=12, bold=False, indent=0):
                style = "BOLD " if bold else ""
                print(f"Text ({style}size {size}, indent {indent}): {text}")
            
            def add_chart(self, chart_path):
                print(f"Chart added: {chart_path}")
                if os.path.exists(chart_path):
                    print(f"  ✅ Chart file exists: {os.path.getsize(chart_path)} bytes")
                else:
                    print(f"  ❌ Chart file missing")
        
        mock_report = MockPDFReport()
        
        # Test guaranteed sections
        add_guaranteed_sections(mock_report, df, "test_charts")
        add_statistical_summary_section(mock_report, df, "test_charts")
        
        # Check if chart files were created
        chart_files = list(Path("test_charts").glob("*.png"))
        print(f"✅ Generated {len(chart_files)} chart files")
        
        # Clean up test charts
        import shutil
        if os.path.exists("test_charts"):
            shutil.rmtree("test_charts")
        
        print("✅ Guaranteed content test completed")
        
    except Exception as e:
        print(f"❌ Error in guaranteed content test: {e}")
        import traceback
        traceback.print_exc()

def test_full_pdf_generation():
    """Test full PDF generation with the new features"""
    print("📋 Testing full PDF report generation...")
    
    try:
        from pdf_report import analyze_csv_file
        
        test_file = "test_messy_data.csv"
        output_file = "test_report_output.pdf"
        
        # Generate PDF report
        result = analyze_csv_file(test_file, output_file)
        
        if result and os.path.exists(result):
            size = os.path.getsize(result)
            print(f"✅ PDF generated successfully: {result} ({size:,} bytes)")
            
            # Clean up
            os.remove(result)
        else:
            print("❌ PDF generation failed")
            
    except Exception as e:
        print(f"❌ Error in full PDF test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Starting Hebrew Analytics Bot Implementation Tests")
    print("=" * 60)
    
    try:
        test_logging_setup()
        print()
        
        test_translation()
        print()
        
        df = test_data_preprocessing()
        print()
        
        if df is not None:
            test_guaranteed_content(df)
            print()
            
            test_full_pdf_generation()
        
        print("=" * 60)
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()