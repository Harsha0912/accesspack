"""Run axe-core via Node; fall back to conservative Python checks."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone

from app import cache
from app.config import SCAN_JS, TOOL_NAME, TOOL_VERSION, USER_AGENT
from app.fetch import fetch_html
from app.python_checks import run_python_checks
from app.wcag import criteria_for_rule

NODE_TIMEOUT_S = 20


def node_available():
    return shutil.which("node") is not None and SCAN_JS.is_file()


def _run_node(html, url):
    if not node_available():
        return None, "node or scripts/scan.js missing"
    try:
        proc = subprocess.run(
            ["node", str(SCAN_JS), url],
            input=html,
            capture_output=True,
            text=True,
            timeout=NODE_TIMEOUT_S,
            cwd=str(SCAN_JS.parent.parent),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "axe helper failed").strip()
        return None, err[:400]
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as exc:
        return None, "axe helper returned invalid JSON: " + str(exc)


def _impact_counts(violations):
    counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for v in violations:
        impact = (v.get("impact") or "moderate").lower()
        if impact not in counts:
            impact = "moderate"
        counts[impact] += 1
    return counts


def _score(impact_counts):
    deduction = (
        impact_counts.get("critical", 0) * 15
        + impact_counts.get("serious", 0) * 10
        + impact_counts.get("moderate", 0) * 5
        + impact_counts.get("minor", 0) * 2
    )
    return max(0, min(100, 100 - deduction))


def _enrich(raw, fetch_meta):
    violations = raw.get("violations") or []
    for v in violations:
        v["wcag"] = criteria_for_rule(v.get("id"), v.get("tags"))
        for n in v.get("nodes") or []:
            html = n.get("html") or ""
            if len(html) > 240:
                n["html"] = html[:240] + "..."
    incomplete = raw.get("incomplete") or []
    passes = raw.get("passes") or []
    inapplicable = raw.get("inapplicable") or []
    impact = _impact_counts(violations)
    scanned_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "engine": raw.get("engine"),
        "engine_version": raw.get("engineVersion"),
        "fallback_note": raw.get("fallback_note"),
        "requested_url": fetch_meta["requested_url"],
        "final_url": fetch_meta["final_url"],
        "scanned_at": scanned_at,
        "user_agent": fetch_meta.get("user_agent") or USER_AGENT,
        "http_status": fetch_meta.get("status"),
        "bytes": fetch_meta.get("bytes"),
        "summary": {
            "violations": len(violations),
            "incomplete": len(incomplete),
            "passes": len(passes) if isinstance(passes, list) else int(passes or 0),
            "inapplicable": len(inapplicable) if isinstance(inapplicable, list) else int(inapplicable or 0),
        },
        "impact_counts": impact,
        "score": _score(impact),
        "violations": violations,
        "incomplete": incomplete,
        "passes": passes,
        "inapplicable": inapplicable,
    }


def scan_url(url, use_cache=True):
    if use_cache:
        hit = cache.get(url)
        if hit:
            return hit
    fetch_meta = fetch_html(url)
    raw, err = _run_node(fetch_meta["html"], fetch_meta["final_url"])
    if raw is None:
        raw = run_python_checks(fetch_meta["html"], fetch_meta["final_url"])
        if err:
            raw["fallback_note"] = (raw.get("fallback_note") or "") + " Node error: " + err
    result = _enrich(raw, fetch_meta)
    if use_cache:
        cache.put(url, result)
        if result["final_url"] != url:
            cache.put(result["final_url"], result)
    return result
