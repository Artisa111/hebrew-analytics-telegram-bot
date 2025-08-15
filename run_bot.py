# -*- coding: utf-8 -*-
"""
סקריפט הפעלה לבוט - Bot launch script
"""

import os
from main import HebrewDataAnalyticsBot

def main():
    """הפונקציה הראשית להפעלת הבוט"""
    
    # ⚠️ ВАЖНО: Замените на ваш настоящий токен от @BotFather
    # ⚠️ IMPORTANT: Replace with your real token from @BotFather
    BOT_TOKEN = "8418603857:AAGoqw3LGd5yRggjNUiNc-4_DcWHNq2Ucdo"
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or BOT_TOKEN == "":
        print("❌ ОШИБКА: Установите ваш токен бота в переменной BOT_TOKEN!")
        print("📱 Получите токен у @BotFather в Telegram")
        print("🔧 Отредактируйте файл run_bot.py и вставьте токен")
        return
    
    try:
        print("🚀 Запускаю бота...")
        print("📱 Токен установлен, создаю экземпляр бота...")
        
        # Устанавливаем токен в переменные окружения
        os.environ['BOT_TOKEN'] = BOT_TOKEN
        
        # Создаем и запускаем бота
        bot = HebrewDataAnalyticsBot(bot_token=BOT_TOKEN)
        print("✅ Бот создан успешно!")
        print("🔄 Запускаю бота...")
        print("📱 Теперь найдите бота в Telegram и отправьте /start")
        
        # Запускаем бота
        bot.run()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        print("🔧 Проверьте настройки и попробуйте снова")

if __name__ == "__main__":
    main()
