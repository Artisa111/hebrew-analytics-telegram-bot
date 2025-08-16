#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Hebrew PDF generation fixes
"""

import os
import sys
import pandas as pd
import logging
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_font_resolution():
    """Test Hebrew font resolution mechanism"""
    print("🔍 Testing Hebrew font resolution...")
    
    try:
        from pdf_report import HebrewPDFReport
        
        # Create PDF report instance to test font resolution
        report = HebrewPDFReport()
        
        # Test the font resolution method
        regular_font, bold_font = report.resolve_hebrew_fonts()
        
        print(f"✅ Font resolution completed:")
        print(f"   Regular font: {regular_font}")
        print(f"   Bold font: {bold_font}")
        
        if regular_font and bold_font:
            print("✅ Both fonts found - Hebrew text should render correctly")
            return True
        elif regular_font:
            print("⚠️  Only regular font found - bold text will use regular font")
            return True
        else:
            print("❌ No Hebrew fonts found - Hebrew text may not display correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing font resolution: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("\n🔍 Testing PDF generation...")
    
    try:
        from pdf_report import generate_complete_data_report
        
        # Create sample data
        data = {
            'שם': ['דוד', 'רחל', 'יוסי', 'שרה', 'אבי'],
            'גיל': [25, 30, 35, 28, 42],
            'משכורת': [8000, 12000, 15000, 9500, 18000],
            'עיר': ['תל אביב', 'ירושלים', 'חיפה', 'באר שבע', 'נתניה']
        }
        
        df = pd.DataFrame(data)
        
        # Generate PDF report
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        result_path = generate_complete_data_report(df, output_path, include_charts=True)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ PDF generated successfully: {result_path}")
            print(f"   File size: {file_size:,} bytes")
            
            # Clean up
            os.remove(result_path)
            return True
        else:
            print("❌ PDF generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_matplotlib_backend():
    """Test matplotlib backend setup"""
    print("\n🔍 Testing matplotlib backend...")
    
    try:
        import matplotlib
        backend = matplotlib.get_backend()
        print(f"✅ Matplotlib backend: {backend}")
        
        if backend == 'Agg':
            print("✅ Headless backend is correctly configured")
            return True
        else:
            print(f"⚠️  Backend is {backend} - should be 'Agg' for headless environments")
            return False
            
    except Exception as e:
        print(f"❌ Error checking matplotlib backend: {e}")
        return False

def test_imports():
    """Test all critical imports"""
    print("\n🔍 Testing imports...")
    
    modules_to_test = [
        'matplotlib',
        'fpdf',
        'arabic_reshaper', 
        'bidi.algorithm',
        'pandas',
        'requests'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("✅ All imports successful")
        return True

def main():
    """Run all tests"""
    print("🚀 Running Hebrew PDF generation tests...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Matplotlib Backend", test_matplotlib_backend),
        ("Font Resolution", test_font_resolution),
        ("PDF Generation", test_pdf_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Hebrew PDF generation should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)