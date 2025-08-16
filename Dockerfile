# Use Python 3.11 slim base image for optimal size and Hebrew font support
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Hebrew fonts
RUN apt-get update && apt-get install -y \
    fonts-noto-core \
    fonts-noto-ui-core \
    fontconfig \
    build-essential \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update font cache
RUN fc-cache -f -v

# Set environment variables with defaults
ENV MPLBACKEND=Agg
ENV REPORT_LANG=he
ENV REPORT_TZ=Asia/Jerusalem  
ENV LOG_LEVEL=INFO
ENV LOGS_MAX_PER_SEC=100
ENV PYTHONUNBUFFERED=1

# Set Hebrew font paths to Noto fonts installed in container
ENV REPORT_FONT_REGULAR=/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf
ENV REPORT_FONT_BOLD=/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p charts temp logs

# Expose port (if needed for future web interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["python", "simple_bot.py"]