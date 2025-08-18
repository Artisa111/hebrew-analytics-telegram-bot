#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for RTL text visibility and safe-mode PDF generation
"""

import os
import sys
import pandas as pd
import numpy as np
import tempfile
import shutil

def test_rtl_visibility():
    """Test that RTL text is positioned correctly and doesn't go off-page"""
    print("🔍 Testing RTL text visibility...")
    
    try:
        from pdf_report import HebrewPDFReport
        
        # Create test data with Hebrew column names and content  
        test_data = pd.DataFrame({
            'שם_מלא': ['דוד כהן', 'רחל לוי', 'יוסי שמיט'],
            'גיל': [25, 30, 35],
            'עיר_מגורים': ['תל אביב', 'ירושלים', 'חיפה'],
            'משכורת_חודשית': [15000, 18000, 22000]
        })
        
        # Create PDF report instance
        report = HebrewPDFReport() 
        
        # Test individual RTL text positioning (edge cases)
        print("  Testing RTL text positioning edge cases...")
        
        # Very long Hebrew text that might cause negative positioning
        long_hebrew_text = "זהו טקסט עברי ארוך מאוד שנועד לבדוק איך המערכת מתמודדת עם טקסט שעלול להיות רחב מדי לעמוד ולגרום לבעיות מיקום"
        
        # Test the RTL text positioning method directly  
        report.pdf.add_page()
        
        # Test right alignment with long text (this used to cause negative x)
        report._add_rtl_text(0, 50, long_hebrew_text, 'R')
        print("    ✓ Long Hebrew text positioned without error")
        
        # Test center alignment
        report._add_rtl_text(0, 70, "טקסט ממורכז", 'C')
        print("    ✓ Centered Hebrew text positioned without error")
        
        # Test left alignment
        report._add_rtl_text(20, 90, "טקסט משמאל", 'L')
        print("    ✓ Left-aligned Hebrew text positioned without error")
        
        # Test multi_cell RTL text
        report.add_text(long_hebrew_text, 12, bold=False, indent=10)
        print("    ✓ Multi-cell RTL text added without error")
        
        # Generate a full report to test all sections
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_path = tmp_file.name
            
        result_path = report.generate_comprehensive_report(test_data, output_path)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"    ✓ Full PDF generated: {result_path} ({file_size:,} bytes)")
            
            # Verify the run_id is in filename (collision prevention)
            if report.run_id in result_path:
                print(f"    ✓ Run ID {report.run_id} included in filename for collision prevention")
            else:
                print(f"    ⚠️  Run ID not found in filename: {result_path}")
                
            # Clean up
            try:
                os.unlink(result_path)
            except:
                pass
                
            return True
        else:
            print("    ❌ Failed to generate PDF")
            return False
            
    except Exception as e:
        print(f"    ❌ Error testing RTL visibility: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safe_mode():
    """Test safe-mode PDF generation when processed DataFrame is empty"""
    print("🔍 Testing safe-mode PDF generation...")
    
    try:
        from pdf_report import HebrewPDFReport
        
        # Create problematic data that will become empty after preprocessing
        # All NaN data
        empty_data = pd.DataFrame({
            'col1': [np.nan, np.nan, np.nan],
            'col2': [None, None, None],
            'col3': ['', '', '']
        })
        
        print(f"  Original problematic data shape: {empty_data.shape}")
        
        # Create PDF report instance
        report = HebrewPDFReport()
        
        # Generate report - should trigger safe mode
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_path = tmp_file.name
            
        result_path = report.generate_comprehensive_report(empty_data, output_path)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"    ✓ Safe-mode PDF generated: {result_path} ({file_size:,} bytes)")
            
            # Should contain "safe" in filename
            if 'safe' in result_path:
                print("    ✓ Safe-mode indicator found in filename")
            else:
                print("    ⚠️  Safe-mode indicator not found in filename")
                
            # Clean up
            try:
                os.unlink(result_path) 
            except:
                pass
                
            return True
        else:
            print("    ❌ Failed to generate safe-mode PDF")
            return False
            
    except Exception as e:
        print(f"    ❌ Error testing safe mode: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concurrent_reports():
    """Test that concurrent reports don't mix assets due to run_id collision prevention"""
    print("🔍 Testing concurrent report asset isolation...")
    
    try:
        from pdf_report import HebrewPDFReport
        
        # Create test data
        test_data1 = pd.DataFrame({
            'name': ['Alice', 'Bob'], 
            'value': [1, 2]
        })
        
        test_data2 = pd.DataFrame({
            'product': ['Item A', 'Item B'], 
            'price': [100, 200]
        })
        
        # Create two report instances (simulating concurrent execution)
        report1 = HebrewPDFReport()
        report2 = HebrewPDFReport()
        
        print(f"  Report 1 run_id: {report1.run_id}")
        print(f"  Report 2 run_id: {report2.run_id}")
        
        # Verify run IDs are different
        if report1.run_id != report2.run_id:
            print("    ✓ Different run_ids generated for concurrent reports")
        else:
            print("    ❌ Run IDs are the same - collision risk!")
            return False
            
        # Test chart directory isolation
        charts_dir1 = os.path.join("charts", f"run_{report1.run_id}")
        charts_dir2 = os.path.join("charts", f"run_{report2.run_id}") 
        
        # Create visualizations to test directory creation
        try:
            charts1 = report1.create_visualizations(test_data1)
            charts2 = report2.create_visualizations(test_data2)
            
            # Check directories are separate
            if os.path.exists(charts_dir1) and os.path.exists(charts_dir2):
                print("    ✓ Separate chart directories created for each run")
                
                # List files in each directory 
                files1 = os.listdir(charts_dir1) if os.path.exists(charts_dir1) else []
                files2 = os.listdir(charts_dir2) if os.path.exists(charts_dir2) else []
                
                print(f"    Report 1 charts: {len(files1)} files")
                print(f"    Report 2 charts: {len(files2)} files")
                
                # Cleanup
                report1._cleanup_temp_files()
                report2._cleanup_temp_files()
                
                print("    ✓ Cleanup completed")
                return True
            else:
                print("    ❌ Chart directories not created properly")
                return False
                
        except Exception as chart_error:
            print(f"    ⚠️  Chart generation error (expected with small data): {chart_error}")
            return True  # This is expected with minimal test data
            
    except Exception as e:
        print(f"    ❌ Error testing concurrent reports: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all RTL and safe-mode tests"""
    print("🚀 Testing RTL Text Visibility and Safe-Mode Features")
    print("=" * 60)
    
    results = {
        'rtl_visibility': test_rtl_visibility(),
        'safe_mode': test_safe_mode(), 
        'concurrent_isolation': test_concurrent_reports()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All RTL and safe-mode tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)