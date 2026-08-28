import json
import logging
import sys
from datetime import datetime, timezone
from app.config import Settings


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = None
        try:
            from app.middleware.request_context import request_id_var
            request_id = request_id_var.get(None)
        except (ImportError, AttributeError):
            pass

        log_data = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": request_id,
            "msg": record.getMessage()
        }

        standard_attrs = {
            'args', 'asctime', 'created', 'exc_info', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
            'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
            'stack_info', 'thread', 'threadName', 'extra', 'taskName'
        }
        for k, v in record.__dict__.items():
            if k not in standard_attrs and k not in log_data:
                log_data[k] = v

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging(settings: Settings) -> None:
    root_logger = logging.getLogger()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_JSON:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
        ))

    root_logger.addHandler(handler)
