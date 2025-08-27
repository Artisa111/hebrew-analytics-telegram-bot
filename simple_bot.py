# -*- coding: utf-8 -*-
"""
Simple bot for testing with advanced PDF generation
Hebrew Telegram bot for data analysis with comprehensive reporting capabilities
"""

# IMPORT SECTION - All necessary libraries for the bot functionality
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
import arabic_reshaper
from bidi.algorithm import get_display

def _hebrew_text(text: str) -> str:
    """
    Shape and reorder text for proper Hebrew RTL display in matplotlib.
    Only applies shaping when Hebrew characters are present.
    """
    try:
        if text is None:
            return ""
        s = str(text)
        if any('\u0590' <= ch <= '\u05FF' for ch in s):
            return get_display(arabic_reshaper.reshape(s))
        return s
    except Exception:
        return str(text)

def _hebrew_list(values) -> list:
    """Apply _hebrew_text to each element of an iterable for tick/label lists."""
    try:
        return [_hebrew_text(v) for v in list(values)]
    except Exception:
        return [str(v) for v in list(values)]

# ENHANCED CHART GENERATOR SECTION
# This section contains an embedded enhanced chart generator that doesn't require external modules
def get_enhanced_chart_generator():  # noqa: N802 - keep external API name
    """
    Factory function that returns an enhanced chart generator instance.
    This creates comprehensive dashboards with multiple chart types.
    """
    class EnhancedChartGenerator:
        def create_comprehensive_dashboard(self, df, analysis_results=None, output_dir=None):
            """
            Creates a comprehensive dashboard with multiple chart types including:
            - Statistical summary tables
            - Bar charts for categorical data
            - Histograms for numerical data
            - Box plots and violin plots
            - Scatter plots with trend lines
            - Correlation heatmaps
            - Time series charts
            - Missing value analysis
            """
            try:
                # Setup output directory for charts
                out_dir = output_dir or os.path.join(os.getcwd(), 'temp_charts')
                os.makedirs(out_dir, exist_ok=True)
                chart_files = []
                generated_signatures = set()

                def add_chart(path: str, signature: str):
                    """Helper function to add chart to list if not already generated"""
                    if not path:
                        return
                    if signature in generated_signatures:
                        return
                    generated_signatures.add(signature)
                    chart_files.append(path)

                # Identify column types for appropriate chart selection
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                categorical_cols = df.select_dtypes(include=['object']).columns

                # CHART TYPE 1: Statistical Summary Table (Hebrew labels)
                try:
                    if len(numeric_cols) > 0:
                        # Generate comprehensive statistics
                        summary = df[numeric_cols].describe(percentiles=[0.25, 0.5, 0.75]).T
                        cols_order = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
                        summary = summary[[c for c in cols_order if c in summary.columns]]
                        
                        # Hebrew translation of statistical terms
                        summary = summary.rename(columns={
                            'count': 'ספירה',
                            'mean': 'ממוצע',
                            'std': 'סטיית תקן',
                            'min': 'מינימום',
                            '25%': 'רבעון ראשון',
                            '50%': 'חציון',
                            '75%': 'רבעון שלישי',
                            'max': 'מקסימום'
                        })
                        
                        # Limit rows for better visualization
                        max_rows = 18
                        if len(summary) > max_rows:
                            summary = summary.head(max_rows)
                        
                        # Format numeric values for display
                        def _format_value(val):
                            try:
                                return f"{float(val):,.2f}".replace(',', ',')
                            except Exception:
                                return str(val)
                        
                        formatted = summary.copy()
                        for col in formatted.columns:
                            formatted[col] = formatted[col].apply(_format_value)
                        
                        # Create table visualization
                        n_rows, n_cols = formatted.shape
                        fig_width = min(20, 2 + 1.2 * n_cols)
                        fig_height = min(14, 2 + 0.55 * n_rows)
                        plt.figure(figsize=(fig_width, fig_height))
                        plt.axis('off')
                        plt.title(_hebrew_text('סיכום סטטיסטי'), fontsize=16, fontweight='bold', pad=20)
                        
                        # Create formatted table
                        table = plt.table(
                            cellText=formatted.values,
                            colLabels=_hebrew_list([str(c) for c in formatted.columns]),
                            rowLabels=_hebrew_list([str(r) for r in formatted.index]),
                            cellLoc='right',
                            loc='center'
                        )
                        table.auto_set_font_size(False)
                        table.set_fontsize(10)
                        table.scale(1, 1.2)
                        for (_, _), cell in table.get_celld().items():
                            cell.set_text_props(ha='right')
                        
                        # Style the table
                        for key, cell in table.get_celld().items():
                            row, col = key
                            if row == 0:  # Header row
                                cell.set_facecolor('#e0f2e9')
                                cell.set_edgecolor('#5aa469')
                                cell.set_linewidth(1)
                            if col == -1:  # Row labels
                                cell.set_facecolor('#f3f6fa')
                        
                        path = os.path.join(out_dir, 'statistical_summary.png')
                        plt.tight_layout()
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, 'table:statistical_summary')
                except Exception:
                    pass

                # CHART TYPE 2: Top Categories Bar Charts (up to 3 categorical columns)
                try:
                    for col in list(categorical_cols)[:3]:
                        top_vals = df[col].value_counts().head(10)
                        if not top_vals.empty:
                            total = int(top_vals.sum())
                            plt.figure(figsize=(10, 6))
                            bars = plt.bar(range(len(top_vals)), top_vals.values)
                            plt.xticks(range(len(top_vals)), _hebrew_list([str(v) for v in top_vals.index]), rotation=45, ha='right')
                            plt.title(_hebrew_text(f'קטגוריות מובילות: {col}'))
                            plt.ylabel(_hebrew_text('תדירות'))
                            
                            # Add percentage labels on bars
                            for i, b in enumerate(bars):
                                cnt = int(top_vals.values[i])
                                pct = (cnt / total) * 100 if total > 0 else 0
                                plt.text(b.get_x() + b.get_width()/2, b.get_height(), f"{cnt} ({pct:.1f}%)",
                                         ha='center', va='bottom', fontsize=9)
                            
                            plt.tight_layout()
                            path = os.path.join(out_dir, f'top_categories_{col}.png')
                            plt.savefig(path, dpi=220, bbox_inches='tight')
                            plt.close()
                            add_chart(path, f"topcat:{col}")
                except Exception:
                    pass

                # CHART TYPE 3: Histogram for first numeric column
                try:
                    if len(numeric_cols) > 0:
                        col = numeric_cols[0]
                        plt.figure(figsize=(9, 6))
                        plt.hist(df[col].dropna(), bins=30, alpha=0.8)
                        plt.title(_hebrew_text(f'היסטוגרמה: {col}'))
                        plt.tight_layout()
                        path = os.path.join(out_dir, f'histogram_{col}.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, f"hist:{col}")
                except Exception:
                    pass

                # CHART TYPE 4: Box Plot (horizontal, consolidated)
                try:
                    if len(numeric_cols) > 0:
                        plt.figure(figsize=(12, 6))
                        sns.boxplot(data=df[numeric_cols], orient='h', showfliers=False)
                        plt.title(_hebrew_text('תרשים קופסאות לעמודות מספריות'))
                        plt.tight_layout()
                        path = os.path.join(out_dir, 'box_plot.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, 'box:all')
                except Exception:
                    pass

                # CHART TYPE 5: Violin Plot for up to 6 numeric columns
                try:
                    if len(numeric_cols) > 1:
                        selected = list(numeric_cols)[:6]
                        data_to_plot = [df[c].dropna().values for c in selected]
                        plt.figure(figsize=(12, 6))
                        parts = plt.violinplot(data_to_plot, showmeans=True, showextrema=False)
                        plt.xticks(range(1, len(selected)+1), _hebrew_list([str(s) for s in selected]), rotation=30, ha='right')
                        plt.title(_hebrew_text('תרשים כינור לעמודות נבחרות'))
                        plt.tight_layout()
                        path = os.path.join(out_dir, 'violin_plot.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, 'violin:all')
                except Exception:
                    pass

                # CHART TYPE 6: Scatter Plot for two numeric columns with regression line
                try:
                    if len(numeric_cols) > 1:
                        x, y = numeric_cols[:2]
                        plt.figure(figsize=(9, 6))
                        sns.regplot(x=df[x], y=df[y], scatter_kws={'alpha': 0.5})
                        plt.title(_hebrew_text(f'תרשים פיזור: {x} מול {y}'))
                        plt.tight_layout()
                        path = os.path.join(out_dir, f'scatter_plot_{x}_vs_{y}.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, f"scatter:{x}:{y}")
                except Exception:
                    pass

                # CHART TYPE 7: Correlation Heatmap
                try:
                    if len(numeric_cols) > 1:
                        corr = df[numeric_cols].corr()
                        plt.figure(figsize=(10, 8))
                        sns.heatmap(corr, annot=False, cmap='coolwarm', center=0)
                        plt.title(_hebrew_text('מפת קורלציה'))
                        plt.tight_layout()
                        path = os.path.join(out_dir, 'correlation_heatmap.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, 'heatmap:corr')
                except Exception:
                    pass

                # CHART TYPE 8: Pairplot for up to 4 numeric columns
                try:
                    if len(numeric_cols) > 1:
                        subset = list(numeric_cols)[:4]
                        g = sns.pairplot(df[subset].dropna())
                        g.fig.suptitle(_hebrew_text('Pairplot - קשרים בין עמודות'), y=1.02)
                        path = os.path.join(out_dir, 'pairplot.png')
                        g.fig.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close('all')
                        add_chart(path, 'pairplot:subset')
                except Exception:
                    pass

                # CHART TYPE 9: Missing Values Analysis
                try:
                    total_missing = df.isnull().sum().sum()
                    if total_missing > 0:
                        missing = df.isnull().sum()
                        missing = missing[missing > 0].sort_values(ascending=False).head(20)
                        plt.figure(figsize=(12, 6))
                        plt.bar(range(len(missing)), missing.values)
                        plt.xticks(range(len(missing)), _hebrew_list([str(v) for v in missing.index]), rotation=45, ha='right')
                        plt.title(_hebrew_text('ערכים חסרים לפי עמודה'))
                        plt.ylabel(_hebrew_text('כמות ערכים חסרים'))
                        plt.tight_layout()
                        path = os.path.join(out_dir, 'missing_values.png')
                        plt.savefig(path, dpi=220, bbox_inches='tight')
                        plt.close()
                        add_chart(path, 'missing:per_col')
                except Exception:
                    pass

                # CHART TYPE 10: Time Series Area Chart (if datetime columns exist)
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
                            plt.title(_hebrew_text('תרשים שטח - ספירת רשומות לפי יום'))
                            plt.tight_layout()
                            path = os.path.join(out_dir, 'area_chart_timeseries.png')
                            plt.savefig(path, dpi=220, bbox_inches='tight')
                            plt.close()
                            add_chart(path, 'area:counts_by_day')
                except Exception:
                    pass

                # CHART TYPE 11: Time Series Line Chart (numeric mean by day)
                try:
                    dt_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
                    if len(dt_cols) > 0 and len(numeric_cols) > 0:
                        dt_col = dt_cols[0]
                        num_col = numeric_cols[0]
                        tmp = df[[dt_col, num_col]].dropna()
                        if not tmp.empty:
                            daily = tmp.groupby(tmp[dt_col].dt.to_period('D'))[num_col].mean().sort_index()
                            x = range(len(daily))
                            plt.figure(figsize=(12, 5))
                            plt.plot(x, daily.values, marker='o')
                            plt.xticks(x[::max(1, len(x)//10)], [str(p) for p in daily.index[::max(1, len(x)//10)]], rotation=45, ha='right')
                            plt.title(_hebrew_text(f'ממוצע יומי: {num_col}'))
                            plt.tight_layout()
                            path = os.path.join(out_dir, 'line_timeseries.png')
                            plt.savefig(path, dpi=220, bbox_inches='tight')
                            plt.close()
                            add_chart(path, f"line:mean_by_day:{num_col}")
                except Exception:
                    pass

                return chart_files
            except Exception:
                return []

    return EnhancedChartGenerator()

# LOGGING CONFIGURATION SECTION
# Setup logging with split handlers: INFO and below to stdout, WARNING+ to stderr
class _MaxLevelFilter(logging.Filter):
    """Custom filter to limit log levels to a maximum threshold"""
    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level
    
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level

def _configure_logging() -> logging.Logger:
    """
    Configure logging with split handlers for better output management:
    - stdout: DEBUG to INFO level messages
    - stderr: WARNING level and above
    """
    logger = logging.getLogger()
    if getattr(logger, "_configured_split_handlers", False):
        return logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler for stdout: up to INFO level
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

# Initialize logger
logger = _configure_logging()

# MATPLOTLIB HEBREW FONT CONFIGURATION
# Configure matplotlib to support Hebrew text rendering
plt.rcParams['font.family'] = ['Noto Sans Hebrew', 'DejaVu Sans', 'Arial Unicode MS', 'Arial', 'Tahoma', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# MAIN BOT CLASS SECTION
class SimpleHebrewBot:
    """
    Main Telegram bot class for Hebrew data analysis.
    Provides comprehensive data analysis capabilities including:
    - File upload and processing (CSV, Excel)
    - Statistical analysis
    - Chart generation
    - Insights and recommendations
    - PDF report generation (regular and advanced)
    """
    
    def __init__(self, bot_token: str):
        """Initialize the bot with token and setup handlers"""
        self.application = Application.builder().token(bot_token).job_queue(None).persistence(None).build()
        self.user_data = {}  # Simple user data storage
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command - welcome message and keyboard setup
        Initializes user data and provides main navigation keyboard
        """
        user = update.effective_user
        user_id = user.id
        
        # Initialize user data storage
        self.user_data[user_id] = {
            'data': None,
            'file_name': None,
            'analysis_done': False
        }
        
        welcome_text = f"ברוך הבא {user.first_name}! 🎉\n\nאני בוט ניתוח נתונים בעברית.\n\n📁 שלח לי קובץ CSV או Excel כדי להתחיל!"
        
        # Create main navigation keyboard
        keyboard = [
            ['📊 ניתוח נתונים'],
            ['📈 תרשימים'],
            ['💡 תובנות והמלצות'],
            ['📄 דוח PDF', '📊 דוח PDF מתקדם'],  # Two PDF options
            ['📁 העלאת קובץ'],
            ['❓ עזרה']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command - comprehensive help information"""
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
        """Check if user has valid data loaded"""
        if user_id not in self.user_data:
            return False
        data = self.user_data[user_id].get('data')
        return data is not None and isinstance(data, pd.DataFrame) and not data.empty
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle file uploads - process CSV and Excel files
        Supports multiple encodings and file formats with validation
        """
        user_id = update.effective_user.id
        document = update.message.document
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {'data': None, 'file_name': None, 'analysis_done': False}
        
        # Validate file type
        file_name = document.file_name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        supported_formats = ['.csv', '.xlsx', '.xls']
        if file_extension not in supported_formats:
            await update.message.reply_text(
                f"❌ סוג קובץ לא נתמך: {file_extension}\n\nהקבצים הנתמכים: {', '.join(supported_formats)}"
            )
            return
        
        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if document.file_size > max_size:
            await update.message.reply_text(
                f"❌ הקובץ גדול מדי: {document.file_size // (1024*1024)}MB\n\nהגודל המקסימלי: 50MB"
            )
            return
        
        await update.message.reply_text("📁 קובץ התקבל! מעבד...")
        
        try:
            # Download file
            file = await context.bot.get_file(document.file_id)
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file_name)
            
            # Download file to temporary location
            await file.download_to_drive(file_path)
            
            # Read data file with appropriate method
            df = await self.read_data_file(file_path, file_extension)
            
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                # Store user data
                self.user_data[user_id].update({
                    'data': df,
                    'file_name': file_name,
                    'analysis_done': False
                })
                
                # Display file information
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
                
                # Show preview of first few rows
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
            # Clean up temporary directory
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def read_data_file(self, file_path: str, file_extension: str):
        """
        Read data files with support for multiple encodings and formats
        Handles CSV with various encodings and Excel files
        """
        try:
            if file_extension == '.csv':
                # Try different encodings for CSV files
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
        """
        Handle text messages - main navigation and feature routing
        Routes user requests to appropriate analysis functions
        """
        user_id = update.effective_user.id
        text = update.message.text
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {'data': None, 'file_name': None, 'analysis_done': False}
        
        # Route to appropriate handlers based on user selection
        if text == '📊 ניתוח נתונים':
            await self.handle_analyze_data(update, context)
        
        elif text == '📈 תרשימים':
            await self.handle_charts(update, context)
        
        elif text == '💡 תובנות והמלצות':
            await self.handle_insights(update, context)

        elif text == '📄 דוח PDF':
            # Regular PDF report (legacy)
            if not self.has_data(user_id):
                await update.message.reply_text("❌ אין נתונים לדוח! שלח קובץ תחילה.")
                return
            
            await update.message.reply_text("🖨️ יוצר דוח PDF רגיל בעברית…")
            
            try:
                df = self.user_data[user_id]['data']
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                # Basic analysis results for report
                analysis_results = {
                    'basic_info': {
                        'shape': df.shape,
                        'memory_usage': df.memory_usage(deep=True).sum(),
                        'null_counts': df.isnull().sum().to_dict(),
                    }
                }
                
                # Add correlation matrix if available
                if len(numeric_cols) > 1:
                    analysis_results['correlation_matrix'] = df[numeric_cols].corr()
                
                # Reuse existing charts if available; otherwise create basic histogram
                chart_dir = os.path.join(os.getcwd(), 'temp_charts')
                chart_files = []
                if os.path.isdir(chart_dir):
                    for name in os.listdir(chart_dir):
                        if name.lower().endswith('.png'):
                            chart_files.append(os.path.join(chart_dir, name))
                
                # Create quick histogram if no charts exist
                if not chart_files and len(numeric_cols) > 0:
                    import matplotlib.pyplot as plt
                    path = os.path.join(chart_dir, 'pdf_quick_hist.png')
                    os.makedirs(chart_dir, exist_ok=True)
                    plt.hist(df[numeric_cols[0]].dropna(), bins=25)
                    plt.title(str(numeric_cols[0]))
                    plt.savefig(path, dpi=200)
                    plt.close()
                    chart_files.append(path)

                # Generate PDF report
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
            # Advanced PDF report (new and enhanced)
            if not self.has_data(user_id):
                await update.message.reply_text("❌ אין נתונים לדוח מתקדם! שלח קובץ תחילה.")
                return
            
            await update.message.reply_text("🚀 יוצר דוח PDF מתקדם בעברית עם ניתוח מקיף וגרפים מקצועיים…")
            
            try:
                df = self.user_data[user_id]['data']
                file_name = self.user_data[user_id]['file_name']
                
                # Create customized filename
                base_name = os.path.splitext(file_name)[0] if file_name else "נתונים"
                out_path = os.path.join(os.getcwd(), f'דוח_מתקדם_{base_name}.pdf')
                
                # Use enhanced report generation function
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
                    
                    # Follow-up message
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
            # Default response for unrecognized messages
            await update.message.reply_text(
                "לא הבנתי את ההודעה שלך. 🤔\n\n"
                "אנא השתמש בכפתורים שלמטה או שלח /help לעזרה מפורטת.\n\n"
                "💡 אם יש לך קובץ נתונים - פשוט שלח אותו לי!"
            )
    
    async def handle_analyze_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle comprehensive data analysis request
        Provides detailed statistical analysis including:
        - Basic information (rows, columns, data types)
        - Detailed statistics for numeric columns
        - Categorical data analysis
        - Data quality assessment
        - Missing values analysis
        """
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
            
            # Basic analysis header
            analysis_text = f"🔍 **ניתוח מפורט: {self.user_data[user_id]['file_name']}**\n\n"
            
            # Basic information section
            rows, cols = df.shape
            analysis_text += f"📊 **מידע בסיסי:**\n"
            analysis_text += f"• מספר שורות: {rows:,}\n"
            analysis_text += f"• מספר עמודות: {cols}\n"
            analysis_text += f"• שם קובץ: {self.user_data[user_id]['file_name']}\n\n"
            
            # Column information and data types
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
            
            # Detailed statistics for numeric columns
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
            
            # Categorical data analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                analysis_text += f"\n**ניתוח קטגוריות:**\n"
                for col in categorical_cols[:3]:  # Limit to first 3 columns
                    value_counts = df[col].value_counts()
                    most_common = value_counts.head(3)
                    analysis_text += f"• {col}:\n"
                    for val, count in most_common.items():
                        percentage = (count / len(df)) * 100
                        analysis_text += f"  - {val}: {count} ({percentage:.1f}%)\n"
            
            # Duplicate analysis
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                analysis_text += f"\n**⚠️ אזהרות:**\n"
                analysis_text += f"• נמצאו {duplicates} שורות כפולות\n"
            
            # Data quality analysis
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
            
            # Split long messages into parts
            if len(analysis_text) > 4000:
                parts = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text(f"📊 המשך הניתוח (חלק {i+1}):\n\n{part}", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(analysis_text, parse_mode=ParseMode.MARKDOWN)
            
            # Next steps message
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
        """
        Handle chart generation request - creates professional charts using enhanced generator
        Uses the embedded enhanced chart generator to create comprehensive visualizations:
        - Statistical summary tables
        - Various chart types (bar, histogram, scatter, box, violin, etc.)
        - Correlation analysis
        - Time series analysis
        - Missing value visualization
        """
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
            
            # Use enhanced chart generator
            enhanced_generator = get_enhanced_chart_generator()
            
            # Create basic analysis for charts
            analysis_results = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                analysis_results['correlation_matrix'] = df[numeric_cols].corr()
            
            # Generate comprehensive dashboard with all enhanced chart types
            chart_files = enhanced_generator.create_comprehensive_dashboard(df, analysis_results)
            
            # Send charts to user
            if chart_files:
                await update.message.reply_text(f"✅ נוצרו {len(chart_files)} תרשימים מקצועיים עם המחולל המשופר!")
                
                # Enhanced chart types mapping (Hebrew + English)
                enhanced_chart_types = {
                    'statistical_summary': '📋 סיכום סטטיסטי',
                    'bar_chart': '📊 תרשים עמודות משופר',
                    'histogram': '📊 היסטוגרמה עם סטטיסטיקות',
                    'scatter_plot': '🔵 תרשים פיזור עם מגמה',
                    'box_plot': '📦 תרשים קופסה עם נתונים',
                    'pie_chart': '🥧 תרשים עוגה עם מקרא',
                    'violin_plot': '🎻 תרשים כינור',
                    'correlation_heatmap': '🔥 מפת קורלציה',
                    'area_chart': '🏔️ תרשים שטח',
                    'radar_chart': '📡 תרשים רדאר',
                    'treemap': '🌳 מפת עץ',
                    'pairplot': '🔗 זוגות משתנים (Pairplot)',
                    'missing_values': '❗ ערכים חסרים לפי עמודה',
                    'line_timeseries': '📈 ממוצע יומי',
                    'top_categories_': '📊 קטגוריות מובילות'
                }
                enhanced_chart_types_en = {
                    'statistical_summary': 'Statistical summary',
                    'bar_chart': 'Bar chart',
                    'histogram': 'Histogram with stats',
                    'scatter_plot': 'Scatter plot with trend',
                    'box_plot': 'Box plot',
                    'pie_chart': 'Pie chart',
                    'violin_plot': 'Violin plot',
                    'correlation_heatmap': 'Correlation heatmap',
                    'area_chart': 'Area chart',
                    'radar_chart': 'Radar chart',
                    'treemap': 'Treemap',
                    'pairplot': 'Pairplot',
                    'missing_values': 'Missing values by column',
                    'line_timeseries': 'Daily average',
                    'top_categories_': 'Top categories'
                }
                
                # Send each chart with appropriate caption
                for i, chart_file in enumerate(chart_files):
                    try:
                        with open(chart_file, 'rb') as img_file:
                            # Identify chart type from filename
                            filename = os.path.basename(chart_file)
                            chart_type_he = "תרשים מקצועי משופר"
                            chart_type_en = "Professional chart"
                            for key, value in enhanced_chart_types.items():
                                if key in filename:
                                    chart_type_he = value
                                    chart_type_en = enhanced_chart_types_en.get(key, chart_type_en)
                                    break
                            
                            caption = (
                                f"{chart_type_he}\n{chart_type_en}\n\n"
                                f"✨ נוצר עם מחולל התרשימים המשופר\n"
                                f"🎨 כולל תוויות בעברית ועיצוב מקצועי"
                            )
                            
                            await context.bot.send_photo(
                                chat_id=update.effective_chat.id,
                                photo=img_file,
                                caption=caption
                            )
                    except Exception as e:
                        logger.error(f"Error sending enhanced chart {chart_file}: {e}")
                        await update.message.reply_text(f"❌ שגיאה בשליחת תרשים {i+1}")
                
                # Final summary message
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
        """
        Handle insights and recommendations request
        Provides advanced insights including:
        - Correlation analysis
        - Outlier detection
        - Data quality recommendations
        - Business insights
        - Further analysis suggestions
        """
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
            
            # 1. Correlation Analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                insights_text += "**🔗 ניתוח קורלציות:**\n"
                correlation_matrix = df[numeric_cols].corr()
                
                # Find top 5 correlations
                correlations = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        col1, col2 = numeric_cols[i], numeric_cols[j]
                        corr_value = correlation_matrix.loc[col1, col2]
                        if not pd.isna(corr_value):
                            correlations.append((col1, col2, abs(corr_value)))
                
                # Sort by correlation strength
                correlations.sort(key=lambda x: x[2], reverse=True)
                
                for i, (col1, col2, corr_abs) in enumerate(correlations[:5]):
                    corr_value = correlation_matrix.loc[col1, col2]
                    insights_text += f"• {col1} ↔ {col2}: {corr_value:.3f}\n"
                
                insights_text += "\n"
            
            # 2. Outlier Analysis
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
            
            # 3. Data Quality Recommendations
            insights_text += "**💡 המלצות לשיפור הנתונים:**\n"
            
            # Check for missing values
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
            
            # Check for duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                duplicate_percentage = (duplicates / len(df)) * 100
                insights_text += f"• שורות כפולות: {duplicates:,} ({duplicate_percentage:.1f}%)\n"
                insights_text += f"  - המלצה: הסר כפילויות לפני הניתוח\n"
            
            insights_text += "\n"
            
            # 4. Business Insights
            insights_text += "**🚀 תובנות עסקיות:**\n"
            
            if len(numeric_cols) > 0:
                # Find column with maximum variability
                max_var_col = numeric_cols[0]
                max_variance = df[max_var_col].var()
                for col in numeric_cols:
                    if df[col].var() > max_variance:
                        max_variance = df[col].var()
                        max_var_col = col
                
                insights_text += f"• העמודה {max_var_col} מראה את השונות הגבוהה ביותר\n"
                insights_text += f"  - זה עשוי להצביע על הזדמנויות או סיכונים עסקיים\n"
            
            # 5. Recommendations for further analysis
            insights_text += "\n**🎯 המלצות לניתוח נוסף:**\n"
            if len(numeric_cols) > 1:
                insights_text += "• ניתוח רגרסיה לזיהוי גורמים משפיעים\n"
                insights_text += "• ניתוח אשכולות (Clustering) לזיהוי דפוסים\n"
            if len(df.select_dtypes(include=['object']).columns) > 0:
                insights_text += "• ניתוח ANOVA להשוואה בין קבוצות\n"
                insights_text += "• ניתוח Chi-Square לבדיקת קשרים\n"
            
            # Split long messages into parts
            if len(insights_text) > 4000:
                parts = [insights_text[i:i+4000] for i in range(0, len(insights_text), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
                    else:
                        await update.message.reply_text(f"💡 המשך התובנות (חלק {i+1}):\n\n{part}", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(insights_text, parse_mode=ParseMode.MARKDOWN)
            
            # Final recommendations message
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
        """
        Start the bot - main execution method
        Runs the Telegram bot in polling mode to continuously check for new messages
        """
        logger.info("Starting Simple Hebrew Bot...")
        self.application.run_polling()

# MAIN EXECUTION SECTION
def main():
    """
    Main function - entry point of the application
    Gets bot token from environment variables and starts the bot
    """
    import os
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not found!")
        print("Please set the BOT_TOKEN environment variable with your Telegram bot token.")
        return
    
    try:
        # Create and start the bot
        bot = SimpleHebrewBot(BOT_TOKEN)
        logger.info("Bot initialized successfully")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()