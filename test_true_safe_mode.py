#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test true safe-mode with completely empty DataFrame
"""

import pandas as pd
import numpy as np
import tempfile
import os

def test_true_safe_mode():
    """Test safe-mode with truly empty DataFrame"""
    from pdf_report import HebrewPDFReport
    
    # Create completely invalid data that will be empty after preprocessing
    truly_empty_data = pd.DataFrame({
        'invalid': [np.nan, '', None],
        'also_invalid': [None, np.nan, ''],
        'still_invalid': ['', None, np.nan]
    })
    
    print(f"Original data:\n{truly_empty_data}")
    print(f"All values null?: {truly_empty_data.isnull().all().all()}")
    
    # Test preprocessing manually first
    from preprocess import preprocess_df
    processed = preprocess_df(truly_empty_data)
    print(f"After preprocessing: {processed.shape if processed is not None else 'None'}")
    print(f"Is empty?: {processed.empty if processed is not None else 'None'}")
    
    # Now test report generation
    report = HebrewPDFReport()
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        output_path = tmp_file.name
        
    result_path = report.generate_comprehensive_report(truly_empty_data, output_path)
    
    if result_path and os.path.exists(result_path):
        print(f"✅ Report generated: {result_path}")
        print(f"File size: {os.path.getsize(result_path)} bytes")
        
        if 'safe' in result_path:
            print("✅ Safe-mode activated!")
        else:
            print("⚠️ Regular mode (data not completely empty after preprocessing)")
        
        # Cleanup
        os.unlink(result_path)
        return True
    else:
        print("❌ Failed to generate report")
        return False

if __name__ == "__main__":
    test_true_safe_mode()