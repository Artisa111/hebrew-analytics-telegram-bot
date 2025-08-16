# -*- coding: utf-8 -*-
"""
סקריפט הפעלה לבוט - Bot launch script
"""

import os
from main import HebrewDataAnalyticsBot

def main():
    """הפונקציה הראשית להפעלת הבוט"""
    
    # Get bot token from environment variable
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN environment variable not set!")
        print("📱 Get your token from @BotFather in Telegram")
        print("🔧 Set the BOT_TOKEN environment variable:")
        print("   export BOT_TOKEN='your_bot_token_here'  # Linux/Mac")
        print("   $env:BOT_TOKEN='your_bot_token_here'    # Windows PowerShell")
        return
    
    try:
        print("🚀 Starting the bot...")
        print("📱 Token loaded from environment, creating bot instance...")
        
        # Create and run the bot
        bot = HebrewDataAnalyticsBot(bot_token=BOT_TOKEN)
        print("✅ Bot created successfully!")
        print("🔄 Starting the bot...")
        print("📱 Now find the bot in Telegram and send /start")
        
        # Run the bot
        bot.run()
        
    except Exception as e:
        print(f"❌ Error starting the bot: {e}")
        print("🔧 Check your settings and try again")

if __name__ == "__main__":
    main()
