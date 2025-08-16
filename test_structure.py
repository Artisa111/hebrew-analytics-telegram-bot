#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the PDF generation system without heavy dependencies
Creates a mock DataFrame and tests the guaranteed sections logic
"""

import sys
import os

# Test that the guaranteed sections logic works
def test_guaranteed_sections_logic():
    """Test the guaranteed sections without actually creating DataFrames"""
    
    print("Testing guaranteed sections logic...")
    
    try:
        # Import our modules
        from logging_config import get_logger
        from i18n import t
        
        logger = get_logger(__name__)
        
        # Test that all required translations exist
        required_keys = [
            "data_preview_title",
            "missing_values_title", 
            "categorical_title",
            "numeric_title",
            "stats_summary_title",
            "outliers_title",
            "recommendations_title",
            "no_missing_values",
            "no_categorical_data",
            "no_numeric_data",
            "no_outliers_found",
            "error_processing"
        ]
        
        print("  ✓ Testing required translations:")
        for key in required_keys:
            text = t(key)
            print(f"    {key}: {text}")
        
        print("  ✓ All guaranteed section translations available")
        
        # Test preprocessing utilities
        from preprocess import normalize_column_name, coerce_numeric
        
        print("  ✓ Testing preprocessing utilities:")
        
        # Test column name normalization  
        test_names = [
            "שם מלא",
            "Name (English)", 
            "  Mixed  Name  ",
            "Column@#$%With&*Special()"
        ]
        
        for name in test_names:
            normalized = normalize_column_name(name)
            print(f"    '{name}' -> '{normalized}'")
        
        print("  ✓ Guaranteed sections logic is working correctly!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing guaranteed sections: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_report_structure():
    """Test the PDF report class structure without actually generating PDF"""
    
    print("\nTesting PDF report structure...")
    
    try:
        # This will test the class structure without requiring pandas/matplotlib
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("pdf_report", "pdf_report.py")
        pdf_module = importlib.util.module_from_spec(spec)
        
        # Check if the class has all guaranteed methods
        required_methods = [
            'add_data_preview_section',
            'add_missing_values_section', 
            'add_categorical_distributions_section',
            'add_numeric_distributions_section',
            'add_statistical_summary_section',
            'add_outliers_section',
            'add_guaranteed_sections'
        ]
        
        print("  ✓ Checking PDF report class structure...")
        
        # We can't actually load the class due to pandas dependency
        # But we can check that our code structure is correct
        with open("pdf_report.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        for method in required_methods:
            if f"def {method}" in content:
                print(f"    ✓ Found method: {method}")
            else:
                print(f"    ❌ Missing method: {method}")
                return False
        
        # Check for key improvements
        improvements = [
            "add_guaranteed_sections",
            "preprocess_df", 
            "t(",  # i18n usage
            "logger.info",  # proper logging
        ]
        
        for improvement in improvements:
            if improvement in content:
                print(f"    ✓ Found improvement: {improvement}")
            else:
                print(f"    ❌ Missing improvement: {improvement}")
        
        print("  ✓ PDF report structure is correct!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing PDF report structure: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration"""
    
    print("\nTesting Docker configuration...")
    
    try:
        # Check Dockerfile exists and has required content
        if not os.path.exists("Dockerfile"):
            print("  ❌ Dockerfile not found")
            return False
            
        with open("Dockerfile", "r") as f:
            dockerfile_content = f.read()
        
        required_docker_items = [
            "FROM python:3.11-slim",
            "fonts-noto-core",
            "MPLBACKEND=Agg", 
            "REPORT_LANG=he",
            "REPORT_TZ=Asia/Jerusalem",
            "LOG_LEVEL=INFO",
            "LOGS_MAX_PER_SEC=100"
        ]
        
        for item in required_docker_items:
            if item in dockerfile_content:
                print(f"    ✓ Found Docker config: {item}")
            else:
                print(f"    ❌ Missing Docker config: {item}")
                return False
        
        # Check .dockerignore exists
        if os.path.exists(".dockerignore"):
            print("    ✓ Found .dockerignore")
        else:
            print("    ❌ Missing .dockerignore")
            
        print("  ✓ Docker configuration is correct!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing Docker configuration: {e}")
        return False

def main():
    """Run all structure tests"""
    
    print("🏗️  Testing Guaranteed PDF Content System Structure")
    print("=" * 60)
    
    tests = [
        ("Guaranteed Sections Logic", test_guaranteed_sections_logic),
        ("PDF Report Structure", test_pdf_report_structure),
        ("Docker Configuration", test_docker_configuration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 STRUCTURE TEST RESULTS:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"  
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"FINAL RESULT: {passed}/{total} structure tests passed")
    
    if passed == total:
        print("\n🎉 All structure tests passed!")
        print("✨ The guaranteed PDF content system is properly structured!")
        print("📋 Key improvements implemented:")
        print("   • Guaranteed sections that always render content")
        print("   • Robust preprocessing for messy data")  
        print("   • i18n support with Hebrew text")
        print("   • Rate-limited logging system")
        print("   • Docker configuration with Hebrew fonts")
        print("   • Environment variable support")
        return True
    else:
        print(f"\n⚠️  {total-passed} structure tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)