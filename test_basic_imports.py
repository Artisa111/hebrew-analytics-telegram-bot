#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic import test to verify all new modules work together
"""

import sys
import os

# Test basic imports
def test_imports():
    """Test that all new modules can be imported"""
    
    print("Testing imports...")
    
    try:
        # Test logging first
        print("  ✓ Testing logging_config...")
        from logging_config import setup_logging, get_logger
        logger = setup_logging()
        logger.info("Logging system initialized successfully")
        
        print("  ✓ Testing i18n...")
        from i18n import t, format_date_time
        
        # Test some translations
        title = t("report_title")
        print(f"    Hebrew title: {title}")
        
        date_str = format_date_time()
        print(f"    Formatted date: {date_str}")
        
        print("  ✓ Testing preprocess...")
        from preprocess import normalize_column_name, preprocess_df
        
        # Test column normalization
        test_name = "שם מלא (Hebrew Name)"
        normalized = normalize_column_name(test_name)
        print(f"    Normalized column: '{test_name}' -> '{normalized}'")
        
        print("  ✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_environment_variables():
    """Test environment variable support"""
    
    print("\nTesting environment variables...")
    
    # Set some test values
    os.environ['REPORT_LANG'] = 'he'
    os.environ['REPORT_TZ'] = 'Asia/Jerusalem'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    try:
        from i18n import get_default_language, get_timezone
        
        lang = get_default_language()
        tz = get_timezone()
        
        print(f"  ✓ Default language: {lang}")
        print(f"  ✓ Timezone: {tz}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Environment variable test failed: {e}")
        return False

def main():
    """Run basic tests"""
    
    print("🧪 Running Basic Module Tests")
    print("=" * 50)
    
    # Run tests
    import_test = test_imports()
    env_test = test_environment_variables()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    print(f"Import Test:      {'✅ PASS' if import_test else '❌ FAIL'}")
    print(f"Environment Test: {'✅ PASS' if env_test else '❌ FAIL'}")
    
    if import_test and env_test:
        print("\n🎉 All basic tests passed!")
        print("The new guaranteed PDF content system modules are working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)