#!/usr/bin/env bash
# Fault injection control.
#
#   ./chaos/chaos.sh set <service> '<json>'   apply a fault
#   ./chaos/chaos.sh clear <service>          remove a fault
#   ./chaos/chaos.sh clear-all                remove every fault
#   ./chaos/chaos.sh show                     list active faults
#
# Example:
#   ./chaos/chaos.sh set bank '{"latency_ms":900,"error_rate":0.2}'
#
# During game day your mentor gives you a scenario number. Run it WITHOUT
# reading it. Finding out what broke is the entire exercise.
set -euo pipefail
R="docker compose exec -T redis redis-cli"

case "${1:-}" in
  set)   $R SET "chaos:$2" "$3" ;;
  clear) $R DEL "chaos:$2" ;;
  clear-all)
    for s in gateway orders payments bank; do $R DEL "chaos:$s" >/dev/null; done
    echo "all faults cleared" ;;
  show)
    for s in gateway orders payments bank; do
      v=$($R GET "chaos:$s" || true)
      [ -n "$v" ] && echo "$s -> $v"
    done
    echo "(done)" ;;
  *) sed -n '2,12p' "$0" ;;
esac
