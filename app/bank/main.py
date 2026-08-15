"""BANK - a mock third party you do not control.

In real life this is Razorpay or Stripe. You cannot fix it, you cannot see
inside it, and it will absolutely have a bad day at some point.
"""
import asyncio
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.chaos import apply_chaos
from common.config import SERVICE_NAME
from common.logging_setup import setup_logging
from common.telemetry import MetricsMiddleware, metrics_endpoint, setup_tracing

log = setup_logging()
app = FastAPI(title="bank")
setup_tracing(app, SERVICE_NAME)

# register your metrics middleware here.
app.add_middleware(MetricsMiddleware)


class AuthorizeRequest(BaseModel):
    order_id: int
    value_rupees: int


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return metrics_endpoint()


@app.post("/authorize")
async def authorize(req: AuthorizeRequest):
    await apply_chaos()
    # Even on a good day a real payment gateway is slow and occasionally rejects.
    await asyncio.sleep(random.uniform(0.02, 0.09))
    if random.random() < 0.005:
        raise HTTPException(status_code=402, detail="card declined")
    return {"authorized": True, "order_id": req.order_id}
