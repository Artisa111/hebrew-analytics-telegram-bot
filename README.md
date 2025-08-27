## Hebrew Data Analytics Telegram Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateUrl=https://github.com/Artisa111/hebrew-analytics-telegram-bot)

Production-ready Telegram bot for automated data analytics, fully localized to Hebrew (RTL). Upload CSV/Excel/Google Sheets and get analysis, charts, insights, and a polished PDF report.

### Key Features
- File input: CSV, Excel (.xlsx), Google Sheets link
- Data quality and descriptive stats (missing values, duplicates, outliers, distributions)
- Visualizations (matplotlib/seaborn): histograms + box plots, bar charts, correlation matrix, scatter plots, KDE, outlier analysis, time trends, statistical summary table
- Funnel analysis with conversion captions per step
- Per-chart insights under every image + actionable guidance
- Insights & Recommendations: correlations, anomalies, distributions, categorical insights, business suggestions, further analyses
- Machine Learning: KMeans clustering, RandomForest regression/classification with metrics and feature importances
- A/B testing: proportions z-test and numeric t-test
- PDF report in Hebrew (RTL) with charts and summaries
- SQLite session storage (optional)

### Tech Stack
- Python 3.11+
- python-telegram-bot ≥ 20
- pandas, numpy, scipy, seaborn, matplotlib
- scikit-learn
- fpdf2 (PDF)
- gspread + oauth2client (optional Google Sheets)

### Project Structure
- simple_bot.py – runnable bot with handlers, analytics, charts, insights
- pdf_report.py – PDF report generation
- requirements.txt – dependencies
- Procfile – Railway worker entrypoint
- runtime.txt – pinned Python version for Railway
- Optional helpers: data_analysis.py, visualization.py, google_sheets.py

## Security and secrets
- Never commit tokens or credentials to the repository. Use environment variables instead.
- Required variable: BOT_TOKEN.
- For local development, create a .env file (not committed) based on env_example.txt.

### Local Run
1) Create a bot via BotFather and copy the token
2) Create venv and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: . .venv/Scripts/activate
pip install -r requirements.txt
```
3) Set env and run:
```bash
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"   # on Windows (PowerShell): $env:BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
python simple_bot.py
```

---

## One-click Railway Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateUrl=https://github.com/Artisa111/hebrew-analytics-telegram-bot)

This project ships with a Procfile and runtime for hassle-free deployment on Railway.

- Procfile:
```
worker: python simple_bot.py
```
- runtime.txt:
```
python-3.11.8
```

### Quick steps
1. Click the Deploy on Railway button above (or create a New Project → Deploy from GitHub → select your fork).
2. In Project Settings → Variables add:
   - BOT_TOKEN = your Telegram token (required)
   - GOOGLE_CREDENTIALS_FILE = path to Google credentials JSON (optional, only if using Google Sheets)
   - MPLBACKEND = Agg (recommended for headless matplotlib)
   - PYTHONUNBUFFERED = 1 (optional, for real-time logs)
3. Deploy. Railway will use the included Procfile and start a Worker.
4. Open Logs — you should see:
   - "Starting Simple Hebrew Bot..."
   - "Bot created successfully!"
   - "Starting bot..."
5. Find your bot in Telegram and send /start. Upload a CSV/Excel and try the Advanced PDF report.

### Notes for Railway
- The bot runs via long polling — no extra web server is required.
- Ensure BOT_TOKEN is set. Without it, the app will exit on startup.
- If you see matplotlib backend/display errors, set MPLBACKEND=Agg.
- Telegram file upload limit for bots is ~50MB.

### Hebrew PDF Font Resolution
The PDF report system uses a robust Hebrew font resolution mechanism with the following priority order:

1. **Repository-bundled fonts**: `assets/fonts/NotoSansHebrew-Regular.ttf` and `assets/fonts/NotoSansHebrew-Bold.ttf`
2. **Environment variable overrides**: `REPORT_FONT_REGULAR` and `REPORT_FONT_BOLD`
3. **System font paths**: Scans common locations on Windows, macOS, and Linux for Hebrew-compatible fonts
4. **Runtime download**: Downloads Noto Sans Hebrew fonts from GitHub if none are found

### Optional Environment Variables
- `BOT_TOKEN`: Telegram bot token (required)
- `MPLBACKEND`: Matplotlib backend (recommend "Agg" for headless environments like Railway)
- `REPORT_LANG`: Report language (default: "he" for Hebrew, can be "en" for English)
- `REPORT_TZ`: Timezone for PDF report dates (default: "Asia/Jerusalem"). Example: "UTC", "America/New_York"
- `REPORT_FONT_REGULAR`: Path to custom regular Hebrew font file
- `REPORT_FONT_BOLD`: Path to custom bold Hebrew font file
- `LOG_LEVEL`: Logging level (default: "INFO", options: "DEBUG", "INFO", "WARNING", "ERROR")
- `LOGS_MAX_PER_SEC`: Rate limit for log messages per second (default: "100")
- `UVICORN_ACCESS_LOG`: Enable/disable Uvicorn access logs (default: "false")

### Font Troubleshooting
The bot logs exactly which fonts are loaded:
- ✅ "Hebrew fonts loaded successfully (regular=..., bold=...)" - Shows actual font paths used
- ⚠️ "Using fallback core font - Hebrew support may be limited" - Hebrew text may not display correctly
- If fonts are missing, the system automatically downloads Noto Sans Hebrew fonts at runtime

---

## Troubleshooting
- Ensure BOT_TOKEN is present in the environment
- Matplotlib font warnings are harmless; charts still render
- If charts fail, check the file columns and types; try a sample CSV

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

## License
MIT — see LICENSE for details.

## Support
- Open a GitHub Issue

## Roadmap
- [ ] Additional file formats (JSON, XML)
- [ ] More advanced ML analyses
- [ ] More export formats
- [ ] Multi-language UI
- [ ] Web interface

---



Disclaimer: This bot is intended for educational and professional use. Handle data responsibly and co
mply with privacy regulations.
   


<div dir="rtl">

## בוט טלגרם לניתוח נתונים בעברית

בוט זה מאפשר להעלות קבצי CSV ולקבל ניתוחים תיאוריים ותרשימים ישירות בטלגרם. הוא משתמש בספריות Python כמו pandas ו‑matplotlib כדי להפיק תובנות מהנתונים ומחזיר את התוצאות בעברית.

### מאפיינים עיקריים
- העלאת קובץ CSV וקבלת הצצה ראשונית (חמש השורות הראשונות).
- חישוב סטטיסטיקות תיאוריות כמו ממוצע, חציון וסיכום עבור שדות נומריים.
- יצירת תרשימי עמודות, היסטוגרמות, תרשימי פיזור ומפת חום כדי להמחיש את התפלגות הנתונים.
- תמיכה מלאה בעברית וטיפול בכיווניות מימין לשמאל.

### טכנולוגיות וספריות
- **Python** – שפת התכנות העיקרית.
- **pandas** – לעיבוד וניתוח נתונים בטבלאות.
- **matplotlib** ו‑**seaborn** – ליצירת תרשימים וגרפים.
- **python‑telegram‑bot** – לסביבת העבודה מול Telegram.

### מבנה הפרויקט
```
bot/       – לוגיקת הבוט וקישור לטלגרם
handlers/  – פונקציות המטפלות באירועים של משתמשים
config.py  – הגדרות קבועות ומפתחות סודיים


