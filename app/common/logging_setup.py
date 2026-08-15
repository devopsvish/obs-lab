"""
Structured (JSON) logging.

WHY JSON AND NOT PLAIN TEXT?
----------------------------
A human reads "Order 42 failed for user bob". A log system cannot - it would
need a regex to pull "42" out. If you emit {"order_id": 42, "user": "bob"}
instead, Loki can filter on order_id directly. Structured logging is the
difference between grep and a query language.
"""
import logging
import sys

from pythonjsonlogger import json as jsonlogger

from common.config import SERVICE_NAME


class ServiceFilter(logging.Filter):
    """Stamps every log record with the service name.

    PYTHON NOTE: a logging Filter's `filter()` method returns True to keep the
    record. We are abusing it slightly - we mutate the record on the way past,
    which is the standard trick for adding fields to every log line.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.service = SERVICE_NAME
        return True


def setup_logging(level: str = "INFO") -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "ts", "levelname": "level"},
        )
    )
    handler.addFilter(ServiceFilter())

    root = logging.getLogger()
    root.handlers.clear()          # drop uvicorn's default text handler
    root.addHandler(handler)
    root.setLevel(level)

    # Uvicorn installs its own loggers; make them use ours instead.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    return logging.getLogger(SERVICE_NAME)
