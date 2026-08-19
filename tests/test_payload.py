from app.payload import assert_free_redacted, is_unlocked, public_payload

SAMPLE = {
    "final_url": "https://example.com/",
    "requested_url": "https://example.com/",
    "scanned_at": "2026-08-19T12:00:00Z",
    "tool": {"name": "Accesspack", "version": "0.1.0"},
    "engine": "axe-core",
    "engine_version": "4.10.3",
    "user_agent": "Accesspack/0.1.0",
    "summary": {"violations": 2, "incomplete": 1, "passes": 10, "inapplicable": 4},
    "impact_counts": {"critical": 1, "serious": 1, "moderate": 0, "minor": 0},
    "score": 75,
    "violations": [
        {
            "id": "image-alt",
            "impact": "critical",
            "help": "Images must have alternate text",
            "wcag": ["1.1.1"],
            "nodes": [{"target": ["img.hero"], "html": "<img src=x>", "failureSummary": "fix"}],
        },
        {
            "id": "html-has-lang",
            "impact": "serious",
            "help": "html element must have a lang attribute",
            "wcag": ["3.1.1"],
            "nodes": [{"target": ["html"], "html": "<html>", "failureSummary": "fix"}],
        },
    ],
    "incomplete": [],
    "passes": [{"id": "document-title", "help": "Documents must have a title"}],
}

def test_free_redacts_nodes_and_full_violations():
    free = public_payload(SAMPLE, unlocked=False)
    assert free["unlocked"] is False
    assert "violations" not in free
    assert "nodes" not in free
    assert len(free["top_issues"]) <= 5
    assert free["top_issues"][0]["id"] == "image-alt"
    assert "nodes" not in free["top_issues"][0]
    assert "html" not in free["top_issues"][0]
    assert assert_free_redacted(free) is True
    assert "informational only" in free["disclaimer"].lower()

def test_paid_includes_nodes():
    paid = public_payload(SAMPLE, unlocked=True)
    assert paid["unlocked"] is True
    assert paid["violations"][0]["nodes"][0]["html"]
    assert paid["user_agent"]

def test_unlock_header_and_query():
    assert is_unlocked("demo", None, expected="demo") is True
    assert is_unlocked(None, "demo", expected="demo") is True
    assert is_unlocked("nope", None, expected="demo") is False
    assert is_unlocked(None, None, expected="demo") is False
