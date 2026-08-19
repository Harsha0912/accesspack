"""10-minute scan cache: memory plus /tmp files, keyed by URL."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path

from app.config import CACHE_DIR, CACHE_TTL_S

_lock = threading.Lock()
_memory = {}


def _key(url):
    return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()


def _path(key):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / (key + ".json")


def get(url):
    key = _key(url)
    now = time.time()
    with _lock:
        hit = _memory.get(key)
        if hit and hit[0] > now:
            return hit[1]
        path = _path(key)
        if path.is_file():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                exp = float(payload.get("_expires", 0))
                if exp > now:
                    data = payload.get("data")
                    _memory[key] = (exp, data)
                    return data
            except (OSError, ValueError, TypeError):
                return None
    return None


def put(url, data):
    key = _key(url)
    exp = time.time() + CACHE_TTL_S
    with _lock:
        _memory[key] = (exp, data)
        path = _path(key)
        tmp = path.with_suffix(".tmp")
        blob = json.dumps({"_expires": exp, "data": data}, ensure_ascii=False, default=str)
        tmp.write_text(blob, encoding="utf-8")
        tmp.replace(path)


def clear():
    with _lock:
        _memory.clear()
