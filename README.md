## Hebrew Data Analytics Telegram Bot (English)

Production‑ready Telegram bot for advanced, automated data analytics — fully localized to Hebrew (RTL). Upload CSV/Excel/Google Sheets and get high‑quality analysis, charts, per‑chart insights, ML results, A/B testing, and a downloadable PDF report — all in Hebrew.

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

### 🔐 Security and Secrets

**⚠️ Important**: This project requires secure handling of sensitive information. Please review our [SECURITY.md](./SECURITY.md) for complete security guidelines.

**Key Security Points:**
- **BOT_TOKEN must be provided via environment variable** (never hardcode it)
- **Never commit `.env` files or `credentials.json`** to the repository
- For Railway deployment: set `BOT_TOKEN` in Project Settings → Variables
- For local development: use environment variables or `.env` files (local only)

**Local .env example** (create this file locally, never commit it):
```bash
# .env (local only - never commit!)
BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_CREDENTIALS_FILE=credentials.json
LOG_LEVEL=INFO
```

See [SECURITY.md](./SECURITY.md) for complete security guidelines, token rotation procedures, and best practices.

### Local Run
1) Create a bot via [@BotFather](https://t.me/BotFather) and copy the token
2) Create venv and install deps:
```bash
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
```
3) Set BOT_TOKEN environment variable and run:
```bash
# Linux/Mac
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
python simple_bot.py

# Windows PowerShell  
$env:BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
python simple_bot.py

# Or create .env file (see Security section above) and run
python simple_bot.py
```

### Railway Deployment
1. Fork this repo on GitHub
2. On Railway → New Project → Deploy from GitHub → select your fork
3. **Project Settings → Variables** (REQUIRED):
   - `BOT_TOKEN` = your Telegram token from [@BotFather](https://t.me/BotFather)
   - (optional) `GOOGLE_CREDENTIALS_FILE` = path to Google credentials JSON
4. Deploy will automatically use the included `Procfile`:
```
worker: python simple_bot.py
```

**Important**: The `BOT_TOKEN` must be set as an environment variable in Railway. Do not hardcode it in the source code.

The included `runtime.txt` specifies Python 3.11.8 for consistency.

### Notes
- Each chart is sent with a Hebrew insight in the caption and a follow‑up “What next” message.
- Hebrew/RTL text is supported in charts and PDF via font configuration.
- Telegram file upload limit for bots is ~50MB.

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

