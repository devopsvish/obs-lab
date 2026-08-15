"""ORDERS - owns the order lifecycle. Reads the menu from Redis, writes orders
to Postgres, and asks PAYMENTS to charge the customer."""
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.chaos import apply_chaos
from common.config import PAYMENTS_URL, SERVICE_NAME
from common.deps import http_client, init_db, pg_connect, redis_client
from common.logging_setup import setup_logging
from common.telemetry import MetricsMiddleware, metrics_endpoint, setup_tracing

log = setup_logging()
app = FastAPI(title="orders")
setup_tracing(app, SERVICE_NAME)

# register your metrics middleware here.
app.add_middleware(MetricsMiddleware)

MENU = [
    {"item": "margherita", "value_rupees": 350},
    {"item": "pepperoni", "value_rupees": 450},
    {"item": "paneer tikka", "value_rupees": 420},
]


class OrderRequest(BaseModel):
    item: str
    value_rupees: int = 350


@app.on_event("startup")
async def startup():
    """Runs once when the process boots, before serving traffic."""
    try:
        await init_db()
    except Exception as exc:
        log.error("db init failed", extra={"error": str(exc)})


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return metrics_endpoint()


@app.get("/menu")
async def menu():
    await apply_chaos()
    cached = await redis_client.get("menu")
    if cached:
        return {"menu": json.loads(cached), "cache": "hit"}

    await redis_client.setex("menu", 60, json.dumps(MENU))
    return {"menu": MENU, "cache": "miss"}


@app.post("/orders")
async def create_order(req: OrderRequest):
    await apply_chaos()

    conn = await pg_connect()
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO orders (item, value_rupees, status) "
                "VALUES (%s, %s, %s) RETURNING id",
                (req.item, req.value_rupees, "pending"),
            )
            row = await cur.fetchone()
            order_id = row[0]
        await conn.commit()

    try:
        r = await http_client.post(
            f"{PAYMENTS_URL}/charge",
            json={"order_id": order_id, "value_rupees": req.value_rupees},
        )
        r.raise_for_status()
    except Exception as exc:
        log.error("payment failed", extra={"order_id": order_id, "error": str(exc)})
        raise HTTPException(status_code=502, detail="payment failed")

    return {"order_id": order_id, "status": "confirmed", "item": req.item}
