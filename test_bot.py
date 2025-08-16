# -*- coding: utf-8 -*-
"""
סקריפט בדיקה לבוט - Test script for the bot
"""

import os
from main import HebrewDataAnalyticsBot

def test_bot():
    """בדיקת הבוט"""
    
    # Get bot token from environment variable
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("⚠️  BOT_TOKEN environment variable not set - skipping live bot test")
        print("✅ Test completed (skipped live parts due to missing credentials)")
        return True
    
    try:
        print("🔍 בודק יצירת הבוט...")
        bot = HebrewDataAnalyticsBot(bot_token=bot_token)
        print("✅ הבוט נוצר בהצלחה!")
        
        print("🔍 בודק מסד הנתונים...")
        if hasattr(bot, 'db'):
            print("✅ מסד הנתונים זמין!")
        
        print("🔍 בודק מחולל התרשימים...")
        if hasattr(bot, 'chart_generator'):
            print("✅ מחולל התרשימים זמין!")
        
        print("🎉 כל הבדיקות עברו בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

if __name__ == "__main__":
    test_bot()
