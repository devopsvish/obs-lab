// Steady background traffic - your "customers".
// Run:  docker compose --profile load run --rm k6 run /scripts/steady.js
import http from "k6/http";
import { check, sleep } from "k6";

const TARGET = __ENV.TARGET || "http://gateway:8000";

export const options = {
  scenarios: {
    browsing: { executor: "constant-vus", vus: 5, duration: "30m", exec: "browse" },
    ordering: { executor: "constant-arrival-rate", rate: 6, timeUnit: "1s",
                duration: "30m", preAllocatedVUs: 20, exec: "order" },
  },
};

export function browse() {
  const r = http.get(`${TARGET}/menu`);
  check(r, { "menu ok": (res) => res.status === 200 });
  sleep(1);
}

const ITEMS = ["margherita", "pepperoni", "paneer tikka"];

export function order() {
  const item = ITEMS[Math.floor(Math.random() * ITEMS.length)];
  const r = http.post(`${TARGET}/order`,
    JSON.stringify({ item, value_rupees: 350 }),
    { headers: { "Content-Type": "application/json" } });
  check(r, { "order ok": (res) => res.status === 200 });
}
