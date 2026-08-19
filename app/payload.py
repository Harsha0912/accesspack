"""Free vs paid payload classifier. Free never includes node details."""

from __future__ import annotations

import hmac
import os

from app.config import DISCLAIMER, EN301549_NOTE, UNLOCK_KEY


def provided_key(header_value, query_value):
    if header_value and str(header_value).strip():
        return str(header_value).strip()
    if query_value and str(query_value).strip():
        return str(query_value).strip()
    return None


def is_unlocked(header_value=None, query_value=None, expected=None):
    expected = expected if expected is not None else os.environ.get("UNLOCK_KEY", UNLOCK_KEY)
    got = provided_key(header_value, query_value)
    if got is None or expected is None:
        return False
    left = got.encode("utf-8")
    right = str(expected).encode("utf-8")
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)


def _top_issues(scan, limit=5):
    order = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
    items = []
    for v in scan.get("violations") or []:
        items.append({
            "id": v.get("id"),
            "impact": v.get("impact"),
            "help": v.get("help"),
            "count": len(v.get("nodes") or []),
            "wcag": v.get("wcag") or [],
        })
    items.sort(key=lambda i: (order.get((i.get("impact") or "").lower(), 9), -(i.get("count") or 0)))
    return items[:limit]


def public_payload(scan, unlocked):
    payload = {
        "informational_only": True,
        "disclaimer": DISCLAIMER,
        "en301549_note": EN301549_NOTE,
        "unlocked": bool(unlocked),
        "url": scan.get("final_url") or scan.get("requested_url"),
        "requested_url": scan.get("requested_url"),
        "scanned_at": scan.get("scanned_at"),
        "tool": scan.get("tool"),
        "engine": scan.get("engine"),
        "engine_version": scan.get("engine_version"),
        "summary": scan.get("summary"),
        "impact_counts": scan.get("impact_counts"),
        "score": scan.get("score"),
        "score_note": "Automated issue score, not a WCAG conformance level.",
        "top_issues": _top_issues(scan, 5),
    }
    if scan.get("fallback_note"):
        payload["fallback_note"] = scan["fallback_note"]
    if not unlocked:
        payload["upgrade"] = {
            "price_usd": 29,
            "what": "Dated VPAT 2.5 draft (WCAG 2.2 + EN 301 549 note) and EAA statement HTML/PDF.",
            "buy": "/buy",
            "preview": "Add ?key=demo (or X-Unlock-Key) to preview the paid pack.",
        }
        return payload
    payload["user_agent"] = scan.get("user_agent")
    payload["http_status"] = scan.get("http_status")
    payload["bytes"] = scan.get("bytes")
    payload["violations"] = scan.get("violations") or []
    payload["incomplete"] = scan.get("incomplete") or []
    payload["passes"] = scan.get("passes") or []
    return payload


def assert_free_redacted(payload):
    """Test helper: free payloads must not leak node HTML or full violation lists."""
    if payload.get("unlocked"):
        return True
    if "violations" in payload:
        return False
    if "nodes" in payload:
        return False
    for issue in payload.get("top_issues") or []:
        if "nodes" in issue or "html" in issue:
            return False
    return True
