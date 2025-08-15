#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט בדיקת התקנה - Installation test script
בודק שכל החבילות הנדרשות הותקנו כראוי
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """בדיקת ייבוא מודול"""
    try:
        if package_name:
            importlib.import_module(module_name)
            print(f"✅ {package_name} - OK")
            return True
        else:
            importlib.import_module(module_name)
            print(f"✅ {module_name} - OK")
            return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def main():
    """הפונקציה הראשית"""
    print("🔍 בודק התקנת חבילות...")
    print("=" * 50)
    
    # רשימת החבילות לבדיקה
    packages = [
        ("telegram", "python-telegram-bot"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("plotly", "plotly"),
        ("gspread", "gspread"),
        ("oauth2client", "oauth2client"),
        ("fpdf", "fpdf2"),
        ("openpyxl", "openpyxl"),
        ("PIL", "Pillow"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
        ("sklearn", "scikit-learn"),
    ]
    
    # בדיקת כל החבילות
    failed_packages = []
    for module, package in packages:
        if not test_import(module, package):
            failed_packages.append(package)
    
    print("=" * 50)
    
    if failed_packages:
        print(f"❌ {len(failed_packages)} חבילות נכשלו:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 פתרון:")
        print("הרץ: pip install -r requirements.txt")
        return False
    else:
        print("🎉 כל החבילות הותקנו בהצלחה!")
        print("הבוט מוכן להפעלה!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

