import os
from pathlib import Path

TOOL_NAME = "Accesspack"
TOOL_VERSION = "0.1.0"
USER_AGENT = (
    "Accesspack/0.1.0 (+https://accesspack.app; informational accessibility scan)"
)

ROOT = Path(__file__).resolve().parent.parent
SCAN_JS = ROOT / "scripts" / "scan.js"

FETCH_TIMEOUT_S = 12.0
FETCH_MAX_BYTES = 2_000_000
FETCH_MAX_REDIRECTS = 3

CACHE_TTL_S = 10 * 60
CACHE_DIR = Path(os.environ.get("ACCESSPACK_CACHE_DIR", "/tmp/accesspack-cache"))

UNLOCK_KEY = os.environ.get("UNLOCK_KEY", "demo")

DISCLAIMER = (
    "This report is informational only. It is not a legal determination, "
    "not a certified VPAT, and not a substitute for a human WCAG/EAA audit."
)

EN301549_NOTE = (
    "EN 301 549 / EAA: this automated scan is evidence, not a conformity assessment."
)

PRICE_PACK = 29
PRICE_MONTHLY_COMING = 49
