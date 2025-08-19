# -*- coding: utf-8 -*-
"""
בוט פשוט לבדיקה - Simple bot for testing with advanced PDF generation
"""

# Initialize logging before other imports
from logging_config import setup_logging
logger = setup_logging()

import os
import pandas as pd
import numpy as np
import tempfile
import shutil
import matplotlib
# Enforce headless backend before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
from pdf_report import generate_complete_data_report

# Setup logging
logger.info("Simple Hebrew Bot starting with advanced PDF generation")

# Настройка matplotlib для поддержки иврита
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

class SimpleHebrewBot:
    def __init__(self, bot_token: str):
        self.application = Application.builder().token(bot_token).job_queue(None).persistence(None).build()
        self.user_data = {}  # Простое хранилище данных пользователей
        self.setup_handlers()
    
    def setup_handlers(self):
        """הגדרת handlers פשוטים"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        # Добавляем обработчик файлов
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פקודת start פשוטה"""
        user = update.effective_user
        user_id = user.id
        
        # Инициализируем данные пользователя
        self.user_data[user_id] = {
            'data': None,
            'file_name': None,
            'analysis_done': False
        }
        
        welcome_text = f"ברוך הבא {user.first_name}! 🎉\n\nאני בוט ניתוח נתונים בעברית.\n\n📁 שלח לי קובץ CSV או Excel כדי להתחיל!"
        
        keyboard = [
            ['📊 ניתוח נתונים'],
            ['📈 תרשימים'],
            ['💡 תובנות והמלצות'],
            ['📄 דוח PDF', '📊 דוח PDF מתקדם'],  # שתי אפשרויות PDF
            ['📁 העלאת קובץ'],
            ['❓ עזרה']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פקודת help פשוטה"""
        help_text = """
📚 **עזרה - בוט ניתוח נתונים בעברית**

**פקודות זמינות:**
/start - התחלת שימוש בבוט
/help - הצגת עזרה זו

**יכולות הבוט:**
• 📁 העלאת קבצי CSV ו-Excel
• 📊 ניתוח נתונים מקיף
• 📈 יצירת תרשימים מקצועיים
• 💡 תובנות אוטומטיות והמלצות
• 🔍 זיהוי דפוסים ואנומליות
• 📄 דוחות PDF בעברית (רגיל ומתקדם)

**איך להשתמש:**
1. שלח לי קובץ CSV או Excel
2. בחר "ניתוח נתונים" לניתוח מקיף
3. בחר "תרשימים" ליצירת גרפים
4. בחר "תובנות והמלצות" לקבלת תובנות
5. בחר "דוח PDF מתקדם" לדוח מקצועי בעברית

**דוח PDF מתקדם מכיל:**
• ניתוח מעמיק של הנתונים
• גרפים מקצועיים
• תובנות ומסקנות
• המלצות מותאמות אישית
• עיצוב מקצועי בעברית מימין לשמאל

**לשאלות נוספות, פנה למפתח הבוט.**
        """
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    def has_data(self, user_id: int) -> bool:
        """Проверяет, есть ли данные у пользователя"""
        if user_id not in self.user_data:
            return False
        data = self.user_data[user_id].get('data')
        return data is not None and isinstance(data, pd.DataFrame) and not data.empty
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בקבצים שהועלו"""
        user_id = update.effective_user.id
        document = update.message.document
        
        # Проверяем, есть ли пользователь в данных
        if user_id not in self.user_data:
            self.user_data[user_id] = {'data': None, 'file_name': None, 'analysis_done': False}
        
        # Проверяем тип файла
        file_name = document.file_name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        supported_formats = ['.csv', '.xlsx', '.xls']
        if file_extension not in supported_formats:
            await update.message.reply_text(
                f"❌ סוג קובץ לא נתמך: {file_extension}\n\nהקבצים הנתמכים: {', '.join(supported_formats)}"
            )
            return
        
        # Проверяем размер файла (максимум 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if document.file_size > max_size:
            await update.message.reply_text(
                f"❌ הקובץ גדול מדי: {document.file_size // (1024*1024)}MB\n\nהגודל המקסימלי: 50MB"
            )
            return
        
        await update.message.reply_text("📁 קובץ התקבל! מעבד...")
        
        try:
            # Скачиваем файл
            file = await context.bot.get_file(document.file_id)
            
            # Создаем временную папку
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file_name)
            
            # Скачиваем файл
            await file.download_to_drive(file_path)
            
            # Читаем файл
            df = await self.read_data_file(file_path, file_extension)
            
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                # Сохраняем данные пользователя
                self.user_data[user_id].update({
                    'data': df,
                    'file_name': file_name,
                    'analysis_done': False
                })
                
                # Показываем информацию о файле
                rows, cols = df.shape
                await update.message.reply_text(
                    f"✅ הקובץ עובד בהצלחה!\n\n"
                    f"📊 מידע על הקובץ:\n"
                    f"• שם: {file_name}\n"
                    f"• שורות: {rows:,}\n"
                    f"• עמודות: {cols}\n"
                    f"• גודל: {document.file_size // 1024}KB\n\n"
                    f"עכשיו אתה יכול לבחור:\n"
                    f"• 'ניתוח נתונים' - לניתוח מפורט\n"
                    f"• 'תרשימים' - ליצירת גרפים\n"
                    f"• 'תובנות והמלצות' - לקבלת תובנות\n"
                    f"• 'דוח PDF מתקדם' - לדוח מקצועי בעברית! 🎯"
                )
                
                # Показываем первые несколько строк (коротко)
                preview = df.head(2).to_string(index=False, max_cols=3)
                if len(preview) > 1000:
                    preview = preview[:1000] + "..."
                await update.message.reply_text(f"👀 תצוגה מקדימה:\n```\n{preview}\n```", parse_mode=ParseMode.MARKDOWN)
                
            else:
                await update.message.reply_text("❌ שגיאה בקריאת הקובץ. אנא ודא שהקובץ תקין ולא ריק.")
            
        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await update.message.reply_text("❌ שגיאה בעיבוד הקובץ. אנא נסה שוב.")
        
        finally:
            # Очищаем временную папку
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def read_data_file(self, file_path: str, file_extension: str):
        """קריאת קובץ נתונים"""
        try:
            if file_extension == '.csv':
                # Пробуем разные кодировки
                encodings = ['utf-8', 'latin-1', 'cp1255', 'iso-8859-8']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        if isinstance(df, pd.DataFrame) and not df.empty:
                            return df
                    except UnicodeDecodeError:
                        continue
                return None
            
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בהודעות טקסט פשוטות"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Проверяем, есть ли пользователь в данных
        if user_id not in self.user_data:
            self.user_data[user_id] = {'data': None, 'file_name': None, 'analysis_done': False}
        
        if text == '📊 ניתוח נתונים':
            await self.handle_analyze_data(update, context)
        
        elif text == '📈 תרשימים':
            await self.handle_charts(update, context)
        
        elif text == '💡 תובנות והמלצות':
            await self.handle_insights(update, context)

        elif text == '📄 דוח PDF':
            # דוח PDF רגיל (ישן)
            if not self.has_data(user_id):
                await update.message.reply_text("❌ אין נתונים לדוח! שלח קובץ תחילה.")
                return
            
            await update.message.reply_text("🖨️ יוצר דוח PDF רגיל בעברית…")
            
            try:
                df = self.user_data[user_id]['data']
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                analysis_results = {
                    'basic_info': {
                        'shape': df.shape,
                        'memory_usage': df.memory_usage(deep=True).sum(),
                        'null_counts': df.isnull().sum().to_dict(),
                    }
                }
                # quick top correlations for report
                if len(numeric_cols) > 1:
                    analysis_results['correlation_matrix'] = df[numeric_cols].corr()
                
                # reuse last charts if exist; otherwise, build minimal hist for first numeric
                chart_dir = os.path.join(os.getcwd(), 'temp_charts')
                chart_files = []
                if os.path.isdir(chart_dir):
                    for name in os.listdir(chart_dir):
                        if name.lower().endswith('.png'):
                            chart_files.append(os.path.join(chart_dir, name))
                
                if not chart_files and len(numeric_cols) > 0:
                    import matplotlib.pyplot as plt
                    path = os.path.join(chart_dir, 'pdf_quick_hist.png')
                    os.makedirs(chart_dir, exist_ok=True)
                    plt.hist(df[numeric_cols[0]].dropna(), bins=25)
                    plt.title(str(numeric_cols[0]))
                    plt.savefig(path, dpi=200)
                    plt.close()
                    chart_files.append(path)

                out_path = os.path.join(os.getcwd(), 'analysis_report.pdf')
                pdf_path = generate_complete_data_report(df, out_path, include_charts=True)
                
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id, 
                            document=f, 
                            filename=os.path.basename(pdf_path), 
                            caption='דוח PDF רגיל הוכן בהצלחה! 📄'
                        )
                else:
                    await update.message.reply_text('❌ שגיאה ביצירת הדוח הרגיל')
                    
            except Exception as e:
                logger.error(f"Error sending regular PDF: {e}")
                await update.message.reply_text('❌ שגיאה ביצירת הדוח הרגיל')

        elif text == '📊 דוח PDF מתקדם':
            # דוח PDF מתקדם (חדש ומשופר)
            if not self.has_data(user_id):
                await update.message.reply_text("❌ אין נתונים לדוח מתקדם! שלח קובץ תחילה.")
                return
            
            await update.message.reply_text("🚀 יוצר דוח PDF מתקדם בעברית עם ניתוח מקיף, גרפים מקצועיים ותוכן מובטח בכל סעיף…")
            
            try:
                df = self.user_data[user_id]['data']
                file_name = self.user_data[user_id]['file_name']
                
                # יצירת שם קובץ מותאם
                base_name = os.path.splitext(file_name)[0] if file_name else "נתונים"
                out_path = os.path.join(os.getcwd(), f'דוח_מתקדם_{base_name}.pdf')
                
                # שימוש בפונקציה החדשה והמשופרת עם תוכן מובטח
                pdf_path = generate_complete_data_report(df, out_path, include_charts=True)
                
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id, 
                            document=f, 
                            filename=os.path.basename(pdf_path), 
                            caption='🎉 דוח PDF מתקדם עם תוכן מובטח הוכן בהצלחה!\n\n'
                                   '✨ הדוח כולל:\n'
                                   '• ניתוח מעמיק של הנתונים עם תוכן מובטח\n'
                                   '• גרפים מקצועיים וויזואליזציות איכותיות\n'
                                   '• תובנות ומסקנות אוטומטיות מפורטות\n'
                                   '• המלצות מותאמות אישית עם הסברים\n'
                                   '• ניתוח ערכים חריגים וקורלציות\n'
                                   '• סיכום סטטיסטי מקיף\n'
                                   '• עיצוב מקצועי בעברית מימין לשמאל\n'
                                   '• תוכן מובטח בכל סעיף - אף סעיף לא יישאר ריק!'
                        )
                    
                    # הודעת מעקב
                    await update.message.reply_text(
                        "🎯 **דוח PDF מתקדם עם תוכן מובטח נוצר בהצלחה!**\n\n"
                        "🔥 **חידושים בדוח החדש:**\n"
                        "✅ תוכן מובטח בכל סעיף - אף סעיף לא נשאר ריק\n"
                        "📊 ניתוח סטטיסטי מלא עם הסברים מפורטים\n"
                        "📈 גרפים מקצועיים עם תיאורים בעברית\n"
                        "🔍 זיהוי קורלציות וחריגים עם המלצות\n"
                        "💡 תובנות עסקיות מותאמות אישית\n"
                        "🎨 עיצוב מקצועי בעברית מימין לשמאל\n"
                        "🛡️ עמידות מול נתונים בעייתיים\n\n"
                        "🚀 זהו דוח מתקדם ומקצועי שמבטיח תוכן איכותי בכל מקרה!",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
                else:
                    await update.message.reply_text('❌ שגיאה ביצירת הדוח המתקדם')
                    
            except Exception as e:
                logger.error(f"Error sending advanced PDF: {e}")
                await update.message.reply_text('❌ שגיאה ביצירת הדוח המתקדם')
        
        elif text == '📁 העלאת קובץ':
            await update.message.reply_text(
                "📁 **העלאת קבצים**\n\n"
                "שלח לי קובץ CSV או Excel כדי להתחיל!\n\n"
                "**קבצים נתמכים:**\n"
                "• CSV (.csv)\n"
                "• Excel (.xlsx, .xls)\n\n"
                "**מגבלות:**\n"
                "• גודל מקסימלי: 50MB\n"
                "• מספר שורות: ללא הגבלה\n"
                "• מספר עמודות: ללא הגבלה\n\n"
                "**טיפים:**\n"
                "• וודא שהקובץ מכיל כותרות עמודות\n"
                "• בדוק שאין שורות ריקות בתחילת הקובץ\n"
                "• השתמש בקידוד UTF-8 לתמיכה בעברית",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif text == '❓ עזרה':
            await self.help_command(update, context)
        
        else:
            await update.message.reply_text(
                "לא הבנתי את ההודעה שלך. 🤔\n\n"
                "אנא השתמש בכפתורים שלמטה או שלח /help לעזרה מפורטת.\n\n"
                "💡 אם יש לך קובץ נתונים - פשוט שלח אותו לי!"
            )
    
    async def handle_analyze_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בניתוח נתונים"""
        user_id = update.effective_user.id
        
        if not self.has_data(user_id):
            await update.message.reply_text(
                "❌ אין נתונים לניתוח!\n\n"
                "אנא שלח לי קובץ CSV או Excel תחילה."
            )
            return
        
        await update.message.reply_text("🔍 מנתח נתונים...")
        
        try:
            df = self.user_data[user_id]['data']
            
            # Базовый анализ
            analysis_text = f"🔍 **ניתוח מפורט: {self.user_data[user_id]['file_name']}**\n\n"
            
            # Основная информация
            rows, cols = df.shape
            analysis_text += f"📊 **מידע בסיסי:**\n"
            analysis_text += f"• מספר שורות: {rows:,}\n"
            analysis_text += f"• מספר עמודות: {cols}\n"
            analysis_text += f"• שם קובץ: {self.user_data[user_id]['file_name']}\n\n"
            
            # Информация о колонках
            analysis_text += f"**עמודות וטיפוסי נתונים:**\n"
            for i, col in enumerate(df.columns, 1):
                col_type = str(df[col].dtype)
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                analysis_text += f"{i}. {col} ({col_type})"
                if null_count > 0:
                    null_percentage = (null_count / len(df)) * 100
                    analysis_text += f" - {null_count} ערכים חסרים ({null_percentage:.1f}%)"
                analysis_text += f" - {unique_count} ערכים ייחודיים\n"
            
            # Детальная статистика для числовых колонок
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis_text += f"\n📊 **סטטיסטיקה מספרית מפורטת:**\n"
                for col in numeric_cols:
                    stats = df[col].describe()
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    analysis_text += f"\n**{col}:**\n"
                    analysis_text += f"• ממוצע: {stats['mean']:.2f}\n"
                    analysis_text += f"• חציון: {stats['50%']:.2f}\n"
                    analysis_text += f"• סטיית תקן: {stats['std']:.2f}\n"
                    analysis_text += f"• מינימום: {stats['min']:.2f}\n"
                    analysis_text += f"• מקסימום: {stats['max']:.2f}\n"
                    analysis_text += f"• Q1: {Q1:.2f}\n"
                    analysis_text += f"• Q3: {Q3:.2f}\n"
            
            # Анализ категориальных колонок
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                analysis_text += f"\n**ניתוח קטגוריות:**\n"
                for col in categorical_cols[:3]:  # Только первые 3
                    value_counts = df[col].value_counts()
                    most_common = value_counts.head(3)
                    analysis_text += f"• {col}:\n"
                    for val, count in most_common.items():
                        percentage = (count / len(df)) * 100
                        analysis_text += f"  - {val}: {count} ({percentage:.1f}%)\n"
            
            # Проверка на дубликаты
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                analysis_text += f"\n**⚠️ אזהרות:**\n"
                analysis_text += f"• נמצאו {duplicates} שורות כפולות\n"
            
            # Анализ качества данных
            total_cells = len(df) * len(df.columns)
            total_nulls = df.isnull().sum().sum()
            if total_nulls > 0:
                null_percentage = (total_nulls / total_cells) * 100
                analysis_text += f"\n**🔍 איכות נתונים:**\n"
                analysis_text += f"• ערכים חסרים: {total_nulls:,} ({null_percentage:.1f}% מהנתונים)\n"
                if null_percentage > 20:
                    analysis_text += f"  - ⚠️ אחוז גבוה של ערכים חסרים - שקול לבדוק את מקור הנתונים\n"
                elif null_percentage > 10:
                    analysis_text += f"  - ⚠️ אחוז בינוני של ערכים חסרים - ייתכן שיידרש טיפול\n"
                else:
                    analysis_text += f"  - ✅ אחוז נמוך של ערכים חסרים - נתונים באיכות טובה\n"
            
            self.user_data[user_id]['analysis_done'] = True
            
            # Разбиваем длинное сообщение
            if len(analysis_text) > 4000:
                parts = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text(f"📊 המשך הניתוח (חלק {i+1}):\n\n{part}", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(analysis_text, parse_mode=ParseMode.MARKDOWN)
            
            await update.message.reply_text(
                "✅ הניתוח הושלם!\n\n"
                "**מה עכשיו?**\n"
                "📈 'תרשימים' - ליצירת גרפים מקצועיים\n"
                "💡 'תובנות והמלצות' - לקבלת תובנות מתקדמות\n"
                "📊 'דוח PDF מתקדם' - לדוח מקצועי מלא! 🎯",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            await update.message.reply_text("❌ שגיאה בניתוח הנתונים")
    
    async def handle_charts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בתרשימים - יצירת תרשימים מקצועיים ומתקדמים"""
        user_id = update.effective_user.id
        
        if not self.has_data(user_id):
            await update.message.reply_text(
                "❌ אין נתונים לתרשימים!\n\n"
                "אנא שלח לי קובץ CSV או Excel תחילה."
            )
            return
        
        await update.message.reply_text("📈 יוצר תרשימים מקצועיים...")
        
        try:
            df = self.user_data[user_id]['data']
            chart_files = []
            chart_insights = {}
            chart_next_steps = {}
            
            # Создаем папку для графиков
            temp_charts_dir = tempfile.mkdtemp()
            
            # Настройка стиля для профессиональных графиков
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # 1. Гистограммы с улучшенным дизайном
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                for col in numeric_cols[:3]:  # Первые 3 числовые колонки
                    plt.figure(figsize=(12, 8))
                    
                    # Создаем подграфики
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
                    
                    # Гистограмма
                    ax1.hist(df[col].dropna(), bins=30, alpha=0.7, color='skyblue', 
                            edgecolor='navy', linewidth=1.2)
                    ax1.set_title(f'היסטוגרמה של {col}', fontsize=16, fontweight='bold', pad=20)
                    ax1.set_xlabel(col, fontsize=12, fontweight='bold')
                    ax1.set_ylabel('תדירות', fontsize=12, fontweight='bold')
                    ax1.grid(True, alpha=0.3, linestyle='--')
                    ax1.axvline(df[col].mean(), color='red', linestyle='--', linewidth=2, 
                               label=f'ממוצע: {df[col].mean():.2f}')
                    ax1.axvline(df[col].median(), color='green', linestyle='--', linewidth=2, 
                               label=f'חציון: {df[col].median():.2f}')
                    ax1.legend(fontsize=10)
                    
                    # Box plot
                    ax2.boxplot(df[col].dropna(), patch_artist=True, 
                               boxprops=dict(facecolor='lightblue', alpha=0.7),
                               medianprops=dict(color='red', linewidth=2))
                    ax2.set_title(f'Box Plot של {col}', fontsize=14, fontweight='bold')
                    ax2.set_ylabel(col, fontsize=12, fontweight='bold')
                    ax2.grid(True, alpha=0.3, linestyle='--')
                    
                    plt.tight_layout()
                    chart_path = os.path.join(temp_charts_dir, f'histogram_box_{col}.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()
                    chart_files.append(chart_path)

                    series = df[col].dropna()
                    if not series.empty:
                        mean_v = series.mean()
                        median_v = series.median()
                        std_v = series.std()
                        skew_v = series.skew()
                        q1 = series.quantile(0.25)
                        q3 = series.quantile(0.75)
                        iqr = q3 - q1
                        lower = q1 - 1.5 * iqr
                        upper = q3 + 1.5 * iqr
                        outliers = ((series < lower) | (series > upper)).sum()
                        out_pct = (outliers / len(series)) * 100.0
                        chart_insights[chart_path] = f"{col}: ממוצע {mean_v:.2f}, חציון {median_v:.2f}, סטיית תקן {std_v:.2f}, הטיה {skew_v:.2f}. חריגים: {out_pct:.1f}%"
                        chart_next_steps[chart_path] = (
                            "מה הלאה:\n"
                            "• בדיקת חריגים והשפעתם על המודלים\n"
                            "• אם |הטיה| גבוהה — שקלו טרנספורמציית Log/Box-Cox\n"
                            "• השוואת ההתפלגות בין קבוצות (A/B, סגמנטים)"
                        )
            
            # 2. Корреляционная матрица
            if len(numeric_cols) > 1:
                plt.figure(figsize=(12, 10))
                correlation_matrix = df[numeric_cols].corr()
                
                # Создаем маску для верхнего треугольника
                mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
                
                # Создаем heatmap
                sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdYlBu_r', 
                           center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                           fmt='.3f', annot_kws={'size': 10, 'weight': 'bold'})
                
                plt.title('מטריצת קורלציה - Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
                plt.tight_layout()
                
                chart_path = os.path.join(temp_charts_dir, 'correlation_matrix.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                chart_files.append(chart_path)

                # Insights
                pairs = []
                cols_list = list(numeric_cols)
                for i in range(len(cols_list)):
                    for j in range(i+1, len(cols_list)):
                        val = correlation_matrix.loc[cols_list[i], cols_list[j]]
                        if not pd.isna(val):
                            pairs.append((cols_list[i], cols_list[j], float(val)))
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                top_pairs = ', '.join([f"{a}↔{b} ({c:.2f})" for a, b, c in pairs[:3]]) if pairs else "אין קשרים חזקים"
                chart_insights[chart_path] = f"זוגות קורלציה בולטים: {top_pairs}"
                chart_next_steps[chart_path] = (
                    "מה הלאה:\n• בדיקת רגרסיה לזוגות חזקים\n• טיפול במולטיקולינאריות לפני ML"
                )
            
            # 3. Столбчатые диаграммы для категориальных данных
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                for col in categorical_cols[:2]:
                    series = df[col].dropna()
                    if series.empty:
                        continue
                    value_counts = series.value_counts()

                    # Detect high-cardinality columns and aggregate tail into 'Other'
                    unique_ratio = series.nunique() / len(series)
                    top_n = 10 if (unique_ratio > 0.3 or len(value_counts) > 12) else 15
                    value_counts = value_counts.sort_values(ascending=False)
                    others_sum = value_counts.iloc[top_n:].sum()
                    value_counts = value_counts.iloc[:top_n]
                    if others_sum > 0:
                        value_counts['אחר'] = others_sum

                    non_null_total = value_counts.sum()

                    plt.figure(figsize=(14, 8))
                    bars = plt.bar(range(len(value_counts)), value_counts.values,
                                 color=plt.cm.Set3(np.linspace(0, 1, len(value_counts))),
                                 alpha=0.8, edgecolor='black', linewidth=0.5)

                    # Добавляем значения на столбцы
                    for i, (bar, value) in enumerate(zip(bars, value_counts.values)):
                        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(value_counts.values),
                                f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=10)

                    plt.title(f'התפלגות {col}', fontsize=16, fontweight='bold', pad=20)
                    plt.xlabel(col, fontsize=12, fontweight='bold')
                    plt.ylabel('מספר', fontsize=12, fontweight='bold')
                    plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
                    plt.grid(True, alpha=0.3, linestyle='--', axis='y')

                    # Добавляем процентные метки
                    for i, (bar, value) in enumerate(zip(bars, value_counts.values)):
                        percentage = (value / non_null_total) * 100 if non_null_total else 0
                        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                                f'{percentage:.1f}%', ha='center', va='center',
                                fontweight='bold', color='white', fontsize=9)

                    plt.tight_layout()
                    chart_path = os.path.join(temp_charts_dir, f'bar_chart_{col}.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()
                    chart_files.append(chart_path)

                    top3 = value_counts.head(3)
                    coverage = (top3.sum() / non_null_total) * 100 if non_null_total else 0
                    dom = ', '.join([f"{k} ({v/non_null_total*100:.1f}%)" for k, v in top3.items()])
                    chart_insights[chart_path] = f"{col}: קטגוריות מובילות — {dom}. כיסוי טופ‑3: {coverage:.1f}%"
                    chart_next_steps[chart_path] = (
                        "מה הלאה:\n"
                        "• ניתוח עומק לפי קטגוריות מובילות\n"
                        "• המרת קטגוריות דלות נתונים ל-'אחר'\n"
                        "• בדיקת קשר ליעדי המרה/הכנסה"
                    )
            
            # Отправляем графики
            if chart_files:
                await update.message.reply_text(f"✅ נוצרו {len(chart_files)} תרשימים מקצועיים!")
                
                # Группируем графики по типам для лучшей организации
                chart_types = {
                    'histogram_box': '📊 היסטוגרמות ו-Box Plots',
                    'bar_chart': '📈 גרפים עמודות',
                    'correlation_matrix': '🔗 מטריצת קורלציה'
                }
                
                for i, chart_file in enumerate(chart_files):
                    try:
                        with open(chart_file, 'rb') as img_file:
                            # Определяем тип графика по имени файла
                            chart_type = "תרשים מקצועי"
                            for key, value in chart_types.items():
                                if key in chart_file:
                                    chart_type = value
                                    break
                            
                            insight_text = chart_insights.get(chart_file, "")
                            caption = f"📊 {chart_type}\n{insight_text}".strip()
                            if len(caption) > 900:
                                caption = caption[:900] + "…"
                            await context.bot.send_photo(
                                chat_id=update.effective_chat.id,
                                photo=img_file,
                                caption=caption
                            )
                            next_steps = chart_next_steps.get(chart_file)
                            if next_steps:
                                await context.bot.send_message(chat_id=update.effective_chat.id, text=next_steps)
                    except Exception as e:
                        logger.error(f"Error sending chart {chart_file}: {e}")
                        await update.message.reply_text(f"❌ שגיאה בשליחת תרשים {i+1}")
                
                await update.message.reply_text(
                    "🎉 כל התרשימים נשלחו!\n\n"
                    "💡 **סוגי התרשימים שנוצרו:**\n"
                    "• 📊 היסטוגרמות עם Box Plots\n"
                    "• 📈 גרפים עמודות עם אחוזים\n"
                    "• 🔗 מטריצת קורלציה מתקדמת\n\n"
                    "**מה עכשיו?**\n"
                    "💡 'תובנות והמלצות' - לקבלת תובנות עסקיות\n"
                    "📊 'דוח PDF מתקדם' - לדוח מקצועי עם כל הגרפים! 🎯"
                )
            else:
                await update.message.reply_text("❌ לא ניתן ליצור תרשימים מהנתונים הנוכחיים.")
            
        except Exception as e:
            logger.error(f"Error creating charts: {e}")
            await update.message.reply_text("❌ שגיאה ביצירת התרשימים")
        
        finally:
            # Очищаем временные файлы
            if 'temp_charts_dir' in locals():
                shutil.rmtree(temp_charts_dir, ignore_errors=True)
    
    async def handle_insights(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בתובנות והמלצות"""
        user_id = update.effective_user.id
        
        if not self.has_data(user_id):
            await update.message.reply_text(
                "❌ אין נתונים לתובנות!\n\n"
                "אנא שלח לי קובץ תחילה."
            )
            return
        
        await update.message.reply_text("💡 מנתח תובנות ומכין המלצות...")
        
        try:
            df = self.user_data[user_id]['data']
            insights_text = "💡 **תובנות מתקדמות והמלצות:**\n\n"
            
            # 1. Анализ корреляций
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                insights_text += "**🔗 ניתוח קורלציות:**\n"
                correlation_matrix = df[numeric_cols].corr()
                
                # Находим топ-5 корреляций
                correlations = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        corr_value = correlation_matrix.loc[col1, col2]
                        if not pd.isna(corr_value):
                            correlations.append((col1, col2, abs(corr_value)))
                
                # Сортируем по силе корреляции
                correlations.sort(key=lambda x: x[2], reverse=True)
                
                for i, (col1, col2, corr_abs) in enumerate(correlations[:5]):
                    corr_value = correlation_matrix.loc[col1, col2]
                    insights_text += f"• {col1} ↔ {col2}: {corr_value:.3f}\n"
                
                insights_text += "\n"
            
            # 2. Анализ выбросов
            if len(numeric_cols) > 0:
                insights_text += "**🔍 זיהוי אנומליות:**\n"
                for col in numeric_cols[:3]:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    
                    if len(outliers) > 0:
                        outlier_percentage = (len(outliers) / len(df)) * 100
                        insights_text += f"• ב-{col}: נמצאו {len(outliers)} ערכים חריגים ({outlier_percentage:.1f}%)\n"
                        insights_text += f"  - טווח תקין: {lower_bound:.2f} עד {upper_bound:.2f}\n"
                        if outlier_percentage > 10:
                            insights_text += f"  - ⚠️ אחוז גבוה של אנומליות - ייתכן שיידרש טיפול\n"
                    else:
                        insights_text += f"• ב-{col}: אין ערכים חריגים\n"
                
                insights_text += "\n"
            
            # 3. Рекомендации по улучшению данных
            insights_text += "**💡 המלצות לשיפור הנתונים:**\n"
            
            # Проверка на пропущенные значения
            total_nulls = df.isnull().sum().sum()
            total_cells = len(df) * len(df.columns)
            if total_nulls > 0:
                null_percentage = (total_nulls / total_cells) * 100
                insights_text += f"• ערכים חסרים: {total_nulls:,} ({null_percentage:.1f}% מהנתונים)\n"
                if null_percentage > 20:
                    insights_text += f"  - ⚠️ אחוז גבוה - בדוק את מקור הנתונים\n"
                elif null_percentage > 10:
                    insights_text += f"  - ⚠️ אחוז בינוני - שקול השלמה באמצעות ממוצע או חציון\n"
                else:
                    insights_text += f"  - ✅ אחוז נמוך - נתונים באיכות טובה\n"
            
            # Проверка на дубликаты
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                duplicate_percentage = (duplicates / len(df)) * 100
                insights_text += f"• שורות כפולות: {duplicates:,} ({duplicate_percentage:.1f}%)\n"
                insights_text += f"  - המלצה: הסר כפילויות לפני הניתוח\n"
            
            insights_text += "\n"
            
            # 4. Бизнес-инсайты
            insights_text += "**🚀 תובנות עסקיות:**\n"
            
            if len(numeric_cols) > 0:
                # Находим колонку с максимальной вариативностью
                max_var_col = numeric_cols[0]
                max_variance = df[max_var_col].var()
                for col in numeric_cols:
                    if df[col].var() > max_variance:
                        max_variance = df[col].var()
                        max_var_col = col
                
                insights_text += f"• העמודה {max_var_col} מראה את השונות הגבוהה ביותר\n"
                insights_text += f"  - זה עשוי להצביע על הזדמנויות או סיכונים עסקיים\n"
            
            # 5. Рекомендации по дальнейшему анализу
            insights_text += "\n**🎯 המלצות לניתוח נוסף:**\n"
            if len(numeric_cols) > 1:
                insights_text += "• ניתוח רגרסיה לזיהוי גורמים משפיעים\n"
                insights_text += "• ניתוח אשכולות (Clustering) לזיהוי דפוסים\n"
            if len(df.select_dtypes(include=['object']).columns) > 0:
                insights_text += "• ניתוח ANOVA להשוואה בין קבוצות\n"
                insights_text += "• ניתוח Chi-Square לבדיקת קשרים\n"
            
            # Разбиваем длинное сообщение
            if len(insights_text) > 4000:
                parts = [insights_text[i:i+4000] for i in range(0, len(insights_text), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text(f"💡 המשך התובנות (חלק {i+1}):\n\n{part}", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(insights_text, parse_mode=ParseMode.MARKDOWN)
            
            await update.message.reply_text(
                "🎯 **התובנות וההמלצות הושלמו!**\n\n"
                "עכשיו יש לך תמונה מלאה של הנתונים שלך.\n\n"
                "**מה עכשיו?**\n"
                "📊 'דוח PDF מתקדם' - לקבלת דוח מקצועי עם כל הניתוחים והתובנות! 🚀\n\n"
                "הדוח המתקדם יכלול את כל הניתוחים, התרשימים והתובנות במסמך אחד מקצועי בעברית!",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            await update.message.reply_text("❌ שגיאה ביצירת התובנות")
    
    def run(self):
        """הפעלת הבוט"""
        logger.info("Starting Simple Hebrew Bot...")
        self.application.run_polling()

def main():
    """הפונקציה הראשית"""
    
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
        print("Starting Simple Hebrew Bot with Advanced PDF Generation...")
        bot = SimpleHebrewBot(BOT_TOKEN)
        print("Bot created successfully!")
        print("Features available:")
        print("• Basic data analysis")
        print("• Professional charts generation")
        print("• Advanced insights and recommendations")
        print("• Regular PDF reports (old version)")
        print("• ADVANCED PDF reports with Hebrew RTL support (NEW!)")
        print("• Hebrew text display from right to left")
        print("• Professional charts in PDF")
        print("• Comprehensive data analysis")
        print("")
        print("Starting bot...")
        print("Now find the bot in Telegram and send /start")
        print("Upload CSV/Excel files and try the new 'דוח PDF מתקדם' button!")
        
        bot.run()
        
    except Exception as e:
        print(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
