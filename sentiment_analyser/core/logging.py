import json
import logging
import logging.handlers
import os
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Optional, TypeVar, cast

from sentiment_analyser.core.settings import get_settings

settings = get_settings()

# Type variables for generic function signatures
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')

@dataclass
class LogContext:
    """Context information for logging."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = field(default_factory=time.time)
    extra_data: Dict[str, Any] = field(default_factory=dict)

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for production logging with enhanced metadata."""
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string with rich metadata."""
        # Get the log context from record if available
        context = getattr(record, 'context', None)
        
        # Basic log data
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add context information if available
        if context:
            log_data.update({
                "request_id": context.request_id,
                "duration_ms": (time.time() - context.start_time) * 1000,
                **context.extra_data
            })
        
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
def log_duration(logger: Optional[logging.Logger] = None) -> Callable[[F], F]:
    """
    Decorator that logs the duration of a function call.
    
    Args:
        logger: Logger instance to use. If None, gets logger with function's module name
        
    Returns:
        Decorated function that logs its execution time
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get or create logger
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.info(
                    f"Function {func.__name__} completed",
                    extra={
                        'duration_ms': duration,
                        'function': func.__name__
                    }
                )
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(
                    f"Function {func.__name__} failed",
                    extra={
                        'duration_ms': duration,
                        'function': func.__name__,
                        'error': str(e)
                    },
                    exc_info=True
                )
                raise
        return cast(F, wrapper)
    return decorator

@contextmanager
def log_context(
    logger: logging.Logger,
    context: Optional[LogContext] = None
) -> Generator[LogContext, None, None]:
    """
    Context manager that attaches context to log records.
    
    Args:
        logger: Logger instance to attach context to
        context: Optional existing context to use
        
    Yields:
        LogContext instance
    """
    if context is None:
        context = LogContext()
    
    # Store original factory
    old_factory = logging.getLogRecordFactory()
    
    # Create new factory that adds context
    def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = old_factory(*args, **kwargs)
        record.context = context  # type: ignore
        return record
    
    try:
        logging.setLogRecordFactory(record_factory)
        yield context
    finally:
        logging.setLogRecordFactory(old_factory)

@lru_cache
def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A configured logger instance with appropriate handlers and formatters
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

