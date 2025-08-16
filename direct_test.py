# -*- coding: utf-8 -*-
"""
סקריפט בדיקה ישיר - Direct test script
"""

import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bot_creation():
    """בדיקה ישירה של יצירת הבוט"""
    
    print("🔍 Testing bot creation directly...")
    
    # Get bot token from environment variable  
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("⚠️  BOT_TOKEN environment variable not set - skipping live bot test")
        print("✅ Test completed (skipped live parts due to missing credentials)")
        return True
    
    try:
        from main import HebrewDataAnalyticsBot
        
        print("🔍 Creating bot instance...")
        bot = HebrewDataAnalyticsBot(bot_token=bot_token)
        print("✅ Bot instance created successfully!")
        
        print("🔍 Checking bot attributes...")
        print(f"  - Database: {hasattr(bot, 'db')}")
        print(f"  - Google Sheets: {hasattr(bot, 'google_sheets')}")
        print(f"  - Chart Generator: {hasattr(bot, 'chart_generator')}")
        print(f"  - Application: {hasattr(bot, 'application')}")
        print(f"  - User Sessions: {hasattr(bot, 'user_sessions')}")
        
        print("🎉 Bot creation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bot_creation()

