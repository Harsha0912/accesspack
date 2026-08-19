"""Accesspack FastAPI application."""
from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import __version__
from app.config import DISCLAIMER, EN301549_NOTE, SCAN_JS, TOOL_NAME, TOOL_VERSION
from app.fetch import FetchError
from app.payload import is_unlocked, public_payload
from app.reports import (
    generate_statement_html,
    generate_statement_pdf,
    generate_vpat_markdown,
    generate_vpat_pdf,
)
from app.scan_engine import node_available, scan_url

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title=TOOL_NAME, version=TOOL_VERSION, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


class ScanBody(BaseModel):
    url: str = Field(..., min_length=3, max_length=2048)


def _unlocked(request: Request) -> bool:
    return is_unlocked(request.headers.get("X-Unlock-Key"), request.query_params.get("key"))


def _err(exc: FetchError):
    return JSONResponse(
        {
            "error": exc.code,
            "detail": str(exc),
            "informational_only": True,
            "disclaimer": DISCLAIMER,
        },
        status_code=exc.status_code,
    )


def _need_url(request: Request) -> str:
    return (request.query_params.get("url") or "").strip()


def _paywall():
    return JSONResponse(
        {
            "error": "payment_required",
            "detail": "Full reports are part of the paid pack.",
            "buy": "/buy",
            "preview": "Use ?key=demo or header X-Unlock-Key to preview.",
            "informational_only": True,
            "disclaimer": DISCLAIMER,
        },
        status_code=402,
    )


def _run_scan(url: str):
    return scan_url(url)


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "accesspack",
        "version": __version__,
        "disclaimer": DISCLAIMER,
        "engines": {
            "node": shutil.which("node") is not None,
            "axe_helper": node_available(),
            "scan_js": SCAN_JS.is_file(),
        },
    }


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/scan")
def scan_page():
    return FileResponse(STATIC / "scan.html")


@app.get("/legal")
def legal_page():
    return FileResponse(STATIC / "legal.html")


@app.get("/buy")
def buy_page():
    return FileResponse(STATIC / "buy.html")


@app.get("/favicon.svg")
def favicon():
    return FileResponse(STATIC / "favicon.svg")


@app.post("/api/scan")
def api_scan(body: ScanBody, request: Request):
    try:
        scan = _run_scan(body.url)
    except FetchError as exc:
        return _err(exc)
    payload = public_payload(scan, _unlocked(request))
    if payload.get("unlocked"):
        q = body.url
        payload["downloads"] = {
            "vpat_pdf": "/api/vpat.pdf?url=" + q,
            "vpat_md": "/api/vpat.md?url=" + q,
            "statement_pdf": "/api/statement.pdf?url=" + q,
            "statement_html": "/api/statement.html?url=" + q,
        }
    return payload


def _paid_scan(request: Request):
    if not _unlocked(request):
        return None, _paywall()
    url = _need_url(request)
    if not url:
        return None, JSONResponse({"detail": "url query parameter required", "disclaimer": DISCLAIMER}, status_code=400)
    try:
        return _run_scan(url), None
    except FetchError as exc:
        return None, _err(exc)


@app.get("/api/vpat.pdf")
def vpat_pdf(request: Request):
    scan, err = _paid_scan(request)
    if err:
        return err
    data = generate_vpat_pdf(scan, company=request.query_params.get("company"))
    return Response(data, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=accesspack-vpat.pdf", "X-Disclaimer": DISCLAIMER})


@app.get("/api/vpat.md")
def vpat_md(request: Request):
    scan, err = _paid_scan(request)
    if err:
        return err
    text = generate_vpat_markdown(scan, company=request.query_params.get("company"))
    return Response(text, media_type="text/markdown; charset=utf-8", headers={"Content-Disposition": "attachment; filename=accesspack-vpat.md"})


@app.get("/api/statement.pdf")
def statement_pdf(request: Request):
    scan, err = _paid_scan(request)
    if err:
        return err
    data = generate_statement_pdf(
        scan,
        company=request.query_params.get("company"),
        email=request.query_params.get("email"),
    )
    return Response(data, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=accesspack-statement.pdf", "X-Disclaimer": DISCLAIMER})


@app.get("/api/statement.html")
def statement_html(request: Request):
    scan, err = _paid_scan(request)
    if err:
        return err
    html = generate_statement_html(
        scan,
        company=request.query_params.get("company"),
        email=request.query_params.get("email"),
    )
    return Response(html, media_type="text/html; charset=utf-8")


@app.exception_handler(Exception)
def unhandled(_request: Request, exc: Exception):
    if isinstance(exc, FetchError):
        return _err(exc)
    return JSONResponse(
        {"error": "internal", "detail": "Unexpected error", "disclaimer": DISCLAIMER, "informational_only": True},
        status_code=500,
    )
