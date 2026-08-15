# The 8-hour plan

## Hour 1 — Concepts (no laptop)
- The three pillars: metrics, logs, traces. What each is *physically*, and the
  cost model that makes them different tools.
- Cardinality, and the rule for deciding which pillar a fact belongs in.
- Monitoring vs observability. Known-unknowns vs unknown-unknowns.
- Signal frameworks: Four Golden Signals, RED (for services), USE (for
  resources). When each applies.
- Symptom vs cause. The most important distinction in on-call.

## Hour 2 — Stand up the stack
- `make up`, verify all targets are UP in Prometheus.
- Pull vs push. Scrape interval vs evaluation interval vs alert `for:`.
- Metric types: counter, gauge, histogram, summary — and when each is wrong.
- Read the raw `/metrics` output by hand. Understand the exposition format.

## Hour 3 — Instrument the app (you write code)
- Write the RED middleware in `common/telemetry.py`.
- Add business metrics: orders, revenue, payment outcomes.
- PromQL properly: `rate`, `increase`, `sum by`, `histogram_quantile`.
- Why `avg` latency lies, and why you cannot average percentiles.

## Hour 3.5 — Infrastructure monitoring (USE method)   [added on request]
- node-exporter: CPU modes, load average, memory *actually* available,
  disk saturation, network. Why `node_memory_MemFree` is the wrong metric.
- cAdvisor: container CPU throttling, memory working set vs RSS, OOM kills,
  restart loops.
- Build a "Machine + Containers" dashboard.
- Why infra dashboards are for *diagnosis*, and must almost never page you.

## Hour 4 — Logs and traces
- Structured JSON logging; log levels that mean something.
- Loki label discipline (the same cardinality rule, different backend).
- Distributed tracing: spans, context propagation, sampling.
- Correlate: metric spike → exemplar → trace → the exact log line.

## Hour 5 — SLI, SLO, SLA, error budget
- Define real SLIs for the pizza shop. Availability and latency.
- Recording rules, and why you precompute.
- Error budget maths. Build a burn-down dashboard.
- Where SLA (the contract) differs from SLO (the target).

## Hour 6 — Alerting done properly
- Symptom-based alerting. Multi-window multi-burn-rate alerts.
- Alertmanager: routing, grouping, inhibition, silences.
- Severity model: page vs ticket. Write a runbook per alert.
- Alert fatigue, and how to measure whether your alerting is any good.

## Hours 7–8 — Game day and RCA
- Three injected incidents. You are on-call. You do not know what broke.
- Incident command: roles, severity declaration, comms, timeline.
- Mitigate first, diagnose second.
- Blameless postmortem with a causal chain and real action items.
