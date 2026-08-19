from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import httpx

from app.config import FETCH_MAX_BYTES, FETCH_MAX_REDIRECTS, FETCH_TIMEOUT_S, USER_AGENT

BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
    "metadata.google.internal",
    "metadata.goog",
    "metadata",
}

BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".invalid")

EXTRA_BLOCKED_NETS = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
    ipaddress.ip_network("2001:db8::/32"),
)

class FetchError(Exception):
    status_code = 400
    code = "fetch_error"

    def __init__(self, message, status_code=None, code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code

class BlockedURLError(FetchError):
    status_code = 400
    code = "blocked_url"

class InvalidURLError(FetchError):
    status_code = 400
    code = "invalid_url"

def _host_of(url):
    parsed = urlparse(url)
    return (parsed.hostname or "").rstrip(".").lower()

def is_blocked_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    mapped = getattr(addr, "ipv4_mapped", None)
    if mapped is not None:
        addr = mapped
    if (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    ):
        return True
    return any(addr in net for net in EXTRA_BLOCKED_NETS)

def _hostname_blocked(host):
    if not host:
        return True
    if host in BLOCKED_HOSTS:
        return True
    if any(host.endswith(suf) for suf in BLOCKED_SUFFIXES):
        return True
    try:
        if is_blocked_ip(host):
            return True
    except ValueError:
        pass
    return False

def check_url_allowed(url):
    if not isinstance(url, str) or not url.strip():
        raise InvalidURLError("URL is required")
    raw = url.strip()
    low = raw.lower()
    if low.startswith(("file:", "data:", "javascript:", "ftp:", "sftp:", "gopher:")):
        raise BlockedURLError("Only http and https URLs are allowed")
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError("Only http and https URLs are allowed")
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise InvalidURLError("URL must include a hostname")
    if parsed.username or parsed.password:
        raise BlockedURLError("URLs with embedded credentials are not allowed")
    if _hostname_blocked(host):
        raise BlockedURLError("That host is not allowed")
    netloc = parsed.netloc
    if "@" in netloc:
        netloc = netloc.split("@", 1)[-1]
    return parsed._replace(fragment="", netloc=netloc).geturl()

def resolve_host_ips(host):
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchError("Could not resolve host: " + host, status_code=400, code="dns") from exc
    ips = []
    for info in infos:
        ip = info[4][0]
        if ip not in ips:
            ips.append(ip)
    if not ips:
        raise FetchError("No addresses for host: " + host, status_code=400, code="dns")
    for ip in ips:
        if is_blocked_ip(ip):
            raise BlockedURLError("That host resolves to a private or reserved address")
    return ips

def _assert_live_url(url):
    normalized = check_url_allowed(url)
    resolve_host_ips(_host_of(normalized))
    return normalized

def fetch_html(url):
    current = _assert_live_url(url)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
        "Accept-Language": "en",
    }
    last_error = None
    with httpx.Client(
        timeout=httpx.Timeout(FETCH_TIMEOUT_S, connect=8.0),
        follow_redirects=False,
        max_redirects=0,
        headers=headers,
        trust_env=False,
    ) as client:
        for hop in range(FETCH_MAX_REDIRECTS + 1):
            try:
                with client.stream("GET", current) as resp:
                    if resp.status_code in (301, 302, 303, 307, 308):
                        loc = resp.headers.get("location")
                        if not loc:
                            raise FetchError("Redirect without Location", status_code=502, code="upstream")
                        nxt = urljoin(current, loc)
                        if hop >= FETCH_MAX_REDIRECTS:
                            raise FetchError("Too many redirects", status_code=502, code="redirects")
                        current = _assert_live_url(nxt)
                        continue
                    if resp.status_code >= 400:
                        raise FetchError(
                            "Upstream returned HTTP " + str(resp.status_code),
                            status_code=502,
                            code="upstream",
                        )
                    chunks = []
                    size = 0
                    for chunk in resp.iter_bytes():
                        size += len(chunk)
                        if size > FETCH_MAX_BYTES:
                            raise FetchError(
                                "Response exceeded the 2MB size cap",
                                status_code=413,
                                code="too_large",
                            )
                        chunks.append(chunk)
                    raw = b"".join(chunks)
                    ctype = (resp.headers.get("content-type") or "").lower()
                    text = raw.decode(resp.encoding or "utf-8", errors="replace")
                    head = text.lstrip()[:64].lower()
                    looks_html = (
                        "html" in ctype
                        or "xml" in ctype
                        or head.startswith("<!doctype")
                        or head.startswith("<html")
                        or "<" in text[:200]
                    )
                    if not looks_html:
                        raise FetchError("URL did not return HTML", status_code=422, code="not_html")
                    return {
                        "requested_url": url.strip(),
                        "final_url": str(resp.url),
                        "status": resp.status_code,
                        "content_type": ctype,
                        "bytes": size,
                        "html": text,
                        "user_agent": USER_AGENT,
                    }
            except httpx.TimeoutException as exc:
                raise FetchError("Fetch timed out (12s limit)", status_code=504, code="timeout") from exc
            except httpx.RequestError as exc:
                last_error = exc
                raise FetchError("Could not fetch URL: " + str(exc), status_code=502, code="upstream") from exc
    raise FetchError("Could not fetch URL: " + str(last_error), status_code=502, code="upstream")
