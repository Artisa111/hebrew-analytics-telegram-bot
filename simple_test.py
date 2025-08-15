# -*- coding: utf-8 -*-
"""
סקריפט בדיקה פשוט - Simple test script
"""

import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_step_by_step():
    """בדיקה שלב אחר שלב"""
    
    print("🔍 Step 1: Testing imports...")
    try:
        from database import DatabaseManager
        print("✅ Database import OK")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from google_sheets import get_google_sheets_manager
        print("✅ Google Sheets import OK")
    except Exception as e:
        print(f"❌ Google Sheets import failed: {e}")
        return False
    
    try:
        from visualization import get_chart_generator
        print("✅ Visualization import OK")
    except Exception as e:
        print(f"❌ Visualization import failed: {e}")
        return False
    
    print("🔍 Step 2: Testing database...")
    try:
        db = DatabaseManager()
        print("✅ Database created OK")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False
    
    print("🔍 Step 3: Testing Google Sheets...")
    try:
        gs = get_google_sheets_manager()
        print("✅ Google Sheets manager created OK")
    except Exception as e:
        print(f"❌ Google Sheets manager creation failed: {e}")
        return False
    
    print("🔍 Step 4: Testing Chart Generator...")
    try:
        cg = get_chart_generator()
        print("✅ Chart generator created OK")
    except Exception as e:
        print(f"❌ Chart generator creation failed: {e}")
        return False
    
    print("🔍 Step 5: Testing main bot class...")
    try:
        from main import HebrewDataAnalyticsBot
        print("✅ Main bot class import OK")
    except Exception as e:
        print(f"❌ Main bot class import failed: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    test_step_by_step()

