// Quick 30-second check that the stack is wired up correctly.
import http from "k6/http";
import { check } from "k6";

const TARGET = __ENV.TARGET || "http://gateway:8000";
export const options = { vus: 2, duration: "30s" };

export default function () {
  check(http.get(`${TARGET}/menu`), { "menu 200": (r) => r.status === 200 });
  check(http.post(`${TARGET}/order`,
        JSON.stringify({ item: "margherita", value_rupees: 350 }),
        { headers: { "Content-Type": "application/json" } }),
        { "order 200": (r) => r.status === 200 });
}
