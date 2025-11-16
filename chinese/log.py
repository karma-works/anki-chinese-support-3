import logging
import os
import sys


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
        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
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
    """Global exception handler to log all unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log = _configure_logger()
    log.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    # Call the default exception handler to maintain normal behavior
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


log = _configure_logger()

# Install global exception handler
sys.excepthook = _exception_handler


