# Accesspack status

## Works

- Marketing page, scan results page, legal, buy stub, health
- SSRF-safe HTML fetch (http/https, private IP block, 12s, 2MB, 3 redirects)
- axe-core via scripts/scan.js when Node is present
- Python fallback checks when Node is missing
- Free vs paid payload (X-Unlock-Key or key query; default demo)
- VPAT 2.5 draft as markdown and PDF; EAA statement as HTML and PDF
- 10-minute URL cache in memory and /tmp
- Disclaimer on pages, PDFs, and API JSON

## Start command

uvicorn app.main:app --host 0.0.0.0 --port 8000

On Render, the same module binds to the platform PORT.

## Known limits

- HTML-only snapshot. JavaScript-rendered apps are not evaluated as users see them.
- Not a legal audit, not a certified VPAT, not a WCAG or EAA conformity assessment.
- Python fallback is a small conservative subset, not axe-core.
- No authenticated pages, no site crawl, no Polar checkout yet.
- DNS is re-checked each redirect hop; residual DNS rebinding between resolve and connect is possible.
