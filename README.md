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

Disclaimer: This bot is intended for educational and professional use. Handle data responsibly and comply with privacy regulations.