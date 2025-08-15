import logging.config
import os
from datetime import datetime
from typing import Dict

from pythonjsonlogger.json import JsonFormatter

from src.core.common.settings import Settings

settings = Settings()


class CustomJsonFormatter(JsonFormatter):
    def add_fields(
        self, log_record: Dict, record: logging.LogRecord, message_dict: Dict
    ):
        super().add_fields(log_record, record, message_dict)

        top_level_keys = {
            "timestamp",
            "level",
            "name",
            "message",
            "pathname",
            "lineno",
            "funcName",
            "exc_info",
            "exc_text",
            "stack_info",
            "process",
            "thread",
            "threadName",
        }
        log_record["appname"] = settings.application_name
        log_record["level"] = record.levelname

        context_data = {}
        for key in list(log_record.keys()):
            if key not in top_level_keys:
                context_data[key] = log_record.pop(key)

        if context_data:
            log_record["context"] = context_data

        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.utcnow().strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )


def setup_logging():
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    logs_directory = os.path.join(project_root, "logs")
    os.makedirs(logs_directory, exist_ok=True)

    defaults = {"log_level": settings.log_level.upper(), "log_dir": logs_directory}

    conf_path = os.path.join(project_root, "logging.conf")
    if not os.path.exists(conf_path):
        raise FileNotFoundError(f"logging.conf not found at {conf_path}")
    logging.config.fileConfig(
        conf_path, defaults=defaults, disable_existing_loggers=False
    )
