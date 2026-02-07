import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime


class AppLogger:
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        to_console: bool = True,
        to_file: bool = False,
        file_path: str = "app.log",
        max_size_mb: int = 10,
        backup_count: int = 5,
        json_format: bool = False,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS.get(level.upper(), logging.INFO))
        self.logger.propagate = False

        self.logger.handlers.clear()

        formatter = (
            JsonFormatter()
            if json_format
            else logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )

        if to_console:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            self.logger.addHandler(console)

        if to_file:
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=max_size_mb * 1024 * 1024,
                backupCount=backup_count,
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    # ---- Public API ----

    def debug(self, msg, *args):
        self.logger.debug(msg, *args)

    def info(self, msg, *args):
        self.logger.info(msg, *args)

    def warning(self, msg, *args):
        self.logger.warning(msg, *args)

    def error(self, msg, *args):
        self.logger.error(msg, *args)

    def exception(self, msg):
        self.logger.exception(msg)

    def critical(self, msg, *args):
        self.logger.critical(msg, *args)


# ---------- JSON FORMATTER ----------

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# ---------- LOGGER INSTANCE ----------

from threading import Lock

_instance = None
_lock = Lock()
def get_logger():
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = AppLogger(
                    name="WebhookActionReceiver",
                    level="INFO",
                    to_console=True
                )
    return _instance