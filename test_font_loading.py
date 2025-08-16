#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Hebrew font loading functionality
"""

import os
import logging
import sys

# Add current directory to path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_font_loading():
    """Test the Hebrew font loading system"""
    try:
        from pdf_report import HebrewPDFReport
        
        print("Testing Hebrew font loading system...")
        
        # Create a PDF report instance
        report = HebrewPDFReport()
        
        print("Font loading test completed. Check logs above for details.")
        
        # Test creating a simple title page to verify fonts work
        print("Testing title page creation with Hebrew text...")
        report.create_title_page(
            title="בדיקת טעינת פונטים עבריים",
            subtitle="מערכת ניתוח נתונים",
            company="חברת הבדיקות"
        )
        
        # Save a test PDF
        test_pdf_path = "font_test.pdf"
        report.pdf.output(test_pdf_path)
        
        if os.path.exists(test_pdf_path):
            print(f"✓ Test PDF created successfully: {test_pdf_path}")
            print("Hebrew text should be visible in the PDF if fonts loaded correctly.")
        else:
            print("✗ Failed to create test PDF")
            
        return True
        
    except Exception as e:
        print(f"✗ Font loading test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_font_loading()
    sys.exit(0 if success else 1)