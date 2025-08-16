# -*- coding: utf-8 -*-
"""
Logging setup with rate limiting for Railway deployment
"""

import logging
import time
from typing import Optional
from config import LOG_LEVEL, LOGS_MAX_PER_SEC

class TokenBucketFilter(logging.Filter):
    """
    Token bucket filter to rate limit log messages
    """
    
    def __init__(self, rate: int = 100):
        """
        Initialize token bucket filter
        
        Args:
            rate: Maximum logs per second (default 100)
        """
        super().__init__()
        self.rate = rate
        self.tokens = rate
        self.last_refill = time.time()
    
    def filter(self, record):
        """
        Filter log records based on token bucket algorithm
        
        Args:
            record: Log record to filter
            
        Returns:
            bool: True if record should be logged, False otherwise
        """
        now = time.time()
        
        # Refill tokens based on time elapsed
        elapsed = now - self.last_refill
        self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
        self.last_refill = now
        
        # Check if we have tokens available
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        
        return False


def setup_logging(level: Optional[str] = None, rate_limit: Optional[int] = None) -> None:
    """
    Setup logging configuration with rate limiting for Railway
    
    Args:
        level: Log level (defaults to LOG_LEVEL from config)
        rate_limit: Max logs per second (defaults to LOGS_MAX_PER_SEC from config)
    """
    if level is None:
        level = LOG_LEVEL
    if rate_limit is None:
        rate_limit = LOGS_MAX_PER_SEC
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add token bucket filter to root logger
    root_logger = logging.getLogger()
    bucket_filter = TokenBucketFilter(rate=rate_limit)
    root_logger.addFilter(bucket_filter)
    
    # Reduce verbosity of external loggers
    external_loggers = [
        'telegram',
        'aiogram', 
        'uvicorn',
        'pandas',
        'matplotlib',
        'PIL',
        'httpx',
        'urllib3'
    ]
    
    for logger_name in external_loggers:
        external_logger = logging.getLogger(logger_name)
        external_logger.setLevel(logging.WARNING)
    
    # Log the setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete: level={level}, rate_limit={rate_limit}/sec")