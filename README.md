# obs-lab — a pizza shop that breaks

An 8-hour hands-on lab for observability, SLOs, alerting, on-call and root
cause analysis. You will instrument a real 4-service system, define SLOs,
build burn-rate alerts, get paged during a game day, and write postmortems.

## Where to run it

- **Ubuntu EC2 instance** → `docs/ec2-setup.md` (recommended; t3.large)
- **WSL2 on a laptop** → `docs/wsl-setup.md`

**Security:** none of these tools has authentication, and Grafana runs with
anonymous admin. Your EC2 security group is the only control. Scope every
inbound rule to your own IP. Redis is deliberately not published at all.

## Ports

| URL | What |
|---|---|
| http://localhost:8000 | Gateway (the app) |
| http://localhost:9090 | Prometheus |
| http://localhost:3000 | Grafana (admin/admin) |
| http://localhost:9093 | Alertmanager |
| http://localhost:8090 | **Your pager** |
| http://localhost:9100 | node-exporter (machine metrics) |
| http://localhost:8080 | cAdvisor (container metrics) |
| http://localhost:3100 | Loki (logs profile) |
| http://localhost:3200 | Tempo (traces profile) |

## Quick start

```bash
make up          # build + start app, metrics, alerting, infra exporters
make ps          # 10 containers Up
make smoke       # 30 seconds of traffic
```

Then open http://localhost:9090/targets — the `pizza-app`, `node` and
`cadvisor` jobs must all be UP. (On EC2, open the SSH tunnel first.)

## Daily commands

```bash
make load          # steady background traffic
make logs-on       # add Loki + Promtail   (Hour 4)
make traces-on     # add Tempo             (Hour 4)
make reload        # reload Prometheus rules after editing them
make down          # stop
make nuke          # stop and wipe data
```

## Layout

```
app/            the pizza shop (gateway, orders, payments, bank)
  common/       shared config, logging, chaos, and YOUR telemetry module
prometheus/     scrape config + rules/ (you write the rules)
alertmanager/   routing (you extend it in Hour 6)
grafana/        datasources + dashboards (you build the dashboards)
loki/ promtail/ tempo/    log and trace backends
loadgen/        k6 traffic scripts
pager/          webhook receiver that shows your pages
chaos/          fault injection - do not read during game day
runbooks/       one per alert (you write these)
postmortems/    your three incidents
docs/           ec2-setup.md, wsl-setup.md, plan.md
```

## What you write, what you got for free

**Given to you:** the business logic, all the YAML plumbing, the load generator,
the pager, the chaos harness.

**You write:** every metric that matters, the middleware that records them, the
PromQL, the dashboards, the SLO definitions, the recording rules, the alert
rules, the runbooks, and the postmortems.

Search the repo for `TODO` to find your work.
