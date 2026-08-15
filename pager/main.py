"""
YOUR PAGER.

Alertmanager POSTs here when an alert fires. In production this would be
PagerDuty, Opsgenie or Splunk On-Call. Here it is 60 lines of Python so you can
see exactly what an alert payload contains - which is more than most engineers
who have been on-call for years can say.

Open http://localhost:8090 to see your page history.
"""
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="pager")

PAGES: list[dict] = []  # in-memory only; restarting the container clears it


@app.post("/alert")
async def receive(request: Request):
    payload = await request.json()
    for alert in payload.get("alerts", []):
        PAGES.insert(0, {
            "received": datetime.now().strftime("%H:%M:%S"),
            "status": alert.get("status"),
            "name": alert.get("labels", {}).get("alertname"),
            "severity": alert.get("labels", {}).get("severity"),
            "summary": alert.get("annotations", {}).get("summary", ""),
            "runbook": alert.get("annotations", {}).get("runbook_url", ""),
        })
    del PAGES[200:]
    return {"received": len(payload.get("alerts", []))}


@app.get("/", response_class=HTMLResponse)
async def index():
    rows = "".join(
        f"<tr class='{p['status']}'><td>{p['received']}</td><td>{p['status']}</td>"
        f"<td>{p['severity']}</td><td><b>{p['name']}</b><br><small>{p['summary']}</small></td>"
        f"<td>{'<a href=' + p['runbook'] + '>runbook</a>' if p['runbook'] else ''}</td></tr>"
        for p in PAGES
    )
    return f"""<html><head><title>Pager</title><meta http-equiv=refresh content=5>
    <style>body{{font-family:sans-serif;margin:2rem}}table{{border-collapse:collapse;width:100%}}
    td{{padding:.5rem;border-bottom:1px solid #ddd;vertical-align:top}}
    tr.firing{{background:#fdeaea}}tr.resolved{{background:#eef7ee}}</style></head>
    <body><h1>Pager &mdash; {len(PAGES)} pages</h1><table>{rows}</table></body></html>"""
