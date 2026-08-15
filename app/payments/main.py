"""PAYMENTS - talks to the (mock) third-party bank."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.chaos import apply_chaos
from common.config import BANK_URL, SERVICE_NAME
from common.deps import http_client
from common.logging_setup import setup_logging
from common.telemetry import MetricsMiddleware, metrics_endpoint, setup_tracing

log = setup_logging()
app = FastAPI(title="payments")
setup_tracing(app, SERVICE_NAME)

# register your metrics middleware here.
app.add_middleware(MetricsMiddleware)


class ChargeRequest(BaseModel):
    order_id: int
    value_rupees: int


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return metrics_endpoint()


@app.post("/charge")
async def charge(req: ChargeRequest):
    await apply_chaos()
    try:
        r = await http_client.post(f"{BANK_URL}/authorize", json=req.model_dump())
        r.raise_for_status()
    except Exception as exc:
        log.error("bank authorize failed",
                  extra={"order_id": req.order_id, "error": str(exc)})
        raise HTTPException(status_code=502, detail="bank unavailable")
    return {"order_id": req.order_id, "charged": True}
