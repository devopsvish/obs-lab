"""
Tiny configuration helper.

PYTHON NOTE
-----------
os.environ is a dict-like object holding this process's environment variables.
Every value in it is a STRING. If you want a number you must convert it
yourself - that is all these helpers do.
"""
import os


def env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


def env_int(key: str, default: int) -> int:
    return int(os.environ.get(key, str(default)))


def env_float(key: str, default: float) -> float:
    return float(os.environ.get(key, str(default)))


# SERVICE_NAME is how this process identifies itself in metrics, logs and traces.
# Without it you cannot tell which of the four containers a data point came from.
SERVICE_NAME = env_str("SERVICE", "unknown")

REDIS_URL = env_str("REDIS_URL", "redis://redis:6379/0")
POSTGRES_DSN = env_str("POSTGRES_DSN", "postgresql://pizza:pizza@postgres:5432/pizza")

ORDERS_URL = env_str("ORDERS_URL", "http://orders:8000")
PAYMENTS_URL = env_str("PAYMENTS_URL", "http://payments:8000")
BANK_URL = env_str("BANK_URL", "http://bank:8000")

OTLP_ENDPOINT = env_str("OTLP_ENDPOINT", "")  # empty string = tracing disabled
