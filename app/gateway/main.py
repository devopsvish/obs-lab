"""
GATEWAY - the public front door. Customers only ever talk to this service.

PYTHON NOTE: FastAPI builds an app object, and decorators like @app.get("/menu")
register a function as the handler for that route. The decorator runs at import
time; the function runs per request.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.config import ORDERS_URL, SERVICE_NAME
from common.deps import http_client
from common.logging_setup import setup_logging
from common.telemetry import MetricsMiddleware, metrics_endpoint, setup_tracing

log = setup_logging()
app = FastAPI(title="gateway")
setup_tracing(app, SERVICE_NAME)

# register your metrics middleware here.
app.add_middleware(MetricsMiddleware)


class OrderRequest(BaseModel):
    """Pydantic model = automatic request validation + docs.

    If the client sends {"item": 5} FastAPI rejects it with a 422 before your
    code ever runs.
    """
    item: str
    value_rupees: int = 350


@app.get("/healthz")
async def healthz():
    """Liveness probe. Answers 'is this process alive', NOT 'is it healthy'.
    Never make this call your dependencies - a dead database would then kill
    every replica in a restart loop."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return metrics_endpoint()


@app.get("/menu")
async def menu():
    r = await http_client.get(f"{ORDERS_URL}/menu")
    r.raise_for_status()
    return r.json()


@app.post("/order")
async def order(req: OrderRequest):
    try:
        r = await http_client.post(f"{ORDERS_URL}/orders", json=req.model_dump())
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.error("order failed at gateway", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="could not place order")
