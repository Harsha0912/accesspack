"""Conservative HTML-only checks used when Node/axe-core is unavailable."""

from __future__ import annotations

from bs4 import BeautifulSoup


def _text(el):
    if el is None:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def _accessible_name(el):
    for attr in ("aria-label", "aria-labelledby", "title", "alt"):
        val = el.get(attr)
        if val and str(val).strip():
            return str(val).strip()
    return _text(el)


def _node(el, extra=None):
    soup_id = el.get("id")
    name = el.name or "*"
    selector = name
    if soup_id:
        selector = name + "#" + str(soup_id)
    elif el.get("class"):
        selector = name + "." + ".".join(str(c) for c in el.get("class")[:2])
    html = str(el)[:240]
    node = {"target": [selector], "html": html, "failureSummary": extra or ""}
    return node


def run_python_checks(html, url):
    soup = BeautifulSoup(html, "html.parser")
    violations = []

    imgs = []
    for img in soup.find_all("img"):
        if not img.has_attr("alt"):
            imgs.append(_node(img, "Image is missing an alt attribute"))
    if imgs:
        violations.append({
            "id": "image-alt",
            "impact": "critical",
            "help": "Images must have alternate text",
            "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/image-alt",
            "description": "Ensures <img> elements have an alt attribute.",
            "tags": ["wcag2a", "wcag111"],
            "nodes": imgs[:25],
        })

    html_el = soup.find("html")
    lang = (html_el.get("lang") if html_el else None) or ""
    if html_el is None or not str(lang).strip():
        violations.append({
            "id": "html-has-lang",
            "impact": "serious",
            "help": "html element must have a lang attribute",
            "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/html-has-lang",
            "description": "Ensures every HTML document has a lang attribute",
            "tags": ["wcag2a", "wcag311"],
            "nodes": [_node(html_el or soup, "Missing lang on html")],
        })

    empty_buttons = []
    for btn in soup.find_all("button"):
        if btn.get("aria-hidden") in ("true", True):
            continue
        if not _accessible_name(btn):
            empty_buttons.append(_node(btn, "Button has no discernible text"))
    if empty_buttons:
        violations.append({
            "id": "button-name",
            "impact": "critical",
            "help": "Buttons must have discernible text",
            "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/button-name",
            "description": "Ensures buttons have an accessible name",
            "tags": ["wcag2a", "wcag412"],
            "nodes": empty_buttons[:25],
        })

    empty_links = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if href is None and not a.get("role"):
            continue
        if not _accessible_name(a):
            empty_links.append(_node(a, "Link has no discernible text"))
    if empty_links:
        violations.append({
            "id": "link-name",
            "impact": "serious",
            "help": "Links must have discernible text",
            "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/link-name",
            "description": "Ensures links have an accessible name",
            "tags": ["wcag2a", "wcag244", "wcag412"],
            "nodes": empty_links[:25],
        })

    unlabeled = []
    controls = soup.find_all(["input", "select", "textarea"])
    for el in controls:
        itype = (el.get("type") or "text").lower()
        if itype in ("hidden", "submit", "button", "reset", "image"):
            continue
        if el.get("aria-label") or el.get("aria-labelledby") or el.get("title"):
            continue
        eid = el.get("id")
        if eid and soup.find("label", attrs={"for": eid}):
            continue
        if el.find_parent("label"):
            continue
        unlabeled.append(_node(el, "Form control has no associated label"))
    if unlabeled:
        violations.append({
            "id": "label",
            "impact": "critical",
            "help": "Form elements must have labels",
            "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/label",
            "description": "Ensures form inputs have an associated label",
            "tags": ["wcag2a", "wcag131", "wcag332", "wcag412"],
            "nodes": unlabeled[:25],
        })

    frames = []
    for fr in soup.find_all(["iframe", "frame"]):
        title = (fr.get("title") or "").strip()
        if not title and not (fr.get("aria-label") or "").strip():
            frames.append(_node(fr, "iframe is missing a title"))
    if frames:
        violations.append({
            "id": "frame-title",
            "impact": "serious",
            "help": "Frames must have an accessible name",
            "helpUrl": "https://dequeuniversity.com/rules/axe/4.10/frame-title",
            "description": "Ensures iframe elements have a title attribute",
            "tags": ["wcag2a", "wcag241", "wcag412"],
            "nodes": frames[:25],
        })

    return {
        "engine": "python-fallback",
        "engineVersion": "0.1.0",
        "url": url,
        "violations": violations,
        "incomplete": [],
        "passes": [],
        "inapplicable": [],
        "fallback_note": (
            "Node/axe-core was unavailable. Applied a conservative HTML-only subset: "
            "images without alt, missing lang, empty buttons/links, missing form labels, "
            "iframe without title. This is not equivalent to axe-core."
        ),
    }