requirements.txt – רשימת חבילות להתקנה
analysis/  – פונקציות ניתוח וויזואליזציה
data/      – קבצי נתונים לדוגמה
fonts/     – גופנים לתמיכה בעברית בפורמטים גרפיים
```

### אבטחה וסודות
שמור על הערכים הבאים כמפתחות סודיים במשתני סביבה או בהגדרות שירות האחסון:

- **BOT_TOKEN** – הטוקן של הבוט בטלגרם לקבלת גישה ל‑API.
- **ALLOWED_USERS** – רשימת מזהי משתמשים (IDs) שמורשים להשתמש בבוט, מופרדת בפסיקים.
- **TEAM_DIR** – נתיב לתיקיית הנתונים על השרת.
- **BOT_LANGUAGE** – שפת ברירת המחדל של הבוט (השתמש ב‑`he` לעברית).

### הרצה מקומית
1. שכפל את המאגר באמצעות `git clone ...`.
2. התקן את התלויות עם `pip install -r requirements.txt`.
3. הגדר את משתני הסביבה הדרושים (`BOT_TOKEN`, `ALLOWED_USERS` וכו').
4. הפעל את הבוט עם `python main.py` ושלח קובץ CSV לבוט בטלגרם.

### פריסה ב‑Railway בלחיצה אחת
[![פריסה ב‑Railway](https://railway.app/button.svg)](https://railway.app/new/template?repositoryUrl=https://github.com/Artisa111/hebrew-analytics-telegram-bot)

לחץ על הכפתור לעיל כדי לפרוס את הבוט אוטומטית ב‑Railway. הזן את ה‑`BOT_TOKEN` והמשתמשים המורשים בממשק הסודות של Railway והגדר את `BOT_LANGUAGE` ל‑`he`.

### מנגנון גופנים ל‑PDF
כדי להבטיח שהתווים העבריים יוצגו כראוי בדוחות PDF, הבוט משתמש בגופן **DejaVu Sans Condensed** הכלול בתיקייה `fonts/`. ניתן להחליף את הגופן באמצעות הגדרת המשתנה `PLOT_FONT` לגופן משלכם.

### משתני סביבה אופציונליים
- **PLOT_FONT** – נתיב לגופן TrueType אחר לבניית גרפים ודוחות.
- **LOCALE** – הגדרת אזור (`he_IL.UTF-8` לברירת המחדל בעברית) לשימוש במיקומים ותאריכים.

### פתרון בעיות
- ודא כי `BOT_TOKEN` מוגדר בסביבת ההרצה.
- אזהרות לגבי גופנים של matplotlib הן תקינות; הגרפים עדיין יוצגו.
- אם יצירת תרשימים נכשלת, בדוק את סוגי העמודות בקובץ ונסה להשתמש בקובץ CSV לדוגמה.

### תרומה לפיתוח
אנא בצעו *fork* למאגר, צרו ענף (branch) חדש לשינויים שלכם, בצעו commit ושלחו בקשת משיכה (Pull Request). נשמח לקבל תרומות לשיפור הפונקציונליות ותוספת יכולות חדשות.

### רישיון
הבוט מופץ תחת רישיון MIT. לפרטים נוספים ראו את קובץ `LICENSE`.

### תמיכה
לעזרה או דיווח על בעיות, פתחו Issue במאגר GitHub.

### מפת דרכים
- [ ] תמיכה בפורמטים נוספים (JSON, XML).
- [ ] הוספת ניתוחים מתקדמים ואלגוריתמים של למידת מכונה.
- [ ] יצוא בפורמטים נוספים של גרפים ודוחות.
- [ ] ממשק משתמש רב‑לשוני.
- [ ] ממשק אינטרנטי להפעלה ללא טלגרם.

---

**כתב ויתור:** בוט זה מיועד לשימוש לימודי ומקצועי. השתמשו בנתונים בצורה אחראית והקפידו לעמוד בדרישות חוקי הגנת הפרטיות.

</div>
