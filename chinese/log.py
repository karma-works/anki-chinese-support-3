import logging
import os
import sys
import threading
from functools import wraps


LOGGER_NAME = "anki-chinese-support"
LOG_FILENAME = "anki-chinese-support.log"


def _configure_logger() -> logging.Logger:
    """Configure and return the add-on logger.

    The logger writes to a file named `anki-chinese-support.log` located
    in the same directory as this module.
    """

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        log_path = os.path.join(os.path.dirname(__file__), LOG_FILENAME)
        handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Avoid passing messages to the root logger if it is configured elsewhere.
        logger.propagate = False

    return logger


def _exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler to log all unhandled exceptions in main thread."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log = _configure_logger()
    log.critical(
        "Unhandled exception in main thread",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    # Call the default exception handler to maintain normal behavior
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def _thread_exception_handler(args):
    """Exception handler for background threads."""
    log = _configure_logger()
    log.critical(
        "Unhandled exception in thread %s",
        args.thread.name if args.thread else "unknown",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )


def log_exceptions(func):
    """Decorator to automatically log exceptions in any function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log = _configure_logger()
            log.exception(
                "Exception in %s.%s",
                func.__module__ if hasattr(func, '__module__') else 'unknown',
                func.__name__
            )
            raise
    return wrapper


def wrap_hook(hook_func):
    """Wrapper for Anki hooks to automatically log exceptions."""
    @wraps(hook_func)
    def wrapper(*args, **kwargs):
        try:
            return hook_func(*args, **kwargs)
        except Exception as e:
            log = _configure_logger()
            log.exception(
                "Exception in hook %s.%s",
                hook_func.__module__ if hasattr(hook_func, '__module__') else 'unknown',
                hook_func.__name__
            )
            raise
    return wrapper


def get_log_path():
    """Get the path to the log file. Useful for debugging."""
    return os.path.join(os.path.dirname(__file__), LOG_FILENAME)


def clear_log():
    """Clear the log file. Useful for debugging."""
    log_path = get_log_path()
    if os.path.exists(log_path):
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("")
        log = _configure_logger()
        log.info("Log file cleared")


log = _configure_logger()

# Install global exception handlers
sys.excepthook = _exception_handler
# threading.excepthook was added in Python 3.8
if hasattr(threading, 'excepthook'):
    threading.excepthook = _thread_exception_handler


