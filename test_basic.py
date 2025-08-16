#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple syntax check for our implementation
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that our modules can be imported without errors"""
    print("🔧 Testing module imports...")
    
    try:
        # Test config module
        from config import t, REPORT_LANG, REPORT_TZ, LOGS_MAX_PER_SEC
        print("✅ config module imported successfully")
        print(f"   REPORT_LANG: {REPORT_LANG}")
        print(f"   REPORT_TZ: {REPORT_TZ}")
        print(f"   LOGS_MAX_PER_SEC: {LOGS_MAX_PER_SEC}")
        
        # Test translation function
        report_date = t("report_date")
        print(f"   t('report_date'): {report_date}")
        
    except Exception as e:
        print(f"❌ Error importing config: {e}")
        return False
    
    try:
        # Test logging setup module
        from logging_setup import TokenBucketFilter, setup_logging
        print("✅ logging_setup module imported successfully")
        
    except Exception as e:
        print(f"❌ Error importing logging_setup: {e}")
        return False
    
    # Note: Can't test data_preprocessing and guaranteed_content without pandas
    print("⚠️  Skipping data_preprocessing and guaranteed_content tests (requires pandas)")
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("📁 Testing file structure...")
    
    required_files = [
        "config.py",
        "logging_setup.py", 
        "data_preprocessing.py",
        "guaranteed_content.py",
        "pdf_report.py",
        "test_messy_data.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def main():
    """Run basic tests without external dependencies"""
    print("🚀 Basic Implementation Tests (No External Dependencies)")
    print("=" * 60)
    
    success = True
    
    if not test_file_structure():
        success = False
    
    print()
    
    if not test_imports():
        success = False
    
    print("=" * 60)
    if success:
        print("🎉 Basic tests passed! Ready for full testing with dependencies.")
    else:
        print("❌ Some basic tests failed. Check the errors above.")

if __name__ == "__main__":
    main()