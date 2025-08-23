# -*- coding: utf-8 -*-
"""
בוט פשוט לבדיקה - Simple bot for testing with advanced PDF generation
"""

import logging
import sys
import os
import pandas as pd
import numpy as np
import tempfile
import shutil
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

# Embedded enhanced chart generator (no external module needed)
def get_enhanced_chart_generator():  # noqa: N802 - keep external API name
    class EnhancedChartGenerator:
        def create_comprehensive_dashboard(self, df, analysis_results=None, output_dir=None):
            try:
                out_dir = output_dir or os.path.join(os.getcwd(), 'temp_charts')
                os.makedirs(out_dir, exist_ok=True)
                chart_files = []

                numeric_cols = df.select_dtypes(include=[np.number]).columns
                categorical_cols = df.select_dtypes(include=['object']).columns

                # 1) Bar chart for first categorical
                try:
                    if len(categorical_cols) > 0:
                        col = categorical_cols[0]
                        top_vals = df[col].value_counts().head(10)
                        if not top_vals.empty:
                            plt.figure(figsize=(10, 6))
                            plt.bar(range(len(top_vals)), top_vals.values)
                            plt.xticks(range(len(top_vals)), top_vals.index, rotation=45, ha='right')
                            plt.title(f'ערכים נפוצים: {col}')
                            plt.tight_layout()
                            path = os.path.join(out_dir, 'bar_chart_top_categories.png')
                            plt.savefig(path, dpi=220, bbox_inches='tight')
                            plt.close()
                            chart_files.append(path)
                except Exception:
                    pass

                # 2) Histogram for first numeric
                try:
                    if len(numeric_cols) > 0:
                        col = numeric_cols[0]
                        plt.figure(figsize=(9, 6))
                        plt.hist(df[col].dropna(), bins=30, alpha=0.8)
                        plt.title(f'היסטוגרמה: {col}')
                        plt.tight_layout()
                        path = os.path.join(out_dir, f'histogram_{col}.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        chart_files.append(path)
                except Exception:
                    pass

                # 3) Scatter for two numerics
                try:
                    if len(numeric_cols) > 1:
                        x, y = numeric_cols[:2]
                        plt.figure(figsize=(9, 6))
                        sns.regplot(x=df[x], y=df[y], scatter_kws={'alpha': 0.5})
                        plt.title(f'תרשים פיזור: {x} מול {y}')
                        plt.tight_layout()
                        path = os.path.join(out_dir, f'scatter_plot_{x}_vs_{y}.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        chart_files.append(path)
                except Exception:
                    pass

                # 4) Correlation heatmap
                try:
                    if len(numeric_cols) > 1:
                        corr = df[numeric_cols].corr()
                        plt.figure(figsize=(10, 8))
                        sns.heatmap(corr, annot=False, cmap='coolwarm', center=0)
                        plt.title('מפת קורלציה')
                        plt.tight_layout()
                        path = os.path.join(out_dir, 'correlation_heatmap.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        chart_files.append(path)
                except Exception:
                    pass

                # 5) Area chart for datetime column (counts by day)
                try:
                    dt_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
                    if len(dt_cols) > 0:
                        col = dt_cols[0]
                        ts = df[col].dropna()
                        if not ts.empty:
                            counts = ts.dt.to_period('D').value_counts().sort_index()
                            x = range(len(counts))
                            plt.figure(figsize=(12, 5))
                            plt.plot(x, counts.values, color='tab:blue')
                            plt.fill_between(x, counts.values, alpha=0.3, color='tab:blue')
                            plt.xticks(x[::max(1, len(x)//10)], [str(p) for p in counts.index[::max(1, len(x)//10)]], rotation=45, ha='right')
                            plt.title('תרשים שטח - ספירת רשומות לפי יום')
                            plt.tight_layout()
                            path = os.path.join(out_dir, 'area_chart_timeseries.png')
                            plt.savefig(path, dpi=220, bbox_inches='tight')
                            plt.close()
                            chart_files.append(path)
                except Exception:
                    pass

                return chart_files
            except Exception:
                return []

    return EnhancedChartGenerator()

# Setup logging: route INFO and below to stdout, WARNING+ to stderr
class _MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level

def _configure_logging() -> logging.Logger:
    logger = logging.getLogger()
    if getattr(logger, "_configured_split_handlers", False):
        return logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler for stdout: up to INFO
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(_MaxLevelFilter(logging.INFO))
    stdout_handler.setFormatter(formatter)

    # Handler for stderr: WARNING and above
    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    setattr(logger, "_configured_split_handlers", True)
    
    return logging.getLogger(__name__)

logger = _configure_logging()

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
            
            await update.message.reply_text("🚀 יוצר דוח PDF מתקדם בעברית עם ניתוח מקיף וגרפים מקצועיים…")
            
            try:
                df = self.user_data[user_id]['data']
                file_name = self.user_data[user_id]['file_name']
                
                # יצירת שם קובץ מותאם
                base_name = os.path.splitext(file_name)[0] if file_name else "נתונים"
                out_path = os.path.join(os.getcwd(), f'דוח_מתקדם_{base_name}.pdf')
                
                # שימוש בפונקציה החדשה והמשופרת
                pdf_path = generate_complete_data_report(df, out_path, include_charts=True)
                
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id, 
                            document=f, 
                            filename=os.path.basename(pdf_path), 
                            caption='🎉 דוח PDF מתקדם הוכן בהצלחה!\n\n'
                                   '✨ הדוח כולל:\n'
                                   '• ניתוח מעמיק של הנתונים\n'
                                   '• גרפים מקצועיים וויזואליזציות\n'
                                   '• תובנות ומסקנות אוטומטיות\n'
                                   '• המלצות מותאמות אישית\n'
                                   '• עיצוב מקצועי בעברית מימין לשמאל'
                        )
                    
                    # הודעת מעקב
                    await update.message.reply_text(
                        "🎯 **דוח PDF מתקדם נוצר בהצלחה!**\n\n"
                        "הדוח החדש כולל:\n"
                        "📊 ניתוח סטטיסטי מלא\n"
                        "📈 גרפים מקצועיים\n"
                        "🔍 זיהוי קורלציות וחריגים\n"
                        "💡 תובנות עסקיות\n"
                        "🎨 עיצוב מקצועי בעברית\n\n"
                        "זהו דוח מתקדם בהרבה מהדוח הרגיל! 🚀",
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
        """טיפול בתרשימים - יצירת תרשימים מקצועיים ומתקדמים עם מחולל משופר"""
        user_id = update.effective_user.id
        
        if not self.has_data(user_id):
            await update.message.reply_text(
                "❌ אין נתונים לתרשימים!\n\n"
                "אנא שלח לי קובץ CSV או Excel תחילה."
            )
            return
        
        await update.message.reply_text("📈 יוצר תרשימים מקצועיים עם מחולל משופר...")
        
        try:
            df = self.user_data[user_id]['data']
            
            # שימוש במחולל התרשימים המשופר
            enhanced_generator = get_enhanced_chart_generator()
            
            # יצירת ניתוח בסיסי לתרשימים
            analysis_results = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                analysis_results['correlation_matrix'] = df[numeric_cols].corr()
            
            # יצירת דשבורד מקיף עם כל סוגי התרשימים המשופרים
            chart_files = enhanced_generator.create_comprehensive_dashboard(df, analysis_results)
            
            # שליחת התרשימים למשתמש
            if chart_files:
                await update.message.reply_text(f"✅ נוצרו {len(chart_files)} תרשימים מקצועיים עם המחולל המשופר!")
                
                # סוגי התרשימים החדשים
                enhanced_chart_types = {
                    'bar_chart': '📊 תרשים עמודות משופר',
                    'histogram': '📊 היסטוגרמה עם סטטיסטיקות',
                    'scatter_plot': '🔵 תרשים פיזור עם מגמה',
                    'box_plot': '📦 תרשים קופסה עם נתונים',
                    'pie_chart': '🥧 תרשים עוגה עם מקרא',
                    'violin_plot': '🎻 תרשים כינור',
                    'correlation_heatmap': '🔥 מפת קורלציה',
                    'area_chart': '🏔️ תרשים שטח',
                    'radar_chart': '📡 תרשים רדאר',
                    'treemap': '🌳 מפת עץ'
                }
                
                for i, chart_file in enumerate(chart_files):
                    try:
                        with open(chart_file, 'rb') as img_file:
                            # זיהוי סוג התרשים
                            chart_type = "תרשים מקצועי משופר"
                            for key, value in enhanced_chart_types.items():
                                if key in os.path.basename(chart_file):
                                    chart_type = value
                                    break
                            
                            caption = f"📊 {chart_type}\n\n✨ נוצר עם מחולל התרשימים המשופר\n🎨 כולל תוויות בעברית ועיצוב מקצועי"
                            
                            await context.bot.send_photo(
                                chat_id=update.effective_chat.id,
                                photo=img_file,
                                caption=caption
                            )
                    except Exception as e:
                        logger.error(f"Error sending enhanced chart {chart_file}: {e}")
                        await update.message.reply_text(f"❌ שגיאה בשליחת תרשים {i+1}")
                
                await update.message.reply_text(
                    "🎉 **כל התרשימים המשופרים נשלחו!**\n\n"
                    "💡 **התרשימים החדשים כוללים:**\n"
                    "• 📊 תרשימי עמודות עם תוויות בעברית\n"
                    "• 📈 היסטוגרמות עם עקומות צפיפות\n"
                    "• 🔵 תרשימי פיזור עם קווי מגמה\n"
                    "• 📦 תרשימי קופסה עם סטטיסטיקות\n"
                    "• 🥧 תרשימי עוגה עם מקרא מפורט\n"
                    "• 🎻 תרשימי כינור מתקדמים\n"
                    "• 🔥 מפות קורלציה משופרות\n"
                    "• 🏔️ תרשימי שטח מוערמים\n\n"
                    "**מה עכשיו?**\n"
                    "💡 'תובנות והמלצות' - לקבלת תובנות עסקיות\n"
                    "📊 'דוח PDF מתקדם' - לדוח מקצועי עם כל הגרפים! 🎯"
                )
            else:
                await update.message.reply_text("❌ לא ניתן ליצור תרשימים מהנתונים הנוכחיים.")
            
        except Exception as e:
            logger.error(f"Error creating enhanced charts: {e}")
            await update.message.reply_text("❌ שגיאה ביצירת התרשימים המשופרים")
    
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
    BOT_TOKEN = "8418603857:AAGoqw3LGd5yRggjNUiNc-4_DcWHNq2Ucdo"
    
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
