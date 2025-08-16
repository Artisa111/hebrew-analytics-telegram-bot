# -*- coding: utf-8 -*-
"""
Centralized logging configuration with rate limiting
Reduces noisy third-party loggers and honors environment variables
"""

import logging
import logging.handlers
import os
import time
import threading
from typing import Dict, Optional
from collections import defaultdict, deque


class TokenBucketRateLimiter:
    """Token bucket algorithm for rate limiting log messages"""
    
    def __init__(self, max_rate: float = 100.0, bucket_size: Optional[float] = None):
        """
        Initialize rate limiter
        
        Args:
            max_rate: Maximum messages per second
            bucket_size: Bucket capacity (defaults to max_rate * 2)
        """
        self.max_rate = max_rate
        self.bucket_size = bucket_size or (max_rate * 2)
        self.tokens = self.bucket_size
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def allow_message(self) -> bool:
        """Check if a message should be allowed through"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            
            # Add tokens based on time passed
            self.tokens = min(
                self.bucket_size,
                self.tokens + time_passed * self.max_rate
            )
            
            self.last_update = now
            
            # Check if we have a token available
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            return False


class RateLimitingFilter(logging.Filter):
    """Logging filter that applies rate limiting"""
    
    def __init__(self, max_rate: float = 100.0):
        super().__init__()
        self.rate_limiter = TokenBucketRateLimiter(max_rate)
        self.dropped_count = 0
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records based on rate limit"""
        if self.rate_limiter.allow_message():
            # If we had dropped messages, add a note about it
            if self.dropped_count > 0:
                record.msg = f"[{self.dropped_count} messages dropped] {record.msg}"
                self.dropped_count = 0
            return True
        else:
            self.dropped_count += 1
            return False


class SuppressingFilter(logging.Filter):
    """Filter to suppress noisy third-party loggers"""
    
    def __init__(self, suppress_patterns: Dict[str, int]):
        """
        Initialize suppressing filter
        
        Args:
            suppress_patterns: Dict mapping logger names to minimum log levels
        """
        super().__init__()
        self.suppress_patterns = suppress_patterns
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter records based on suppression patterns"""
        for pattern, min_level in self.suppress_patterns.items():
            if record.name.startswith(pattern):
                return record.levelno >= min_level
        
        return True


def setup_logging():
    """
    Configure logging with rate limiting and third-party suppression
    Honors environment variables for configuration
    """
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logs_max_per_sec = float(os.getenv('LOGS_MAX_PER_SEC', '100'))
    uvicorn_access_log = os.getenv('UVICORN_ACCESS_LOG', 'false').lower() == 'true'
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add rate limiting filter
    if logs_max_per_sec > 0:
        rate_limit_filter = RateLimitingFilter(logs_max_per_sec)
        console_handler.addFilter(rate_limit_filter)
        
        logging.getLogger(__name__).info(
            f"Rate limiting enabled: {logs_max_per_sec} messages/second"
        )
    
    # Define noisy third-party loggers to suppress
    suppress_patterns = {
        'urllib3.connectionpool': logging.WARNING,
        'requests.packages.urllib3': logging.WARNING,
        'matplotlib': logging.WARNING,
        'PIL': logging.WARNING,
        'fontTools': logging.WARNING,
        'asyncio': logging.WARNING,
        'telegram': logging.INFO,  # Keep some telegram logs but reduce noise
        'httpx': logging.WARNING,
        'httpcore': logging.WARNING,
    }
    
    # Suppress Uvicorn access logs if disabled
    if not uvicorn_access_log:
        suppress_patterns['uvicorn.access'] = logging.CRITICAL
    
    # Add suppression filter
    suppression_filter = SuppressingFilter(suppress_patterns)
    console_handler.addFilter(suppression_filter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels for known noisy modules
    for logger_name, min_level in suppress_patterns.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(min_level)
    
    # Ensure our application loggers have appropriate levels
    app_loggers = [
        'pdf_report',
        'preprocess', 
        'i18n',
        'logging_config',
        'main',
        'simple_bot',
        '__main__'
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
    
    # Log configuration summary
    main_logger = logging.getLogger(__name__)
    main_logger.info(f"Logging configured - Level: {log_level}, Rate limit: {logs_max_per_sec}/sec")
    main_logger.debug(f"Suppression patterns: {list(suppress_patterns.keys())}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    Ensures logging is configured if not already done
    """
    # Check if root logger has handlers (i.e., logging is configured)
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logging.getLogger(name)


class PeriodicReporter:
    """Reports periodic statistics about logging"""
    
    def __init__(self, report_interval: float = 300.0):  # 5 minutes
        self.report_interval = report_interval
        self.last_report = time.time()
        self.message_counts = defaultdict(int)
        self.lock = threading.Lock()
    
    def record_message(self, level: str):
        """Record a message for statistics"""
        with self.lock:
            self.message_counts[level] += 1
            
            # Check if it's time to report
            now = time.time()
            if now - self.last_report >= self.report_interval:
                self._report_stats()
                self.message_counts.clear()
                self.last_report = now
    
    def _report_stats(self):
        """Report logging statistics"""
        if not self.message_counts:
            return
            
        logger = logging.getLogger(__name__)
        total = sum(self.message_counts.values())
        logger.info(f"Logging stats (last {self.report_interval/60:.1f}min): "
                   f"Total={total}, " +
                   ", ".join(f"{level}={count}" for level, count in self.message_counts.items()))


# Global reporter instance
_reporter = PeriodicReporter()


class StatsLoggingHandler(logging.Handler):
    """Handler that records statistics about log messages"""
    
    def emit(self, record: logging.LogRecord):
        """Record statistics for the log record"""
        _reporter.record_message(record.levelname)


def add_stats_reporting():
    """Add statistics reporting to the root logger"""
    stats_handler = StatsLoggingHandler()
    stats_handler.setLevel(logging.DEBUG)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(stats_handler)


# Initialize logging when module is imported
if __name__ != '__main__':
    # Only auto-configure if we're being imported, not run directly
    try:
        setup_logging()
    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.getLogger(__name__).error(f"Failed to configure advanced logging: {e}")


if __name__ == '__main__':
    # Test the logging configuration
    setup_logging()
    add_stats_reporting()
    
    logger = get_logger(__name__)
    logger.info("Testing logging configuration")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test rate limiting
    logger.info("Testing rate limiting...")
    for i in range(150):  # Should trigger rate limiting
        logger.debug(f"Rapid message {i}")
    
    logger.info("Logging test complete")