## Hebrew Data Analytics Telegram Bot (English)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateUrl=https://github.com/Artisa111/hebrew-analytics-telegram-bot)

Production‑ready Telegram bot for advanced, automated data analytics — fully localized to Hebrew (RTL). Upload CSV/Excel/Google Sheets and get high‑quality analysis, charts, per‑chart insights, and a polished Hebrew PDF report.

### Key Features

- File input: CSV, Excel (.xlsx), Google Sheets link
- Data quality and descriptive stats (missing values, duplicates, outliers, distributions)
- Visualizations (matplotlib/seaborn): histograms + box plots, bar charts, correlation matrix, scatter plots, KDE, outlier analysis, time trends, statistical summary table
- Funnel analysis with conversion captions per step
- Per‑chart insights under every image + “what to do next” guidance (Hebrew)
- Insights & Recommendations: correlations, anomalies, distributions, categorical insights, business suggestions, further analyses
- Machine Learning: KMeans clustering, RandomForest regression/classification with metrics and feature importances
- A/B testing: proportions z‑test and numeric t‑test
- PDF report in Hebrew (RTL) with charts and summaries
- SQLite session storage (optional)

### Tech Stack
- Python 3.11+ (tested on 3.13)
- python‑telegram‑bot ≥ 20
- pandas, numpy, scipy, seaborn, matplotlib
- scikit‑learn
- fpdf2 (PDF)
- gspread + oauth2client (optional Google Sheets)

### Project Structure
- `simple_bot.py` – runnable bot with handlers, analytics, charts, insights
- `data_analysis.py`, `visualization.py`, `pdf_report.py` – optional helpers
- `run_bot.py` – alt runner
- `requirements.txt` – dependencies

## Security and secrets
- Never commit tokens or credentials to the repository. Use environment variables instead.
- Required variable: `BOT_TOKEN`.
- For local development, keep a `.env` file (not committed) and export variables before running. See SECURITY.md for details.

### Local Run
1) Create a bot via BotFather and copy the token  
2) Create venv and install deps:
```bash
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
```
3) Set env and run:
```powershell
$env:BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
python simple_bot.py
```

---

## One‑click Railway Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateUrl=https://github.com/Artisa111/hebrew-analytics-telegram-bot)

This project ships with a Procfile and runtime for hassle‑free deployment on Railway.

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
   - PYTHONUNBUFFERED = 1 (optional, for real‑time logs)
3. Deploy. Railway will use the included Procfile and start a Worker.
4. Open Logs — you should see:
   - “Starting Simple Hebrew Bot...”“
   - “Bot created successfully!”
   - “Starting bot...”
5. Find your bot in Telegram and send /start. Upload CSV/Excel and try “דוח PDF מתקדם”.

### Notes for Railway
- The bot runs via long polling — no extra web server is required.
- Ensure BOT_TOKEN is set. Without it, the app will exit on startup.
- If you see matplotlib backend/display errors, set MPLBACKEND=Agg.
- Telegram file upload limit for bots is ~50MB.

---

### Troubleshooting
- Ensure `BOT_TOKEN` is present in environment
- Matplotlib font warnings are harmless; charts still render
- If charts fail, check the file columns and types; try sample CSV



## 🤝 תרומה לפרויקט

תרומות יתקבלו בברכה! אנא:

1. Fork את הפרויקט
2. צור branch חדש לתכונה
3. Commit את השינויים
4. Push ל-branch
5. פתח Pull Request


פרויקט זה מוגן תחת רישיון MIT. ראה קובץ `LICENSE` לפרטים.

## 📞 תמיכה

לשאלות ותמיכה:

- פתח Issue ב-GitHub
- פנה למפתח הבוט
- בדוק את התיעוד

## 🔄 עדכונים עתידיים

- [ ] תמיכה בפורמטים נוספים (JSON, XML)
- [ ] ניתוח מתקדם יותר (Machine Learning)
- [ ] ייצוא לפורמטים נוספים
- [ ] תמיכה בשפות נוספות
- [ ] ממשק ווב

---

**הערה**: בוט זה נועד לשימוש חינוכי ומקצועי. אנא השתמש בנתונים בצורה אחראית ובהתאם לחוקי הפרטיות הרלוונטיים.