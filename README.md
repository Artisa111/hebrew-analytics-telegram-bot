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

### Railway Deployment
1. Fork this repo on GitHub
2. On Railway → New Project → Deploy from GitHub → select your fork
3. Project Settings → Variables:
   - `BOT_TOKEN` = your Telegram token
   - (optional) Google credentials
4. Start command:
```
python simple_bot.py
```
Alternatively, add a `Procfile` with:
```
worker: python simple_bot.py
```

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

