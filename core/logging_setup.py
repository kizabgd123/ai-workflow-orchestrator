import logging
import json
import os
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.
    Required for Zero Script QA methodology.
    """

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
        }

        # Handle structured data if passed in 'extra'
        if hasattr(record, "event"):
            log_data["event"] = record.event
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id
        if hasattr(record, "confidence"):
            log_data["confidence"] = record.confidence
        if hasattr(record, "status"):
            log_data["status"] = record.status

        # Include any other extra fields
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(level=logging.INFO):
    """
    Initializes the logging system with a JSON formatter for standard output.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Standard Output Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)

    logging.info(
        "Structured JSON logging initialized.",
        extra={"event": "system.startup", "status": "success"},
    )
