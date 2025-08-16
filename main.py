# -*- coding: utf-8 -*-
"""
הבוט הראשי - Main bot file for the Hebrew Data Analytics Telegram Bot
"""

import logging
import os
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Filters
import asyncio
from typing import Dict, Any, Optional
import tempfile
import shutil

# Import our modules
from config import HEBREW_TEXTS, SUPPORTED_FORMATS, MAX_FILE_SIZE
from database import DatabaseManager
from google_sheets import get_google_sheets_manager
from data_analysis import DataAnalyzer
from visualization import get_chart_generator
from pdf_report import generate_hebrew_pdf_report

# Setup robust logging with rate limiting
from logging_setup import setup_logging
setup_logging()
setup_logging()
logger = logging.getLogger(__name__)

class HebrewDataAnalyticsBot:
    def __init__(self, bot_token: str = None):
        self.db = DatabaseManager()
        self.google_sheets = get_google_sheets_manager()
        self.chart_generator = get_chart_generator()
        
        # User sessions storage
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
        
        # Get token from environment or parameter
        if bot_token is None:
            bot_token = os.getenv('BOT_TOKEN')
        
        if not bot_token:
            raise ValueError("BOT_TOKEN not found! Please set BOT_TOKEN environment variable or pass it as parameter.")
        
        # Initialize bot
        self.updater = Updater(token=bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()
    
    def setup_handlers(self):
        """הגדרת כל ה-handlers של הבוט"""
        # Command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("menu", self.show_main_menu))
        
        # Message handlers
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_text_message))
        self.dispatcher.add_handler(MessageHandler(Filters.document, self.handle_document))
        
        # Callback query handlers
        self.dispatcher.add_handler(CallbackQueryHandler(self.handle_callback_query))
    
    def start_command(self, update: Update, context: CallbackContext):
        """טיפול בפקודת /start"""
        user = update.effective_user
        
        # הוספת משתמש למסד הנתונים
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # יצירת סשן משתמש
        self.user_sessions[user.id] = {
            'state': 'main_menu',
            'data': None,
            'analysis_results': None,
            'chart_files': []
        }
        
        # שליחת הודעת פתיחה
        welcome_text = HEBREW_TEXTS['welcome']
        update.message.reply_text(welcome_text, reply_markup=self.get_main_menu_keyboard())
    
    def help_command(self, update: Update, context: CallbackContext):
        """טיפול בפקודת /help"""
        help_text = """
📚 **עזרה - בוט ניתוח נתונים בעברית**

**פקודות זמינות:**
/start - התחלת שימוש בבוט
/menu - הצגת תפריט ראשי
/help - הצגת עזרה זו

**יכולות הבוט:**
• 📁 העלאת קבצי CSV ו-Excel
• 🔗 חיבור ל-Google Sheets
• 🔍 ניתוח נתונים אוטומטי
• 📊 יצירת תרשימים
• 💡 תובנות ותגליות
• 📄 יצירת דוחות PDF
• ❓ שאלות בשפה טבעית בעברית

**לשאלות נוספות, פנה למפתח הבוט.**
        """
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    def show_main_menu(self, update: Update, context: CallbackContext):
        """הצגת התפריט הראשי"""
        update.message.reply_text(
            HEBREW_TEXTS['main_menu'],
            reply_markup=self.get_main_menu_keyboard()
        )
    
    def get_main_menu_keyboard(self):
        """יצירת מקלדת התפריט הראשי"""
        keyboard = [
            [HEBREW_TEXTS['buttons']['upload_file']],
            [HEBREW_TEXTS['buttons']['google_sheets']],
            [HEBREW_TEXTS['buttons']['analyze_data']],
            [HEBREW_TEXTS['buttons']['show_charts']],
            [HEBREW_TEXTS['buttons']['generate_pdf']],
            [HEBREW_TEXTS['buttons']['ask_question']]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    def get_chart_selection_keyboard(self):
        """יצירת מקלדת בחירת סוג תרשים"""
        keyboard = []
        row = []
        for chart_type, chart_name in HEBREW_TEXTS['chart_types'].items():
            row.append(InlineKeyboardButton(chart_name, callback_data=f"chart_{chart_type}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton(HEBREW_TEXTS['buttons']['back_to_menu'], callback_data="back_to_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    def handle_text_message(self, update: Update, context: CallbackContext):
        """טיפול בהודעות טקסט"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # עדכון פעילות משתמש
        self.db.update_user_activity(user_id)
        
        # בדיקה אם המשתמש קיים בסשנים
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'state': 'main_menu',
                'data': None,
                'analysis_results': None,
                'chart_files': []
            }
        
        session = self.user_sessions[user_id]
        
        # טיפול לפי המצב הנוכחי
        if session['state'] == 'waiting_for_sheets_url':
            self.handle_sheets_url(update, context, text)
        elif session['state'] == 'waiting_for_question':
            self.handle_natural_language_question(update, context, text)
        else:
            # טיפול בכפתורים מהתפריט
            self.handle_menu_selection(update, context, text)
    
    def handle_menu_selection(self, update: Update, context: CallbackContext):
        """טיפול בבחירת תפריט"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if text == HEBREW_TEXTS['buttons']['upload_file']:
            update.message.reply_text(HEBREW_TEXTS['upload_file'])
            update.message.reply_text(
                "📁 שלח לי קובץ CSV או Excel, או הכנס קישור לגיליון Google Sheets"
            )
        
        elif text == HEBREW_TEXTS['buttons']['google_sheets']:
            self.handle_google_sheets_request(update, context)
        
        elif text == HEBREW_TEXTS['buttons']['analyze_data']:
            self.handle_analyze_data_request(update, context)
        
        elif text == HEBREW_TEXTS['buttons']['show_charts']:
            self.handle_show_charts_request(update, context)
        
        elif text == HEBREW_TEXTS['buttons']['generate_pdf']:
            self.handle_generate_pdf_request(update, context)
        
        elif text == HEBREW_TEXTS['buttons']['ask_question']:
            self.handle_ask_question_request(update, context)
        
        else:
            update.message.reply_text(
                "לא הבנתי את הבחירה שלך. אנא השתמש בכפתורים מהתפריט.",
                reply_markup=self.get_main_menu_keyboard()
            )
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בקבצים שהועלו"""
        user_id = update.effective_user.id
        document = update.message.document
        
        # בדיקת סוג הקובץ
        file_name = document.file_name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if file_extension not in SUPPORTED_FORMATS:
            await update.message.reply_text(
                f"❌ סוג קובץ לא נתמך. הקבצים הנתמכים: {', '.join(SUPPORTED_FORMATS)}"
            )
            return
        
        # בדיקת גודל הקובץ
        if document.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ הקובץ גדול מדי. הגודל המקסימלי: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
            return
        
        await update.message.reply_text(HEBREW_TEXTS['file_received'])
        
        try:
            # הורדת הקובץ
            file = await context.bot.get_file(document.file_id)
            
            # יצירת תיקייה זמנית
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file_name)
            
            # הורדת הקובץ
            await file.download_to_drive(file_path)
            
            # קריאת הקובץ
            df = await self.read_data_file(file_path, file_extension)
            
            if df is not None:
                # שמירת הנתונים בסשן
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = {}
                
                self.user_sessions[user_id].update({
                    'data': df,
                    'file_name': file_name,
                    'file_path': file_path,
                    'analysis_results': None,
                    'chart_files': []
                })
                
                # יצירת סשן במסד הנתונים
                session_id = self.db.create_session(
                    user_id=user_id,
                    file_name=file_name,
                    file_type=file_extension,
                    file_size=document.file_size
                )
                
                if session_id:
                    self.user_sessions[user_id]['session_id'] = session_id
                
                await update.message.reply_text(HEBREW_TEXTS['data_ready'])
                await update.message.reply_text(
                    "הנתונים מוכנים לניתוח! מה תרצה לעשות?",
                    reply_markup=self.get_main_menu_keyboard()
                )
            else:
                await update.message.reply_text(HEBREW_TEXTS['file_error'])
            
        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await update.message.reply_text(HEBREW_TEXTS['processing_error'])
        
        finally:
            # ניקוי תיקייה זמנית
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def read_data_file(self, file_path: str, file_extension: str) -> Optional[pd.DataFrame]:
        """קריאת קובץ נתונים"""
        try:
            if file_extension == '.csv':
                # ניסיון לקרוא עם encoding שונים
                encodings = ['utf-8', 'latin-1', 'cp1255', 'iso-8859-8']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        return df
                    except UnicodeDecodeError:
                        continue
                return None
            
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    async def handle_google_sheets_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בבקשת Google Sheets"""
        user_id = update.effective_user.id
        
        # בדיקת חיבור Google Sheets
        if not self.google_sheets.test_connection():
            await update.message.reply_text(
                "❌ לא ניתן להתחבר ל-Google Sheets. אנא ודא שקובץ האישורים קיים ותקין."
            )
            return
        
        # שינוי מצב המשתמש
        self.user_sessions[user_id]['state'] = 'waiting_for_sheets_url'
        
        await update.message.reply_text(HEBREW_TEXTS['enter_sheets_url'])
        await update.message.reply_text(
            "דוגמה: https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        )
    
    async def handle_sheets_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """טיפול בקישור Google Sheets"""
        user_id = update.effective_user.id
        
        # בדיקת תקינות הקישור
        if not self.google_sheets.is_valid_sheet_url(url):
            await update.message.reply_text(
                "❌ הקישור אינו תקין. אנא ודא שזהו קישור לגיליון Google Sheets."
            )
            return
        
        await update.message.reply_text("🔄 מתחבר לגיליון Google Sheets...")
        
        try:
            # קבלת נתונים מהגיליון
            df, sheet_title, error = self.google_sheets.get_sheet_data(url)
            
            if df is not None:
                # שמירת הנתונים בסשן
                self.user_sessions[user_id].update({
                    'data': df,
                    'file_name': f"Google Sheets - {sheet_title}",
                    'sheets_url': url,
                    'analysis_results': None,
                    'chart_files': []
                })
                
                # הוספת חיבור למסד הנתונים
                self.db.add_google_sheets_connection(user_id, url, sheet_title)
                
                # יצירת סשן במסד הנתונים
                session_id = self.db.create_session(
                    user_id=user_id,
                    file_name=f"Google Sheets - {sheet_title}",
                    file_type='.sheets',
                    file_size=len(df) * len(df.columns) * 8  # הערכת גודל
                )
                
                if session_id:
                    self.user_sessions[user_id]['session_id'] = session_id
                
                # החזרה למצב רגיל
                self.user_sessions[user_id]['state'] = 'main_menu'
                
                await update.message.reply_text(HEBREW_TEXTS['sheets_connected'])
                await update.message.reply_text(
                    f"הנתונים מהגיליון '{sheet_title}' מוכנים לניתוח!",
                    reply_markup=self.get_main_menu_keyboard()
                )
            else:
                await update.message.reply_text(f"❌ {error}")
                self.user_sessions[user_id]['state'] = 'main_menu'
        
        except Exception as e:
            logger.error(f"Error handling Google Sheets: {e}")
            await update.message.reply_text(HEBREW_TEXTS['sheets_error'])
            self.user_sessions[user_id]['state'] = 'main_menu'
    
    async def handle_analyze_data_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בבקשת ניתוח נתונים"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or self.user_sessions[user_id].get('data') is None:
            await update.message.reply_text(HEBREW_TEXTS['no_data'])
            return
        
        await update.message.reply_text(HEBREW_TEXTS['analyzing_data'])
        
        try:
            # ניתוח הנתונים
            df = self.user_sessions[user_id]['data']
            analyzer = DataAnalyzer(df)
            
            # ניקוי הנתונים
            clean_df = analyzer.clean_data()
            
            # ניתוח מקיף
            analysis_results = analyzer.get_analysis_summary()
            
            # שמירת תוצאות הניתוח
            self.user_sessions[user_id]['analysis_results'] = analysis_results
            self.user_sessions[user_id]['clean_data'] = clean_df
            
            # עדכון מסד הנתונים
            if 'session_id' in self.user_sessions[user_id]:
                self.db.update_session_analysis(
                    self.user_sessions[user_id]['session_id'],
                    'comprehensive_analysis',
                    analysis_results
                )
            
            # שליחת סיכום
            summary_text = "📊 **סיכום הניתוח:**\n\n"
            
            if 'basic_info' in analysis_results:
                basic_info = analysis_results['basic_info']
                rows, cols = basic_info['shape']
                summary_text += f"• מספר שורות: {rows:,}\n"
                summary_text += f"• מספר עמודות: {cols}\n"
                
                total_nulls = sum(basic_info['null_counts'].values())
                if total_nulls > 0:
                    summary_text += f"• ערכים חסרים: {total_nulls:,}\n"
                else:
                    summary_text += "• אין ערכים חסרים\n"
            
            if 'insights' in analysis_results:
                summary_text += "\n💡 **תובנות עיקריות:**\n"
                for insight in analysis_results['insights'][:3]:  # רק 3 הראשונות
                    summary_text += f"• {insight}\n"
            
            await update.message.reply_text(summary_text, parse_mode=ParseMode.MARKDOWN)
            await update.message.reply_text(
                "הניתוח הושלם! מה תרצה לעשות עכשיו?",
                reply_markup=self.get_main_menu_keyboard()
            )
        
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            await update.message.reply_text(HEBREW_TEXTS['processing_error'])
    
    async def handle_show_charts_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בבקשת הצגת תרשימים"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or self.user_sessions[user_id].get('data') is None:
            await update.message.reply_text(HEBREW_TEXTS['no_data'])
            return
        
        await update.message.reply_text(
            HEBREW_TEXTS['choose_chart'],
            reply_markup=self.get_chart_selection_keyboard()
        )
    
    async def handle_generate_pdf_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בבקשת יצירת דוח PDF"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or self.user_sessions[user_id].get('analysis_results') is None:
            await update.message.reply_text(
                "❌ אין תוצאות ניתוח זמינות. אנא בצע ניתוח נתונים תחילה."
            )
            return
        
        await update.message.reply_text(HEBREW_TEXTS['generating_pdf'])
        
        try:
            # יצירת תרשימים אם אין
            if not self.user_sessions[user_id].get('chart_files'):
                df = self.user_sessions[user_id]['data']
                analysis_results = self.user_sessions[user_id]['analysis_results']
                
                chart_files = self.chart_generator.create_comprehensive_dashboard(df, analysis_results)
                self.user_sessions[user_id]['chart_files'] = chart_files
            
            # יצירת הדוח PDF
            analysis_results = self.user_sessions[user_id]['analysis_results']
            chart_files = self.user_sessions[user_id].get('chart_files', [])
            
            pdf_path = generate_hebrew_pdf_report(
                analysis_results=analysis_results,
                chart_files=chart_files,
                output_path=f"report_user_{user_id}.pdf"
            )
            
            if pdf_path and os.path.exists(pdf_path):
                # שליחת הדוח
                with open(pdf_path, 'rb') as pdf_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=pdf_file,
                        filename="דוח_ניתוח_נתונים.pdf",
                        caption=HEBREW_TEXTS['pdf_ready']
                    )
                
                # ניקוי הקובץ
                os.remove(pdf_path)
            else:
                await update.message.reply_text("❌ שגיאה ביצירת הדוח PDF")
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            await update.message.reply_text("❌ שגיאה ביצירת הדוח PDF")
    
    async def handle_ask_question_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בבקשת שאלה בשפה טבעית"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or self.user_sessions[user_id].get('data') is None:
            await update.message.reply_text(HEBREW_TEXTS['no_data'])
            return
        
        # שינוי מצב המשתמש
        self.user_sessions[user_id]['state'] = 'waiting_for_question'
        
        await update.message.reply_text(HEBREW_TEXTS['ask_question'])
        await update.message.reply_text(HEBREW_TEXTS['question_examples'])
    
    async def handle_natural_language_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, question: str):
        """טיפול בשאלה בשפה טבעית"""
        user_id = update.effective_user.id
        
        try:
            # ניתוח השאלה
            df = self.user_sessions[user_id]['data']
            analyzer = DataAnalyzer(df)
            
            answer = analyzer.answer_natural_language_question(question)
            
            await update.message.reply_text(f"❓ **שאלה:** {question}\n\n💡 **תשובה:** {answer}")
            
            # החזרה למצב רגיל
            self.user_sessions[user_id]['state'] = 'main_menu'
            
            await update.message.reply_text(
                "יש לך שאלה נוספת?",
                reply_markup=self.get_main_menu_keyboard()
            )
        
        except Exception as e:
            logger.error(f"Error handling question: {e}")
            await update.message.reply_text("❌ שגיאה במענה על השאלה")
            self.user_sessions[user_id]['state'] = 'main_menu'
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בכפתורים inline"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data.startswith("chart_"):
            await self.handle_chart_creation(query, query.data.replace("chart_", ""))
        elif query.data == "back_to_menu":
            await self.handle_back_to_menu(query)
    
    async def handle_chart_creation(self, query, chart_type: str):
        """טיפול ביצירת תרשים"""
        user_id = query.from_user.id
        
        if user_id not in self.user_sessions or self.user_sessions[user_id].get('data') is None:
            await query.edit_message_text(HEBREW_TEXTS['no_data'])
            return
        
        await query.edit_message_text("🔄 יוצר תרשים...")
        
        try:
            df = self.user_sessions[user_id]['data']
            chart_generator = self.chart_generator
            
            chart_file = None
            
            if chart_type == 'bar':
                # בחירת עמודות מתאימות
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    # תרשים עמודות לממוצעים
                    means = df[numeric_cols].mean().sort_values(ascending=False)
                    chart_file = chart_generator.create_bar_chart(
                        pd.DataFrame({'Column': means.index, 'Mean': means.values}),
                        'Column', 'Mean', "ממוצעים לפי עמודות"
                    )
            
            elif chart_type == 'line':
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    chart_file = chart_generator.create_line_chart(
                        df, numeric_cols[0], numeric_cols[1], f"מגמה: {numeric_cols[0]} vs {numeric_cols[1]}"
                    )
            
            elif chart_type == 'pie':
                # תרשים עוגה לעמודה קטגורית
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    col = categorical_cols[0]
                    value_counts = df[col].value_counts().head(10)
                    chart_file = chart_generator.create_pie_chart(
                        value_counts.reset_index(), 'index', col, f"התפלגות {col}"
                    )
            
            elif chart_type == 'histogram':
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    chart_file = chart_generator.create_histogram(
                        df, numeric_cols[0], f"היסטוגרמה של {numeric_cols[0]}"
                    )
            
            elif chart_type == 'scatter':
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    chart_file = chart_generator.create_scatter_plot(
                        df, numeric_cols[0], numeric_cols[1], 
                        f"פיזור: {numeric_cols[0]} vs {numeric_cols[1]}"
                    )
            
            elif chart_type == 'box':
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    chart_file = chart_generator.create_box_plot(
                        df, numeric_cols[0], title=f"תרשים קופסה של {numeric_cols[0]}"
                    )
            
            if chart_file and os.path.exists(chart_file):
                # שליחת התרשים
                with open(chart_file, 'rb') as img_file:
                    await context.bot.send_photo(
                        chat_id=query.message.chat.id,
                        photo=img_file,
                        caption=f"📊 התרשים שלך - {HEBREW_TEXTS['chart_types'].get(chart_type, chart_type)}"
                    )
                
                # שמירת התרשים בסשן
                if 'chart_files' not in self.user_sessions[user_id]:
                    self.user_sessions[user_id]['chart_files'] = []
                self.user_sessions[user_id]['chart_files'].append(chart_file)
                
                await query.edit_message_text(HEBREW_TEXTS['chart_sent'])
            else:
                await query.edit_message_text("❌ שגיאה ביצירת התרשים")
        
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            await query.edit_message_text("❌ שגיאה ביצירת התרשים")
    
    async def handle_back_to_menu(self, query):
        """טיפול בחזרה לתפריט"""
        await query.edit_message_text(
            HEBREW_TEXTS['main_menu'],
            reply_markup=self.get_main_menu_keyboard()
        )
    
    def run(self):
        """הפעלת הבוט"""
        logger.info("Starting Hebrew Data Analytics Bot...")
        self.updater.start_polling()
        self.updater.idle()

def main():
    """הפונקציה הראשית"""
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    bot = HebrewDataAnalyticsBot(bot_token=bot_token)
    bot.run()

if __name__ == "__main__":
    main()
