"""
=============================================================================
THIS IS YOUR FILE. YOU WILL WRITE MOST OF IT IN HOUR 3.
=============================================================================

Right now it exposes only the metrics the prometheus_client library gives you
for free (process CPU, memory, GC). That is enough for Prometheus to scrape
successfully in Hour 2 - and enough to prove a painful point: those metrics
tell you NOTHING about whether customers can buy pizza.

The TODOs below are the instrumentation you will add. Do not fill them in yet.
"""
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

# ---------------------------------------------------------------------------
# METRIC DEFINITIONS
# ---------------------------------------------------------------------------
# PYTHON NOTE: these run once at import time and live for the life of the
# process. A Counter only ever goes up. A Histogram records a distribution of
# observed values (here: seconds per request) into buckets.
#
# NAMING: Prometheus convention is <namespace>_<thing>_<unit>_total.
# Always use base units - seconds, not milliseconds. Always suffix counters
# with _total. Interviewers do ask this.
# ---------------------------------------------------------------------------

http_requests_total = Counter(
    "pizza_http_requests_total",
    "Total HTTP requests handled.",
    ["service", "route", "method", "status"],
)

http_request_duration_seconds = Histogram(
    "pizza_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["service", "route", "method"],
    # Buckets are CUMULATIVE upper bounds. Choose them around the latency you
    # actually care about - the defaults are rarely right for your service.
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# TODO (Hour 3): define your business metrics here.
#   - pizza_orders_total{service, status}          Counter
#   - pizza_order_value_rupees_total{service}      Counter
#   - pizza_payment_attempts_total{result}         Counter
#   - pizza_dependency_up{dependency}              Gauge
# Ask yourself for each one: "if this number moved, would a customer notice?"


def metrics_endpoint() -> Response:
    """Render the Prometheus exposition format.

    Prometheus PULLS. It calls GET /metrics on a schedule and reads whatever
    text you return. Your app does not push anything anywhere.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------------------------
# TODO (Hour 3): write the middleware that records every request.
#
# Spec you must satisfy:
#   * time the request with time.perf_counter()
#   * on the way out, increment http_requests_total with the correct labels
#   * observe the duration into http_request_duration_seconds
#   * a request that raises an exception must STILL be recorded, as status 500
#   * use the ROUTE TEMPLATE ("/orders/{id}"), never the raw path
#     ("/orders/8471"). Raw paths create unbounded cardinality and will melt
#     your Prometheus. This is the single most common junior mistake.
# ---------------------------------------------------------------------------


def setup_tracing(app, service_name: str) -> None:
    """Wire up OpenTelemetry tracing. Filled in during Hour 4."""
    from common.config import OTLP_ENDPOINT

    if not OTLP_ENDPOINT:
        return
    # TODO (Hour 4): TracerProvider, OTLP exporter, FastAPI + httpx auto-instrumentation.
