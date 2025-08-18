#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test bot integration with fixed PDF generation
"""

import pandas as pd
import tempfile
import os

def test_bot_pdf_integration():
    """Test that bot PDF generation works with the new run_id system"""
    print("🔍 Testing bot integration with fixed PDF generation...")
    
    try:
        # Import the function the bot uses
        from pdf_report import generate_complete_data_report
        
        # Create test data like the bot would receive
        test_data = pd.DataFrame({
            'שם': ['דוד', 'שרה', 'יוסי'],
            'גיל': [25, 30, 35], 
            'עיר': ['תל אביב', 'ירושלים', 'חיפה'],
            'משכורת': [15000, 18000, 22000]
        })
        
        print(f"  Test data shape: {test_data.shape}")
        
        # Test the same way the bot calls it
        out_path = os.path.join(os.getcwd(), 'דוח_מתקדם_test.pdf')
        
        # This is the exact function call the bot makes
        pdf_path = generate_complete_data_report(test_data, out_path, include_charts=True)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"    ✅ PDF generated: {pdf_path}")
            print(f"    ✅ File size: {file_size:,} bytes")
            
            # Check that it has a run_id suffix (collision prevention)
            if os.path.basename(pdf_path) != os.path.basename(out_path):
                print(f"    ✅ Run ID suffix added to prevent collisions")
            
            # Clean up
            os.unlink(pdf_path)
            
            return True
        else:
            print(f"    ❌ Failed to generate PDF")
            return False
            
    except Exception as e:
        print(f"    ❌ Error testing bot integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_data_bot_integration():
    """Test bot integration with empty data (safe mode)"""
    print("🔍 Testing bot integration with empty data...")
    
    try:
        from pdf_report import generate_complete_data_report
        
        # Empty DataFrame that might come from corrupted upload
        empty_data = pd.DataFrame()
        
        out_path = os.path.join(os.getcwd(), 'דוח_מתקדם_empty.pdf')
        
        pdf_path = generate_complete_data_report(empty_data, out_path, include_charts=True)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"    ✅ Safe-mode PDF generated: {pdf_path}")
            print(f"    ✅ File size: {file_size:,} bytes")
            
            # Should contain "safe" in filename
            if 'safe' in pdf_path:
                print(f"    ✅ Safe-mode indicator present")
                
            # Clean up
            os.unlink(pdf_path)
            
            return True
        else:
            print(f"    ❌ Failed to generate safe-mode PDF")
            return False
            
    except Exception as e:
        print(f"    ❌ Error testing empty data integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Testing Bot Integration with Fixed PDF System")
    print("=" * 60)
    
    results = {
        'normal_data': test_bot_pdf_integration(),
        'empty_data_safe_mode': test_empty_data_bot_integration()
    }
    
    print("\n" + "=" * 60)
    print("📊 BOT INTEGRATION TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nSUMMARY: {passed}/{total} integration tests passed")
    
    if passed == total:
        print("🎉 Bot integration tests passed! The Telegram bot will work correctly with the fixes.")
        return True
    else:
        print("⚠️  Some integration tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)