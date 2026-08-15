"""
Fault injection.

Each service reads its chaos settings from Redis on every request. That lets
your mentor break the system at runtime WITHOUT restarting containers - which
is exactly how real incidents arrive: nothing was deployed, it just broke.

Key format:  chaos:<service>  ->  JSON
Example:     {"latency_ms": 800, "error_rate": 0.3}

DO NOT read chaos/scenarios.json during game day. That is cheating, and you
will only be cheating yourself out of the lesson.
"""
import asyncio
import json
import random

import redis.asyncio as aioredis

from common.config import REDIS_URL, SERVICE_NAME

_redis = aioredis.from_url(REDIS_URL, decode_responses=True)


class InjectedFault(Exception):
    """Raised when chaos decides this request should fail."""


async def apply_chaos() -> None:
    """Sleep and/or raise, according to the current chaos config.

    PYTHON NOTE: `async def` makes this a coroutine. Calling it does nothing on
    its own - you must `await` it. `await asyncio.sleep(x)` pauses THIS request
    while letting the server handle others, unlike time.sleep which blocks
    everything.
    """
    try:
        raw = await _redis.get(f"chaos:{SERVICE_NAME}")
    except Exception:
        return  # if Redis is down, do not let chaos break the app further

    if not raw:
        return

    cfg = json.loads(raw)

    latency_ms = cfg.get("latency_ms", 0)
    if latency_ms:
        jitter = random.uniform(0.7, 1.3)
        await asyncio.sleep((latency_ms / 1000.0) * jitter)

    error_rate = cfg.get("error_rate", 0.0)
    if error_rate and random.random() < error_rate:
        raise InjectedFault(cfg.get("message", "injected fault"))
