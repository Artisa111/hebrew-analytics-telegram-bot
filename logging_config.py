# -*- coding: utf-8 -*-
"""
Logging configuration module with rate limiting
Provides centralized logging setup with token bucket rate limiting
"""

import logging
import logging.handlers
import os
import time
import threading
from typing import Optional
from collections import defaultdict


class TokenBucketFilter(logging.Filter):
    """
    Token bucket filter for rate limiting log messages
    Limits log messages per second to stay within Railway deployment limits
    """
    
    def __init__(self, max_tokens: int = 100, refill_rate: int = 100):
        """
        Initialize token bucket filter
        
        Args:
            max_tokens: Maximum number of tokens (messages) per second
            refill_rate: Rate at which tokens are refilled per second
        """
        super().__init__()
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record based on token bucket algorithm
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: True if record should be logged, False if rate limited
        """
        with self.lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = int(elapsed * self.refill_rate)
            
            if tokens_to_add > 0:
                self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
                self.last_refill = now
            
            # Check if we have tokens available
            if self.tokens > 0:
                self.tokens -= 1
                return True
            else:
                # Rate limited - don't log this message
                return False


class PerLoggerTokenBucketFilter(logging.Filter):
    """
    Per-logger token bucket filter for more granular rate limiting
    Maintains separate token buckets for different loggers
    """
    
    def __init__(self, max_tokens: int = 100, refill_rate: int = 100):
        """
        Initialize per-logger token bucket filter
        
        Args:
            max_tokens: Maximum number of tokens per logger per second
            refill_rate: Rate at which tokens are refilled per second
        """
        super().__init__()
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.buckets = defaultdict(lambda: {
            'tokens': max_tokens,
            'last_refill': time.time()
        })
        self.lock = threading.Lock()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record based on per-logger token bucket
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: True if record should be logged, False if rate limited
        """
        logger_name = record.name
        
        with self.lock:
            now = time.time()
            bucket = self.buckets[logger_name]
            
            # Refill tokens based on elapsed time
            elapsed = now - bucket['last_refill']
            tokens_to_add = int(elapsed * self.refill_rate)
            
            if tokens_to_add > 0:
                bucket['tokens'] = min(self.max_tokens, bucket['tokens'] + tokens_to_add)
                bucket['last_refill'] = now
            
            # Check if we have tokens available
            if bucket['tokens'] > 0:
                bucket['tokens'] -= 1
                return True
            else:
                # Rate limited - don't log this message
                return False


def configure_logging(
    log_level: Optional[str] = None,
    max_logs_per_sec: Optional[int] = None,
    disable_uvicorn_access: Optional[bool] = None
) -> None:
    """
    Configure centralized logging with rate limiting
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_logs_per_sec: Maximum log messages per second for rate limiting
        disable_uvicorn_access: Whether to disable uvicorn access logs
    """
    
    # Get configuration from environment variables
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    if max_logs_per_sec is None:
        max_logs_per_sec = int(os.getenv('LOGS_MAX_PER_SEC', '100'))
    
    if disable_uvicorn_access is None:
        disable_uvicorn_access = os.getenv('UVICORN_ACCESS_LOG', 'true').lower() == 'false'
    
    # Validate log level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_levels:
        log_level = 'INFO'
        print(f"Warning: Invalid log level, using INFO. Valid levels: {', '.join(valid_levels)}")
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    
    # Create formatter (English only as per requirements)
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add token bucket filter for rate limiting
    rate_limiter = TokenBucketFilter(
        max_tokens=max_logs_per_sec,
        refill_rate=max_logs_per_sec
    )
    console_handler.addFilter(rate_limiter)
    
    # Configure root logger
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)
    
    # Configure third-party loggers to reduce noise
    noisy_loggers = [
        'telegram',
        'telegram.ext',
        'telegram.bot',
        'aiogram',
        'uvicorn',
        'uvicorn.access',
        'uvicorn.error', 
        'pandas',
        'matplotlib',
        'matplotlib.font_manager',
        'matplotlib.pyplot',
        'PIL',
        'PIL.Image',
        'requests',
        'urllib3',
        'urllib3.connectionpool',
        'asyncio',
        'httpx',
        'httpcore'
    ]
    
    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
    
    # Special handling for uvicorn access logs
    if disable_uvicorn_access:
        uvicorn_access_logger = logging.getLogger('uvicorn.access')
        uvicorn_access_logger.disabled = True
    
    # Log the configuration
    app_logger = logging.getLogger('logging_config')
    app_logger.info(f"Logging configured - Level: {log_level}, Rate limit: {max_logs_per_sec} msgs/sec")
    app_logger.info(f"Third-party loggers set to WARNING level to reduce noise")
    
    if disable_uvicorn_access:
        app_logger.info("Uvicorn access logs disabled")


def setup_file_logging(
    log_file: str = 'app.log',
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Setup additional file logging with rotation
    
    Args:
        log_file: Log file path
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    logger = logging.getLogger('logging_config')
    logger.info(f"File logging enabled: {log_file} (max: {max_bytes} bytes, backups: {backup_count})")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with proper configuration
    All loggers should use English messages only
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)


def test_rate_limiting() -> None:
    """
    Test function to verify rate limiting is working
    """
    logger = get_logger('rate_limit_test')
    
    logger.info("Starting rate limit test...")
    
    # Try to log many messages quickly
    start_time = time.time()
    logged_count = 0
    
    for i in range(200):
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Test message {i + 1}")
            logged_count += 1
        time.sleep(0.001)  # Small delay
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    logger.info(f"Rate limit test completed: {logged_count} messages in {elapsed:.2f} seconds")
    logger.info(f"Effective rate: {logged_count / elapsed:.1f} messages/second")


def silence_logger(logger_name: str, level: int = logging.CRITICAL) -> None:
    """
    Silence a specific logger by setting its level
    
    Args:
        logger_name: Name of logger to silence
        level: Minimum level for this logger (default: CRITICAL)
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    config_logger = get_logger('logging_config')
    config_logger.debug(f"Logger '{logger_name}' silenced (level: {logging.getLevelName(level)})")


def unsilence_logger(logger_name: str) -> None:
    """
    Restore a logger to use the root logger's level
    
    Args:
        logger_name: Name of logger to restore
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.NOTSET)  # Will inherit from root
    
    config_logger = get_logger('logging_config')
    config_logger.debug(f"Logger '{logger_name}' restored to inherit root level")


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    configure_logging()