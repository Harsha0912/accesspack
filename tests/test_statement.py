from app.config import DISCLAIMER
from app.reports import generate_statement_html, generate_statement_pdf, generate_vpat_markdown, generate_vpat_pdf

SCAN = {
    "final_url": "https://example.com/",
    "requested_url": "https://example.com/",
    "scanned_at": "2026-08-19T12:00:00Z",
    "engine": "axe-core",
    "engine_version": "4.10.3",
    "user_agent": "Accesspack/0.1.0",
    "summary": {"violations": 1, "incomplete": 0, "passes": 8, "inapplicable": 2},
    "impact_counts": {"critical": 0, "serious": 1, "moderate": 0, "minor": 0},
    "score": 90,
    "violations": [{
        "id": "html-has-lang",
        "impact": "serious",
        "help": "html element must have a lang attribute",
        "tags": ["wcag2a", "wcag311"],
        "wcag": ["3.1.1"],
        "nodes": [{"target": ["html"], "html": "<html>"}],
    }],
}

def test_statement_html_contains_disclaimer():
    html = generate_statement_html(SCAN, company="Acme", email="a@acme.test")
    low = html.lower()
    assert "informational only" in low
    assert "not a certified vpat" in low
    assert "not a legal determination" in low
    assert "not a substitute for a human" in low
    assert DISCLAIMER.split(".")[0].lower() in low
    assert "[company name]" not in html.lower() or "acme" in html.lower()
    assert "acme" in html.lower()
    assert "a@acme.test" in html

def test_vpat_markdown_contains_disclaimer_and_en_note():
    md = generate_vpat_markdown(SCAN)
    low = md.lower()
    assert "informational only" in low
    assert "not a certified vpat" in low
    assert "en 301 549" in low
    assert "html-has-lang" in md

def test_pdfs_are_pdf_and_nonempty():
    v = generate_vpat_pdf(SCAN)
    s = generate_statement_pdf(SCAN, company="Acme", email="a@acme.test")
    assert v.startswith(b"%PDF")
    assert s.startswith(b"%PDF")
    assert len(v) > 500 and len(s) > 500
