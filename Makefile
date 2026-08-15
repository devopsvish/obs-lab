.PHONY: up down logs smoke load chaos-clear ps reload

up:            ## start app + metrics + alerting
	docker compose up -d --build

logs-on:       ## add Loki + Promtail
	docker compose --profile logs up -d

traces-on:     ## add Tempo
	docker compose --profile traces up -d

down:
	docker compose --profile logs --profile traces --profile load down

nuke:          ## down + delete volumes (fresh start)
	docker compose --profile logs --profile traces --profile load down -v

ps:
	docker compose ps

logs:
	docker compose logs -f --tail=50

smoke:         ## 30s traffic to prove the stack works
	docker compose --profile load run --rm k6 run /scripts/smoke.js

load:          ## steady background traffic (ctrl-C to stop)
	docker compose --profile load run --rm k6 run /scripts/steady.js

reload:        ## hot-reload Prometheus rules without restarting it
	curl -sX POST http://localhost:9090/-/reload && echo "prometheus reloaded"

chaos-clear:
	./chaos/chaos.sh clear-all
