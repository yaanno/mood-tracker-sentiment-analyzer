import json
import logging
import logging.handlers
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from sentiment_analyser.core.config import get_settings

settings = get_settings()

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for production logging."""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

class CustomFormatter(logging.Formatter):
    """Custom formatter for development logging with color support."""
    COLORS = {
        logging.DEBUG: "\033[36m",    # cyan
        logging.INFO: "\033[32m",     # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",    # red
        logging.CRITICAL: "\033[41m", # red background
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        record.color_level_name = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_file_handler(log_path: Path) -> Optional[logging.Handler]:
    """Set up file logging handler with rotation."""
    try:
        os.makedirs(log_path.parent, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            # maxBytes=settings.logging.max_file_size_bytes,
            # backupCount=settings.logging.backup_count,
            encoding="utf-8",
        )
        
        if settings.app.ENVIRONMENT.upper() == "PRODUCTION":
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
        
        return file_handler
    except (OSError, PermissionError) as e:
        print(f"Failed to setup file logging: {e}", file=sys.stderr)
        return None

def setup_console_handler() -> logging.Handler:
    """Set up console logging handler with appropriate formatting."""
    console_handler = logging.StreamHandler()
    
    if settings.app.ENVIRONMENT.upper() == "PRODUCTION":
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(
            CustomFormatter(
                "%(asctime)s - %(name)s - %(color_level_name)s - %(message)s"
            )
        )
    
    return console_handler

@lru_cache
def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if the logger doesn't have handlers
    if not logger.handlers:
        log_level = (
            logging.DEBUG 
            if settings.app.ENVIRONMENT.upper() != "PRODUCTION"
            else logging.INFO
        )
        logger.setLevel(log_level)
        
        # Add console handler
        logger.addHandler(setup_console_handler())
        
        # Add file handler if enabled
        # if settings.logging.log_to_file:
        #     file_handler = setup_file_handler(
        #         Path(settings.logging.file_path)
        #     )
        #     if file_handler:
        #         logger.addHandler(file_handler)
        
        logger.propagate = False
    
    return logger

