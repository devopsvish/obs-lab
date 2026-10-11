# PromQL — the five shapes

Almost every query you will ever write is one of these five, with different
metric names. Learn the shapes, not the functions.

---

## Shape 1 — "How fast is this happening?"

```promql
sum by (LABEL) (rate(SOME_counter_total[5m]))
```

Use for: request rate, error rate, orders per second, log lines per second.

- `rate()` — per-second rate of increase. **Counters only.**
- `[5m]` — look back this far. Shorter = twitchy, longer = smooth but slow.
- `sum by (x)` — collapse everything except label `x`.

Examples:
```promql
sum by (service) (rate(pizza_http_requests_total[5m]))
sum by (service, status) (rate(pizza_http_requests_total[5m]))
sum(rate(pizza_orders_total{status="failed"}[5m]))
```

---

## Shape 2 — "What fraction is bad?"

```promql
sum(rate(METRIC{bad="yes"}[5m]))
/
sum(rate(METRIC[5m]))
```

Use for: error ratio, cache hit ratio, success rate. **This is what an SLI is.**

Rules:
- Both sides must have the SAME label shape or you get an empty result.
- Wrap both in `sum()` (both become label-less) — easiest way to guarantee that.
- Returns 0.0–1.0. Grafana unit: **Percent (0.0-1.0)**.
- Returns NaN when the denominator is 0. Alert on traffic absence separately.

---

## Shape 3 — "How slow is it for the unlucky ones?"

```promql
histogram_quantile(0.95,
  sum by (le, LABEL) (rate(METRIC_seconds_bucket[5m]))
)
```

Use for: p50 / p95 / p99 latency.

Rules:
- `le` MUST stay in the `by` clause. It is the bucket ladder.
- `le` must NEVER go in the Grafana legend.
- You cannot average percentiles. Sum the buckets, then take the quantile.
- Precision is limited by your bucket boundaries. Put a bucket at your SLO
  threshold or you cannot measure your own SLO.

Average latency (for contrast — use sparingly, it hides tails):
```promql
sum by (service) (rate(METRIC_seconds_sum[5m]))
/
sum by (service) (rate(METRIC_seconds_count[5m]))
```

---

## Shape 4 — "What is the current level?"

```promql
SOME_gauge
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
```

Use for: memory used, disk used, queue depth, connections open.

Gauges need no `rate()`. If you find yourself writing `rate(some_gauge)`, stop —
you have the wrong metric type.

---

## Shape 5 — "Normalise against capacity"

```promql
node_load1 / scalar(count(count by (cpu) (node_cpu_seconds_total)))
```

Use for: load per core, usage vs limit, percent of quota.

Raw numbers are meaningless without their denominator. Load 4 is fine on
16 cores and fatal on 2.

---

# The traps, in one place

| Symptom | Cause | Fix |
|---|---|---|
| Empty result from a division | Label sets don't match | `scalar()` or `on()`, or `sum()` both sides |
| Huge negative spike | Raw counter arithmetic | Always use `rate()` / `increase()` |
| Gaps in a latency panel | No requests → NaN | Expected. Don't "connect nulls" |
| p95 wildly higher than reality | Bucket ladder too coarse | Add buckets near the range you care about |
| Impossibly large totals | cAdvisor cgroup roll-ups | Filter by `name`, use `max by (name)` |
| Alert never fires during outage | Ratio is NaN when traffic is 0 | Separate "no traffic" alert |
| Prometheus memory climbing | Cardinality growth | Check `topk(10, count by (__name__)({__name__=~".+"}))` |

---

# Selectors

```promql
metric{service="orders"}          exact match
metric{service!="orders"}         not equal
metric{status=~"5.."}             regex match
metric{name!~".*k6-run.*"}        regex NOT match
```

Regexes are anchored automatically — `5..` means the whole value, not a substring.

---

# Aggregation operators

```promql
sum by (x) (...)      add up, keep label x
avg by (x) (...)      average — careful, hides outliers
max by (x) (...)      largest — good for deduplicating
min by (x) (...)
count by (x) (...)    how many series
topk(5, ...)          five largest — great for finding cardinality hogs
```

`by (x)` keeps only `x`. `without (x)` keeps everything except `x`.

---

# Drills — do these without looking

1. Requests per second, per service.
2. Same, but only 5xx responses.
3. What fraction of gateway requests are 5xx?
4. p99 latency of the `/order` route.
5. Which container is using the most memory right now?
6. How many distinct time series does `pizza_http_requests_total` have?
7. Memory used as a fraction of total, on the host.
8. Orders per second that failed, over the last 30 minutes.

Answers are all one of the five shapes above.
