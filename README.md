# Accesspack

Paste a URL. Get a VPAT-shaped report in a minute.

Accesspack fetches public HTML and runs an automated WCAG 2.2 scan.

This is informational only. It is not a legal determination, not a certified VPAT, and not a substitute for a human WCAG/EAA audit.

## Local setup

Use Python 3.11+ and Node 18+. Install Python deps from requirements.txt and JS deps from package.json. Start the ASGI app module app.main:app on 0.0.0.0, reading PORT from the environment (8000 locally).

Set UNLOCK_KEY (default demo). Open the home page, paste https://example.com, then add key=demo on the results URL to preview paid downloads.

## Tests

pytest from the project root.

## API

POST /api/scan with JSON url returns a free summary (counts plus top 5 issue titles).
Header X-Unlock-Key or query key unlocks node details and download links.
GET /api/vpat.pdf and GET /api/statement.pdf return 402 unless unlocked.
GET /api/vpat.md and GET /api/statement.html use the same gate.
GET /health.
GET /buy is a Polar stub: checkout wires when Polar is connected. Preview with key=demo. No fake charge.

## Deploy

render.yaml uses a Python web service. Start command: uvicorn app.main:app bound to 0.0.0.0 and the platform PORT.

Node is required at runtime for axe-core. Native Python images may lack Node. The service always tries the Node helper first. If Node is missing, it applies a conservative HTML-only subset: images without alt, missing lang, empty buttons/links, missing form labels, iframe without title. That subset is not equivalent to axe-core.

## Security

Only http and https. Blocks localhost, private/reserved IPs, metadata 169.254.169.254, .internal, embedded credentials, file: and data:. Max 3 redirects, IP re-checked each hop. 12s timeout, 2MB cap. Page JS is not evaluated in Python.

## Cache and limits

Ten-minute cache in memory and /tmp/accesspack-cache. No database. HTML snapshot only. See STATUS.md.
