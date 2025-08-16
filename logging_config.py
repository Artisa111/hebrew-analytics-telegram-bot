# -*- coding: utf-8 -*-
"""
מודול תצורת לוגים - Logging configuration module
הגדרת לוגים מרכזית עם הגבלת קצב עבור Railway
"""

import logging
import os
import time
import threading
from typing import Dict, Any
from collections import deque


class TokenBucketFilter(logging.Filter):
    """
    מסנן לוגים עם אלגוריתם Token Bucket להגבלת קצב
    Token bucket filter for rate limiting logs
    """
    
    def __init__(self, rate: float = 100.0, burst: int = None):
        """
        Args:
            rate: Maximum logs per second (default 100 for Railway safety)
            burst: Maximum burst size (default is 2x rate)
        """
        super().__init__()
        self.rate = rate
        self.burst = burst or int(rate * 2)
        self.tokens = self.burst
        self.last_update = time.time()
        self.lock = threading.RLock()
        
    def filter(self, record):
        """Filter log records based on token bucket algorithm"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            self.last_update = now
            
            # Add tokens based on time passed
            self.tokens = min(self.burst, self.tokens + time_passed * self.rate)
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class MemoryLogHandler(logging.Handler):
    """
    מטפל לוגים שמשמר בזיכרון
    Memory log handler for keeping recent logs
    """
    
    def __init__(self, max_records: int = 1000):
        super().__init__()
        self.max_records = max_records
        self.records = deque(maxlen=max_records)
        self.lock = threading.RLock()
    
    def emit(self, record):
        """Emit a log record to memory"""
        with self.lock:
            try:
                formatted = self.format(record)
                self.records.append({
                    'timestamp': record.created,
                    'level': record.levelname,
                    'message': formatted,
                    'module': record.module
                })
            except Exception:
                self.handleError(record)
    
    def get_recent_logs(self, count: int = 50) -> list:
        """Get recent log records"""
        with self.lock:
            return list(self.records)[-count:]


def setup_logging():
    """
    הגדרת לוגים מרכזית עם הגבלת קצב
    Central logging setup with rate limiting for Railway
    """
    
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    max_logs_per_sec = float(os.getenv('LOGS_MAX_PER_SEC', '100'))
    disable_uvicorn_access = os.getenv('DISABLE_UVICORN_ACCESS_LOGS', 'false').lower() == 'true'
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with rate limiting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Add token bucket filter for rate limiting
    rate_limiter = TokenBucketFilter(rate=max_logs_per_sec)
    console_handler.addFilter(rate_limiter)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Add memory handler for debugging
    memory_handler = MemoryLogHandler()
    memory_handler.setLevel(logging.WARNING)  # Only store warnings and errors
    memory_handler.setFormatter(formatter)
    root_logger.addHandler(memory_handler)
    
    # Configure external libraries to WARNING level
    external_loggers = [
        'telegram',
        'telegram.bot',
        'telegram.ext',
        'aiogram',
        'uvicorn',
        'uvicorn.access',
        'pandas',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.font_manager',
        'PIL',
        'urllib3',
        'requests',
        'httpx',
        'asyncio',
    ]
    
    for logger_name in external_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
        logger.propagate = True  # Allow propagation but with higher threshold
    
    # Special handling for Uvicorn access logs
    if disable_uvicorn_access:
        uvicorn_access_logger = logging.getLogger('uvicorn.access')
        uvicorn_access_logger.disabled = True
    
    # Log configuration info
    app_logger = logging.getLogger(__name__)
    app_logger.info("=== Logging Configuration ===")
    app_logger.info(f"Log Level: {log_level}")
    app_logger.info(f"Max Logs/sec: {max_logs_per_sec}")
    app_logger.info(f"External loggers reduced to WARNING level")
    if disable_uvicorn_access:
        app_logger.info("Uvicorn access logs disabled")
    app_logger.info("=== End Logging Configuration ===")
    
    return memory_handler


def get_logging_stats() -> Dict[str, Any]:
    """
    קבלת סטטיסטיקות לוגים
    Get logging statistics
    """
    stats = {
        'configured_loggers': len(logging.Logger.manager.loggerDict),
        'root_handlers': len(logging.getLogger().handlers),
        'log_level': logging.getLogger().getEffectiveLevel(),
    }
    
    # Check for rate limiter
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        for filter_obj in handler.filters:
            if isinstance(filter_obj, TokenBucketFilter):
                stats['rate_limiter'] = {
                    'rate': filter_obj.rate,
                    'burst': filter_obj.burst,
                    'current_tokens': round(filter_obj.tokens, 2)
                }
                break
    
    return stats


def suppress_verbose_loggers():
    """
    השתקת לוגרים מפולטים נוספים
    Suppress additional verbose loggers that might appear at runtime
    """
    verbose_loggers = [
        'matplotlib.backends',
        'matplotlib.backends.backend_agg',
        'matplotlib.colorbar',
        'matplotlib.ticker',
        'PIL.PngImagePlugin',
        'PIL.Image',
        'fpdf.fpdf',
        'urllib3.connectionpool',
        'charset_normalizer',
    ]
    
    for logger_name in verbose_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)  # Only show errors


# Global memory handler for accessing recent logs
_memory_handler = None


def get_memory_handler() -> MemoryLogHandler:
    """Get the global memory handler instance"""
    return _memory_handler


def initialize_logging():
    """
    אתחול מערכת הלוגים
    Initialize the logging system
    """
    global _memory_handler
    _memory_handler = setup_logging()
    suppress_verbose_loggers()
    return _memory_handler