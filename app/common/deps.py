"""Shared clients for Postgres, Redis and outbound HTTP."""
import httpx
import psycopg
import redis.asyncio as aioredis

from common.config import POSTGRES_DSN, REDIS_URL

redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

# One shared httpx client per process. Creating a new client per request leaks
# sockets and destroys connection reuse - a classic cause of mystery latency.
http_client = httpx.AsyncClient(timeout=httpx.Timeout(5.0))


async def pg_connect():
    """Open a Postgres connection. Deliberately un-pooled so you can watch it
    become a bottleneck later."""
    return await psycopg.AsyncConnection.connect(POSTGRES_DSN)


async def init_db() -> None:
    conn = await pg_connect()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id          SERIAL PRIMARY KEY,
                    item        TEXT NOT NULL,
                    value_rupees INTEGER NOT NULL,
                    status      TEXT NOT NULL,
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        await conn.commit()
