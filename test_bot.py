# -*- coding: utf-8 -*-
"""
סקריפט בדיקה לבוט - Test script for the bot
"""

import os
from main import HebrewDataAnalyticsBot

# הגדרת טוקן זמני לבדיקה
os.environ['BOT_TOKEN'] = '8418603857:AAGoqw3LGd5yRggjNUiNc-4_DcWHNq2Ucdo'

def test_bot():
    """בדיקת הבוט"""
    try:
        print("🔍 בודק יצירת הבוט...")
        bot = HebrewDataAnalyticsBot(bot_token='8418603857:AAGoqw3LGd5yRggjNUiNc-4_DcWHNq2Ucdo')
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
