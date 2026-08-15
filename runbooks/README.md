# Runbooks

One file per alert. An alert without a runbook is a 3am guessing game.

Every runbook must answer, in this order:

1. **What is broken, in customer terms.** Not "p99 latency > 2s" but
   "customers are waiting more than 2 seconds to place an order".
2. **How bad is it.** How do I tell a small blip from an outage?
3. **What do I check first.** The exact dashboard link and the exact query.
4. **How do I make the pain stop.** Mitigation comes before diagnosis.
5. **What if that does not work.** Escalation path.
6. **What this alert does NOT mean.** Known false-positive causes.

You will write one per alert in Hour 6.
