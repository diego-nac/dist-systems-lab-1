import logging
from typing import Optional
import sys

PROJECT_NAME = "smart_devices"

LOGGER_MODE = 'DEBUG'

LOGGING_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

def format_uppercase(record):
    record.name = record.name.upper()
    record.module = record.module.upper()
    return True

class LoggerConfig:
    _logger: Optional[logging.Logger] = None  # Singleton instance

    def __init__(self, project_name: Optional[str] = PROJECT_NAME) -> None:
        self.project_name: str = project_name
        self.LOG_FORMAT: str = (
            "%(asctime)s (%(levelname)s) %(name)s/%(module)s - %(message)s"
        )
        if not LoggerConfig._logger:
            self.setup_logger()
        self.logger = LoggerConfig._logger

    def validate_logger_mode(self, mode: str) -> str:
        if mode not in LOGGING_LEVELS:
            raise ValueError(f"Invalid LOGGER_MODE: {mode}. Must be one of {list(LOGGING_LEVELS.keys())}")
        return mode

    def setup_logger(self) -> None:
        validated_mode = self.validate_logger_mode(LOGGER_MODE)
        LoggerConfig._logger = logging.getLogger(self.project_name)
        LoggerConfig._logger.setLevel(LOGGING_LEVELS[validated_mode])
        formatter = logging.Formatter(
            self.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(format_uppercase)
        LoggerConfig._logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger