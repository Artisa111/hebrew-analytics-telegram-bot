## Hebrew Data Analytics Telegram Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateUrl=https://github.com/Artisa111/hebrew-analytics-telegram-bot)

Production-ready Telegram bot for automated data analytics, fully localized to Hebrew (RTL). Upload CSV/Excel/Google Sheets and get analysis, charts, insights, and a polished PDF report.

### Key Features
- File input: CSV, Excel (.xlsx), Google Sheets link
- **Robust data preprocessing**: Handles messy data with currencies, percentages, mixed formats
- Data quality and descriptive stats (missing values, duplicates, outliers, distributions)
- Visualizations (matplotlib/seaborn): histograms + box plots, bar charts, correlation matrix, scatter plots, KDE, outlier analysis, time trends, statistical summary table
- Funnel analysis with conversion captions per step
- Per-chart insights under every image + actionable guidance
- Insights & Recommendations: correlations, anomalies, distributions, categorical insights, business suggestions, further analyses
- Machine Learning: KMeans clustering, RandomForest regression/classification with metrics and feature importances
- A/B testing: proportions z-test and numeric t-test
- **Enhanced PDF report in Hebrew (RTL)** with guaranteed content sections and charts
- **Rate-limited logging** for production deployments
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
- pdf_report.py – Enhanced PDF report generation with guaranteed sections
- preprocess.py – Robust data preprocessing utilities
- i18n.py – Internationalization support (Hebrew/English)
- logging_config.py – Rate-limited logging configuration
- requirements.txt – dependencies
- Dockerfile – Production container with Hebrew font support
- Procfile – Railway worker entrypoint
- runtime.txt – pinned Python version for Railway
- Optional helpers: data_analysis.py, visualization.py, google_sheets.py

### Environment Variables

The bot supports the following environment variables for customization:

#### Required
- `BOT_TOKEN` - Your Telegram bot token (get from @BotFather)

#### Optional - Report Configuration
- `REPORT_LANG` - Report language (default: "he" for Hebrew, also supports "en")
- `REPORT_TZ` - Timezone for report timestamps (default: "Asia/Jerusalem")
- `REPORT_FONT_REGULAR` - Path to regular Hebrew font (auto-detected if not set)
- `REPORT_FONT_BOLD` - Path to bold Hebrew font (auto-detected if not set)

#### Optional - Logging Configuration  
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: "INFO")
- `LOGS_MAX_PER_SEC` - Maximum log messages per second (default: "100")
- `UVICORN_ACCESS_LOG` - Enable uvicorn access logs: "true" or "false" (default: "true")

#### Optional - Application Settings
- `MPLBACKEND` - Matplotlib backend (default: "Agg" for headless)
- `PYTHONUNBUFFERED` - Disable Python output buffering (recommended: "1")
- `GOOGLE_CREDENTIALS_FILE` - Path to Google Sheets credentials JSON (if using Google Sheets)

## Enhanced Data Preprocessing

The bot now handles messy data formats automatically:

- **Currency symbols**: ₪, $, €, £, ¥ automatically detected and cleaned
- **Percentage values**: 15% → 0.15 (converted to decimal)  
- **Negative values in parentheses**: (250) → -250
- **Thousand separators**: "1,234.56", "1.234,56", "1 234" all handled
- **Mixed decimal formats**: European (12,5) and US (12.5) formats supported
- **Date detection**: Automatic parsing with European day-first preference
- **Column name normalization**: Spaces, special characters cleaned automatically

## Enhanced PDF Reports

Reports now include guaranteed content sections:

- **Data Preview**: Always shows first 10 rows in a formatted table
- **Missing Values Analysis**: Bar chart of missing data percentages
- **Categorical Distributions**: Top value frequencies for categorical columns
- **Numeric Distributions**: Histograms and box plots for numeric data
- **Statistical Summary**: Complete df.describe() results as formatted table

Reports feature proper Hebrew RTL layout with timezone-aware timestamps.

## Docker Deployment

The application includes full Docker support with Hebrew font handling:

```bash
# Build the Docker image
docker build -t hebrew-analytics-bot .

# Run with environment variables
docker run -d \
  -e BOT_TOKEN=your_bot_token_here \
  -e REPORT_LANG=he \
  -e LOG_LEVEL=INFO \
  --name hebrew-bot \
  hebrew-analytics-bot
```

The Docker image includes:
- Python 3.11-slim base
- Noto Sans Hebrew fonts pre-installed
- Optimized for production deployment
- All dependencies pre-installed

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
- `REPORT_TZ`: Timezone for PDF report dates (default: "Asia/Jerusalem"). Example: "UTC", "America/New_York"
- `REPORT_FONT_REGULAR`: Path to custom regular Hebrew font file
- `REPORT_FONT_BOLD`: Path to custom bold Hebrew font file
- `MPLBACKEND`: Matplotlib backend (recommend "Agg" for headless environments like Railway)

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

Disclaimer: This bot is intended for educational and professional use. Handle data responsibly and comply with privacy regulations.