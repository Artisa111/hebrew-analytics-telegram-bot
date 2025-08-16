FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Hebrew fonts
RUN apt-get update && apt-get install -y \
    fonts-noto-core \
    fonts-noto-ui-core \
    fonts-dejavu-core \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables with defaults
ENV MPLBACKEND=Agg
ENV REPORT_LANG=he
ENV REPORT_TZ=Asia/Jerusalem
ENV LOG_LEVEL=INFO
ENV LOGS_MAX_PER_SEC=100
ENV UVICORN_ACCESS_LOG=false
ENV PYTHONUNBUFFERED=1
ENV REPORT_FONT_REGULAR=/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf
ENV REPORT_FONT_BOLD=/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for temporary files
RUN mkdir -p /app/temp /app/charts /app/reports

# Set permissions
RUN chmod -R 755 /app

# Default command
CMD ["python", "main.py"]