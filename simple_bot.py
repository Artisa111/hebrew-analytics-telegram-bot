# -*- coding: utf-8 -*-
"""
בוט פשוט לבדיקה - Simple bot for testing
"""

import logging
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

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

**איך להשתמש:**
1. שלח לי קובץ CSV או Excel
2. בחר "ניתוח נתונים" לניתוח מקיף
3. בחר "תרשימים" ליצירת גרפים
4. בחר "תובנות והמלצות" לקבלת תובנות

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
                    f"עכשיו אתה יכול לבחור 'ניתוח נתונים', 'תרשימים' או 'תובנות והמלצות'!"
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
        
        elif text == '📁 העלאת קובץ':
            await update.message.reply_text(
                "📁 שלח לי קובץ CSV או Excel כדי להתחיל!\n\n"
                "אני תומך בקבצים:\n"
                "• CSV (.csv)\n"
                "• Excel (.xlsx, .xls)\n\n"
                "גודל מקסימלי: 50MB"
            )
        
        elif text == '❓ עזרה':
            await self.help_command(update, context)
        
        else:
            await update.message.reply_text(
                "לא הבנתי את ההודעה שלך. אנא השתמש בכפתורים או שלח /help"
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
                "✅ הניתוח הושלם! עכשיו אתה יכול לבחור 'תרשימים' או 'תובנות והמלצות'."
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
            
            # 2. Столбчатые диаграммы для категориальных данных
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

                    # Добавляем процентные метки (относительно ненулевого количества)
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
            
            # 3. Корреляционная матрица с улучшенным дизайном
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
            
            # 4. Scatter plot для числовых колонок
            if len(numeric_cols) > 1:
                # Создаем scatter plot matrix
                fig, axes = plt.subplots(2, 2, figsize=(16, 12))
                fig.suptitle('Scatter Plots - גרפי פיזור', fontsize=18, fontweight='bold')
                
                plot_count = 0
                for i in range(min(2, len(numeric_cols))):
                    for j in range(min(2, len(numeric_cols))):
                        if i != j and plot_count < 4:
                            row, col = plot_count // 2, plot_count % 2
                            axes[row, col].scatter(df[numeric_cols[i]], df[numeric_cols[j]], 
                                                 alpha=0.6, s=30, c='steelblue', edgecolors='black', linewidth=0.5)
                            axes[row, col].set_xlabel(numeric_cols[i], fontsize=10, fontweight='bold')
                            axes[row, col].set_ylabel(numeric_cols[j], fontsize=10, fontweight='bold')
                            axes[row, col].grid(True, alpha=0.3, linestyle='--')
                            
                            # Добавляем линию тренда
                            z = np.polyfit(df[numeric_cols[i]].dropna(), df[numeric_cols[j]].dropna(), 1)
                            p = np.poly1d(z)
                            axes[row, col].plot(df[numeric_cols[i]], p(df[numeric_cols[i]]), 
                                              "r--", alpha=0.8, linewidth=2)
                            
                            plot_count += 1
                
                plt.tight_layout()
                chart_path = os.path.join(temp_charts_dir, 'scatter_matrix.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                chart_files.append(chart_path)
                chart_insights[chart_path] = "בדקו קשרים ליניאריים וקלאסטרים אפשריים בין זוגות משתנים."
                chart_next_steps[chart_path] = "מה הלאה:\n• הוספת קווי רגרסיה\n• נסיון קלאסטריזציה (KMeans)"
            
            # 5. Анализ распределения (Distribution Analysis)
            if len(numeric_cols) > 0:
                fig, axes = plt.subplots(2, 2, figsize=(16, 12))
                fig.suptitle('ניתוח התפלגות - Distribution Analysis', fontsize=18, fontweight='bold')
                
                for i, col in enumerate(numeric_cols[:4]):
                    if i < 4:
                        row, col_idx = i // 2, i % 2
                        
                        # Histogram с кривой плотности
                        axes[row, col_idx].hist(df[col].dropna(), bins=25, density=True, alpha=0.7, 
                                               color='lightcoral', edgecolor='darkred', linewidth=1)
                        
                        # Добавляем кривую плотности
                        data = df[col].dropna()
                        if len(data) > 0:
                            x = np.linspace(data.min(), data.max(), 100)
                            kde = stats.gaussian_kde(data)
                            axes[row, col_idx].plot(x, kde(x), 'b-', linewidth=2, label='KDE')
                        
                        axes[row, col_idx].set_title(f'{col}', fontsize=12, fontweight='bold')
                        axes[row, col_idx].set_xlabel('ערך', fontsize=10)
                        axes[row, col_idx].set_ylabel('צפיפות', fontsize=10)
                        axes[row, col_idx].grid(True, alpha=0.3, linestyle='--')
                        axes[row, col_idx].legend()
                
                plt.tight_layout()
                chart_path = os.path.join(temp_charts_dir, 'distribution_analysis.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                chart_files.append(chart_path)

                skews = [abs(df[c].dropna().skew()) for c in numeric_cols[:4] if df[c].dropna().size > 0]
                if skews:
                    skew_avg = float(np.mean(skews))
                    chart_insights[chart_path] = f"ממוצע הטיה במדגם: {skew_avg:.2f}. ערכים גבוהים מעידים על זנבות כבדים/אי-נורמליות."
                    chart_next_steps[chart_path] = "מה הלאה:\n• שקילת נרמול/סטנדרטיזציה\n• שימוש במדדים חסיני-חריגים"
            
            # 6. Анализ выбросов (Outlier Analysis)
            if len(numeric_cols) > 0:
                fig, axes = plt.subplots(2, 2, figsize=(16, 12))
                fig.suptitle('ניתוח אנומליות - Outlier Analysis', fontsize=18, fontweight='bold')
                
                for i, col in enumerate(numeric_cols[:4]):
                    if i < 4:
                        row, col_idx = i // 2, i % 2
                        
                        # Box plot с выбросами
                        bp = axes[row, col_idx].boxplot(df[col].dropna(), patch_artist=True,
                                                       boxprops=dict(facecolor='lightblue', alpha=0.7),
                                                       medianprops=dict(color='red', linewidth=2),
                                                       flierprops=dict(marker='o', markerfacecolor='red', 
                                                                      markersize=6, alpha=0.7))
                        
                        axes[row, col_idx].set_title(f'{col}', fontsize=12, fontweight='bold')
                        axes[row, col_idx].set_ylabel('ערך', fontsize=10)
                        axes[row, col_idx].grid(True, alpha=0.3, linestyle='--')
                        
                        # Добавляем статистику
                        stats_text = f'Q1: {df[col].quantile(0.25):.2f}\nQ3: {df[col].quantile(0.75):.2f}\nIQR: {df[col].quantile(0.75) - df[col].quantile(0.25):.2f}'
                        axes[row, col_idx].text(0.02, 0.98, stats_text, transform=axes[row, col_idx].transAxes,
                                               verticalalignment='top', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                plt.tight_layout()
                chart_path = os.path.join(temp_charts_dir, 'outlier_analysis.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                chart_files.append(chart_path)

                outlier_rates = []
                for c in numeric_cols[:4]:
                    s = df[c].dropna()
                    if s.empty:
                        continue
                    q1, q3 = s.quantile(0.25), s.quantile(0.75)
                    iqr = q3 - q1
                    low, up = q1 - 1.5*iqr, q3 + 1.5*iqr
                    outlier_rates.append(((s < low) | (s > up)).mean()*100)
                if outlier_rates:
                    chart_insights[chart_path] = f"שיעור חריגים ממוצע: {np.mean(outlier_rates):.1f}%."
                    chart_next_steps[chart_path] = "מה הלאה:\n• טיפול בחריגים (חיתוך/Winsorize)\n• שימוש במודלים חסיני-חריגים"
            
            # 7. Временной анализ (если есть колонки с датами)
            date_cols = [col for col in numeric_cols if any(keyword in col.lower() for keyword in ['date', 'time', 'year', 'month', 'day', '202', '201'])]
            if len(date_cols) > 0:
                for col in date_cols[:2]:
                    plt.figure(figsize=(14, 8))
                    
                    # Сортируем данные по времени
                    sorted_data = df.sort_values(col)
                    
                    plt.plot(sorted_data[col], sorted_data.index, 'o-', linewidth=2, markersize=4, 
                           color='purple', alpha=0.7, markerfacecolor='white', markeredgecolor='purple')
                    
                    plt.title(f'ניתוח טרנדים - {col}', fontsize=16, fontweight='bold', pad=20)
                    plt.xlabel(col, fontsize=12, fontweight='bold')
                    plt.ylabel('אינדקס', fontsize=12, fontweight='bold')
                    plt.grid(True, alpha=0.3, linestyle='--')
                    
                    # Добавляем линию тренда
                    if len(sorted_data) > 1:
                        z = np.polyfit(range(len(sorted_data)), sorted_data[col], 1)
                        p = np.poly1d(z)
                        plt.plot(sorted_data[col], p(range(len(sorted_data))), "r--", alpha=0.8, linewidth=2, label='Trend')
                        plt.legend()
                    
                    plt.tight_layout()
                    chart_path = os.path.join(temp_charts_dir, f'trend_analysis_{col}.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()
                    chart_files.append(chart_path)

                    try:
                        z = np.polyfit(range(len(sorted_data)), sorted_data[col], 1)
                        slope = float(z[0])
                        direction = 'מגמת עליה' if slope > 0 else 'מגמת ירידה' if slope < 0 else 'יציב'
                        chart_insights[chart_path] = f"{col}: {direction} (שיפוע {slope:.3f})."
                        chart_next_steps[chart_path] = "מה הלאה:\n• בדיקת עונתיות\n• חיזוי (ARIMA/Prophet)"
                    except Exception:
                        pass
            
            # 8. Сводная статистика в виде таблицы
            if len(numeric_cols) > 0:
                fig, ax = plt.subplots(figsize=(14, 8))
                ax.axis('tight')
                ax.axis('off')
                
                # Создаем таблицу со статистикой
                stats_data = []
                for col in numeric_cols[:6]:  # Первые 6 колонок
                    col_stats = df[col].describe()
                    stats_data.append([
                        col,
                        f"{col_stats['count']:.0f}",
                        f"{col_stats['mean']:.2f}",
                        f"{col_stats['std']:.2f}",
                        f"{col_stats['min']:.2f}",
                        f"{col_stats['25%']:.2f}",
                        f"{col_stats['50%']:.2f}",
                        f"{col_stats['75%']:.2f}",
                        f"{col_stats['max']:.2f}"
                    ])
                
                table = ax.table(cellText=stats_data,
                               colLabels=['עמודה', 'מספר', 'ממוצע', 'סט"ת', 'מינימום', 'Q1', 'חציון', 'Q3', 'מקסימום'],
                               cellLoc='center',
                               loc='center',
                               colWidths=[0.15, 0.1, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12])
                
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1.2, 1.5)
                
                # Стилизация таблицы
                for i in range(len(stats_data) + 1):
                    for j in range(9):
                        if i == 0:  # Заголовки
                            table[(i, j)].set_facecolor('#4CAF50')
                            table[(i, j)].set_text_props(weight='bold', color='white')
                        else:  # Данные
                            if j == 0:  # Названия колонок
                                table[(i, j)].set_facecolor('#E8F5E8')
                            else:  # Числовые значения
                                table[(i, j)].set_facecolor('#F8F9FA')
                
                plt.title('סיכום סטטיסטי - Statistical Summary', fontsize=16, fontweight='bold', pad=20)
                plt.tight_layout()
                
                chart_path = os.path.join(temp_charts_dir, 'statistical_summary.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                chart_files.append(chart_path)

                try:
                    stds = {c: float(df[c].std()) for c in numeric_cols[:6]}
                    max_col = max(stds, key=stds.get)
                    chart_insights[chart_path] = f"סטיית התקן הגבוהה ביותר: {max_col} ({stds[max_col]:.2f}). מצביע על שונות גבוהה."
                    chart_next_steps[chart_path] = "מה הלאה:\n• נרמול לפני ML\n• פילוח להקטנת שונות"
                except Exception:
                    pass
            
            # === 9. Воронка (Funnel) если удается определить этапы ===
            try:
                funnel_chart_created = False
                stage_keywords = ['stage','status','event','step','funnel','phase','state']
                ordered_stage_keywords = ['visit','view','signup','register','add_to_cart','checkout','purchase','pay','converted']
                
                # Кейс 1: одна категориальная колонка с этапами
                stage_col = None
                for col in df.select_dtypes(include=['object']).columns:
                    col_lower = col.lower()
                    if any(k in col_lower for k in stage_keywords):
                        if df[col].nunique() <= 12 and df[col].nunique() >= 3:
                            stage_col = col
                            break
                
                stage_counts = None
                stage_order = None
                
                if stage_col is not None:
                    counts = df[stage_col].value_counts()
                    # Пытаемся упорядочить по известной последовательности, иначе по убыванию частоты
                    order_map = {name: i for i, name in enumerate(ordered_stage_keywords)}
                    keys = list(counts.index)
                    if any(any(k in str(v).lower() for k in ordered_stage_keywords) for v in keys):
                        keys_sorted = sorted(keys, key=lambda v: order_map.get(str(v).lower(), 999))
                        stage_counts = counts[keys_sorted]
                        stage_order = keys_sorted
                    else:
                        stage_counts = counts
                        stage_order = list(counts.index)
                else:
                    # Кейс 2: несколько числовых колонок по ключам этапов (суммы по колонкам)
                    cols = []
                    for key in ordered_stage_keywords:
                        for c in df.columns:
                            if key in c.lower():
                                cols.append(c)
                    cols = list(dict.fromkeys(cols))
                    if len(cols) >= 3:
                        stage_order = cols
                        totals = []
                        for c in cols:
                            series = pd.to_numeric(df[c], errors='coerce')
                            totals.append(np.nansum(series.values))
                        stage_counts = pd.Series(totals, index=cols)
                
                if stage_counts is not None and len(stage_counts) >= 3:
                    # Строим красивую воронку
                    base = float(stage_counts.iloc[0]) if float(stage_counts.iloc[0]) != 0 else 1.0
                    conversions = [100.0]
                    for i in range(1, len(stage_counts)):
                        prev = float(stage_counts.iloc[i-1]) if float(stage_counts.iloc[i-1]) != 0 else 1.0
                        conv = (float(stage_counts.iloc[i]) / prev) * 100.0
                        conversions.append(conv)
                    
                    plt.figure(figsize=(12, 8))
                    vals = stage_counts.values.astype(float)
                    rel = vals / (vals[0] if vals[0] != 0 else 1.0)
                    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(vals)))
                    
                    y_pos = np.arange(len(stage_counts))[::-1]
                    plt.barh(y_pos, rel, color=colors, edgecolor='black', height=0.6)
                    
                    for i, (v, c) in enumerate(zip(vals, conversions)):
                        plt.text(rel[i] + 0.01, y_pos[i], f"{v:,.0f}  ({c:.1f}%)", va='center', fontsize=11, fontweight='bold')
                    
                    plt.yticks(y_pos, [str(s) for s in stage_counts.index])
                    plt.gca().invert_yaxis()
                    plt.title('וורונקה עסקית - Funnel Analysis', fontsize=16, fontweight='bold', pad=20)
                    plt.xlabel('יחס לשלב הראשון', fontsize=12, fontweight='bold')
                    plt.grid(True, axis='x', alpha=0.3, linestyle='--')
                    plt.tight_layout()
                    chart_path = os.path.join(temp_charts_dir, 'funnel_chart.png')
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()
                    chart_files.append(chart_path)
                    funnel_chart_created = True
                    
                    # Если удалось — сообщим о конверсиях
                    try:
                        msg = ["🔻 ניתוח וורונקה (Funnel):"]
                        for i, name in enumerate(stage_counts.index):
                            msg.append(f"• {name}: {stage_counts.iloc[i]:,.0f}")
                            if i > 0:
                                msg.append(f"  ↳ המרה משלב קודם: {conversions[i]:.1f}%")
                        # вместо отдельного сообщения добавим это כתובית לתרשים
                        overall = 0.0
                        try:
                            overall = (float(stage_counts.iloc[-1]) / float(stage_counts.iloc[0])) * 100.0 if float(stage_counts.iloc[0]) != 0 else 0.0
                        except Exception:
                            overall = 0.0
                        insight = [f"המרה כוללת: {overall:.1f}%"]
                        for j in range(1, len(stage_counts)):
                            insight.append(f"{stage_counts.index[j]}: {conversions[j]:.1f}% משלב קודם")
                        chart_insights[chart_path] = " | ".join(insight)
                        chart_next_steps[chart_path] = "מה הלאה:\n• אתר את שלב הנפילה וטפל בו\n• להריץ A/B על קריאות לפעולה"
                    except:
                        pass
            except Exception as e:
                logging.exception("Funnel build failed")
            
            # 3. Funnel Chart
            funnel_cols = ['visit', 'signup', 'purchase']  # Example columns for funnel
            if all(col in df.columns for col in funnel_cols):
                funnel_data = df[funnel_cols].sum()
                plt.figure(figsize=(10, 6))
                plt.barh(funnel_cols, funnel_data, color=['#FF9999', '#66B3FF', '#99FF99'])
                plt.title('תרשים משפך', fontsize=16, fontweight='bold')
                plt.xlabel('כמות', fontsize=12, fontweight='bold')
                plt.ylabel('שלב', fontsize=12, fontweight='bold')
                for index, value in enumerate(funnel_data):
                    plt.text(value, index, f'{value}', va='center', ha='right', fontweight='bold')
                plt.tight_layout()
                funnel_chart_path = os.path.join(temp_charts_dir, 'funnel_chart.png')
                plt.savefig(funnel_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                chart_files.append(funnel_chart_path)
                try:
                    overall = (float(funnel_data.iloc[-1]) / float(funnel_data.iloc[0])) * 100.0 if float(funnel_data.iloc[0]) != 0 else 0.0
                except Exception:
                    overall = 0.0
                chart_insights[funnel_chart_path] = f"המרה כוללת: {overall:.1f}% | שלבים: {', '.join(funnel_cols)}"
                chart_next_steps[funnel_chart_path] = "מה הלאה:\n• חפשו צווארי בקבוק בין שלבים\n• להריץ A/B לשיפור CTA"
            
            # Отправляем графики
            if chart_files:
                await update.message.reply_text(f"✅ נוצרו {len(chart_files)} תרשימים מקצועיים!")
                
                # Группируем графики по типам для лучшей организации
                chart_types = {
                    'histogram_box': '📊 היסטוגרמות ו-Box Plots',
                    'bar_chart': '📈 גרפים עמודות',
                    'correlation_matrix': '🔗 מטריצת קורלציה',
                    'scatter_matrix': '🎯 גרפי פיזור',
                    'distribution_analysis': '📈 ניתוח התפלגות',
                    'outlier_analysis': '🔍 ניתוח אנומליות',
                    'trend_analysis': '📈 ניתוח טרנדים',
                    'statistical_summary': '📋 סיכום סטטיסטי',
                    'funnel_chart': '🔗 וורונקה עסקית'
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
                    "🎉 כל התרשימים נשלחו! עכשיו יש לך ניתוח ויזואלי מקיף ומקצועי.\n\n"
                    "💡 **סוגי התרשימים שנוצרו:**\n"
                    "• 📊 היסטוגרמות עם Box Plots\n"
                    "• 📈 גרפים עמודות עם אחוזים\n"
                    "• 🔗 מטריצת קורלציה מתקדמת\n"
                    "• 🎯 גרפי פיזור עם קווי טרנד\n"
                    "• 📈 ניתוח התפלגות עם KDE\n"
                    "• 🔍 ניתוח אנומליות מפורט\n"
                    "• 📈 ניתוח טרנדים זמניים\n"
                    "• 📋 סיכום סטטיסטי בטבלה\n"
                    "• 🔗 וורונקה עסקית\n\n"
                    "עכשיו אתה יכול לבחור 'תובנות והמלצות' לקבלת תובנות עסקיות מתקדמות!"
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
            insights_text = "💡 תובנות מתקדמות והמלצות:\n\n"
            
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
            
            # 3. Анализ распределения
            if len(numeric_cols) > 0:
                insights_text += "**📊 ניתוח התפלגות:**\n"
                for col in numeric_cols[:2]:
                    skewness = df[col].skew()
                    if abs(skewness) > 1:
                        distribution_type = "מוטה מאוד" if abs(skewness) > 2 else "מוטה"
                        direction = "ימינה" if skewness > 0 else "שמאלה"
                        insights_text += f"• {col}: התפלגות {distribution_type} {direction} (skewness: {skewness:.2f})\n"
                        if abs(skewness) > 2:
                            insights_text += f"  - ⚠️ התפלגות מאוד מוטה - שקול לבדוק את מקור הנתונים\n"
                    else:
                        insights_text += f"• {col}: התפלגות נורמלית יחסית (skewness: {skewness:.2f})\n"
                
                insights_text += "\n"
            
            # 4. Анализ категориальных данных
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                insights_text += "**🏷️ ניתוח קטגוריות:**\n"
                for col in categorical_cols[:2]:
                    value_counts = df[col].value_counts()
                    diversity = len(value_counts) / len(df)
                    
                    if diversity > 0.8:
                        insights_text += f"• {col}: מגוון גבוה מאוד - {len(value_counts)} ערכים ייחודיים\n"
                        insights_text += f"  - 💡 מתאים לניתוח דפוסים מתקדמים\n"
                    elif diversity > 0.5:
                        insights_text += f"• {col}: מגוון בינוני - {len(value_counts)} ערכים ייחודיים\n"
                        insights_text += f"  - 💡 מתאים לניתוח סגמנטי\n"
                    else:
                        insights_text += f"• {col}: מגוון נמוך - {len(value_counts)} ערכים ייחודיים\n"
                        insights_text += f"  - 💡 מתאים לניתוח השוואתי\n"
                    
                    # Находим доминирующую категорию
                    dominant = value_counts.iloc[0]
                    dominant_percentage = (dominant / len(df)) * 100
                    if dominant_percentage > 50:
                        insights_text += f"  - קטגוריה דומיננטית: {value_counts.index[0]} ({dominant_percentage:.1f}%)\n"
                        if dominant_percentage > 80:
                            insights_text += f"    ⚠️ דומיננטיות גבוהה מאוד - ייתכן בעיה באיסוף נתונים\n"
                
                insights_text += "\n"
            
            # 5. Рекомендации по улучшению данных
            insights_text += "**💡 המלצות לשיפור הנתונים:**\n"
            
            # Проверка на пропущенные значения
            total_nulls = df.isnull().sum().sum()
            total_cells = len(df) * len(df.columns)
            if total_nulls > 0:
                null_percentage = (total_nulls / total_cells) * 100
                insights_text += f"• ערכים חסרים: {total_nulls:,} ({null_percentage:.1f}% מהנתונים)\n"
                if null_percentage > 20:
                    insights_text += f"  - ⚠️ אחוז גבוה - בדוק את מקור הנתונים או השתמש בשיטות השלמה מתקדמות\n"
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
            
            # Рекомендации по типам данных
            conversion_recommendations = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Проверяем, можно ли конвертировать в числовой тип
                    try:
                        pd.to_numeric(df[col], errors='raise')
                        conversion_recommendations.append(col)
                    except:
                        pass
            
            if conversion_recommendations:
                insights_text += f"• עמודות להמרה מספרית: {', '.join(conversion_recommendations)}\n"
                insights_text += f"  - המלצה: המר לטיפוס מספרי לניתוח מתקדם יותר\n"
            
            insights_text += "\n"
            
            # 6. Бизнес-инсайты
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
                
                # Анализ трендов (если есть временные колонки)
                date_cols = [col for col in numeric_cols if any(keyword in col.lower() for keyword in ['date', 'time', 'year', 'month', 'day'])]
                if date_cols:
                    insights_text += f"• עמודות זמן זוהו: {', '.join(date_cols)}\n"
                    insights_text += f"  - 💡 מתאים לניתוח טרנדים וזמן\n"
            
            if len(categorical_cols) > 0:
                # Анализ сегментации
                for col in categorical_cols[:1]:
                    if df[col].nunique() <= 10:  # Не слишком много категорий
                        insights_text += f"• {col} מתאים לניתוח סגמנטי\n"
                        insights_text += f"  - 💡 שקול לנתח ביצועים לפי קטגוריות\n"
                        insights_text += f"  - 💡 מתאים ליצירת דשבורדים עסקיים\n"
            
            # 7. Рекомендации по дальнейшему анализу
            insights_text += "\n**🎯 המלצות לניתוח נוסף:**\n"
            if len(numeric_cols) > 1:
                insights_text += "• ניתוח רגרסיה לזיהוי גורמים משפיעים\n"
                insights_text += "• ניתוח אשכולות (Clustering) לזיהוי דפוסים\n"
            if len(categorical_cols) > 0:
                insights_text += "• ניתוח ANOVA להשוואה בין קבוצות\n"
                insights_text += "• ניתוח Chi-Square לבדיקת קשרים\n"
            
            # === ניתוח ML (רגרסיה/סיווג + קלאסטרינג) ===
            try:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                ml_msgs = []
                if len(numeric_cols) >= 2:
                    clean = df[numeric_cols].dropna()
                    if len(clean) >= 30:
                        # יעד לרגרסיה: ננסה לזהות לפי שם, אחרת נבחר בעל שונות גבוהה
                        target_candidates = [c for c in clean.columns if any(k in c.lower() for k in ['target','label','y','revenue','sales','price','amount'])]
                        y_col = target_candidates[0] if target_candidates else clean.var().sort_values(ascending=False).index[0]
                        X_cols = [c for c in clean.columns if c != y_col]
                        X = clean[X_cols].values
                        y = clean[y_col].values
                        
                        scaler = StandardScaler()
                        Xs = scaler.fit_transform(X)
                        
                        X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.25, random_state=42)
                        
                        # רגרסיה יער אקראי
                        rf = RandomForestRegressor(n_estimators=120, random_state=42)
                        rf.fit(X_train, y_train)
                        r2 = r2_score(y_test, rf.predict(X_test))
                        importances = rf.feature_importances_
                        top_idx = np.argsort(importances)[::-1][:5]
                        top_feats = ", ".join([f"{X_cols[i]} ({importances[i]:.3f})" for i in top_idx])
                        ml_msgs.append(f"• רגרסיה (יעד: {y_col}) — R²={r2:.3f}. תכונות מובילות: {top_feats}")
                        
                        # קלאסטרינג KMeans
                        k = 3
                        km = KMeans(n_clusters=k, n_init=10, random_state=42)
                        labels = km.fit_predict(Xs)
                        sizes = pd.Series(labels).value_counts().sort_index().tolist()
                        ml_msgs.append(f"• קלאסטרינג KMeans (k={k}) — גדלים: {sizes}")
                if ml_msgs:
                    insights_text += "\n".join(["🔬 ניתוח ML:"] + ml_msgs) + "\n\n"
            except Exception:
                logging.exception("ML analysis failed")
            
            # === A/B Testing ===
            try:
                ab_msgs = []
                # עמודת קבוצה
                group_col = None
                for col in df.columns:
                    if df[col].nunique() == 2 and any(k in col.lower() for k in ['group','variant','test','bucket','arm','exposure','experiment']):
                        group_col = col
                        break
                if group_col is None:
                    # נסה למצוא דו-ערכית כללית
                    for col in df.select_dtypes(include=['object']).columns:
                        if df[col].nunique() == 2:
                            group_col = col
                            break
                if group_col is not None:
                    # תוצא דו-ערכי להמרה
                    bin_cols = []
                    for col in df.columns:
                        if col == group_col:
                            continue
                        series = pd.to_numeric(df[col], errors='coerce')
                        # נחשב אם 0/1 או שיעור 0..1
                        unique_vals = pd.Series(series.dropna().unique())
                        if len(unique_vals) > 0 and unique_vals.isin([0,1]).all():
                            bin_cols.append(col)
                    
                    if bin_cols:
                        outcome = bin_cols[0]
                        g_vals = df[group_col].dropna().unique().tolist()
                        if len(g_vals) == 2:
                            g1, g2 = g_vals[0], g_vals[1]
                            g1_mask = df[group_col] == g1
                            g2_mask = df[group_col] == g2
                            x1 = pd.to_numeric(df.loc[g1_mask, outcome], errors='coerce')
                            x2 = pd.to_numeric(df.loc[g2_mask, outcome], errors='coerce')
                            x1 = x1.dropna()
                            x2 = x2.dropna()
                            if len(x1) > 10 and len(x2) > 10:
                                p1 = x1.mean()
                                p2 = x2.mean()
                                n1 = len(x1)
                                n2 = len(x2)
                                p_pool = (x1.sum() + x2.sum()) / (n1 + n2)
                                se = float(np.sqrt(p_pool * (1 - p_pool) * (1.0/n1 + 1.0/n2)))
                                se = se if se != 0 else 1e-9
                                z = (p1 - p2) / se
                                p_val = 2 * (1 - stats.norm.cdf(abs(z)))
                                ab_msgs.append(f"• מבחן שיעורים (קבוצה {g1} מול {g2}, תוצא {outcome}) — p={p_val:.4f}, המרה: {p1:.3f} מול {p2:.3f}")
                    else:
                        # תוצא רציף — t-test
                        metric_col = None
                        cand = [c for c in df.select_dtypes(include=[np.number]).columns if c != group_col]
                        if cand:
                            metric_col = cand[0]
                            g_vals = df[group_col].dropna().unique().tolist()
                            if len(g_vals) == 2:
                                g1, g2 = g_vals[0], g_vals[1]
                                x1 = pd.to_numeric(df.loc[df[group_col]==g1, metric_col], errors='coerce').dropna()
                                x2 = pd.to_numeric(df.loc[df[group_col]==g2, metric_col], errors='coerce').dropna()
                                if len(x1) > 10 and len(x2) > 10:
                                    t_stat, p_val = stats.ttest_ind(x1, x2, equal_var=False)
                                    ab_msgs.append(f"• t-test (מדד {metric_col}, {g1} מול {g2}) — p={p_val:.4f}, ממוצעים: {x1.mean():.2f} מול {x2.mean():.2f}")
                if ab_msgs:
                    insights_text += "\n".join(["🧪 A/B Testing:"] + ab_msgs) + "\n\n"
            except Exception:
                logging.exception("AB analysis failed")
            
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
                "🎯 התובנות וההמלצות הושלמו! עכשיו יש לך תמונה מלאה של הנתונים שלך."
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
    BOT_TOKEN = "REDACTED"
    
    try:
        # Avoid Unicode in Windows CP1251 console
        print("Starting Simple Hebrew Bot...")
        bot = SimpleHebrewBot(BOT_TOKEN)
        print("Bot created successfully!")
        print("Starting bot...")
        print("Now find the bot in Telegram and send /start")
        print("You can now upload CSV/Excel files!")
        print("Full analytics, charts, and insights are now available!")
        
        bot.run()
        
    except Exception as e:
        print(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
