from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert "disclaimer" in r.json()

def test_home_renders():
    r = client.get("/")
    assert r.status_code == 200
    assert b"Accesspack" in r.content
    assert b"informational only" in r.content.lower()

def test_legal_and_buy():
    legal = client.get("/legal")
    buy = client.get("/buy")
    assert legal.status_code == 200
    assert b"not a certified vpat" in legal.content.lower()
    assert buy.status_code == 200
    assert b"Checkout wires when Polar is connected" in buy.content

def test_pdf_paywall():
    r = client.get("/api/vpat.pdf", params={"url": "https://example.com/"})
    assert r.status_code in (402, 403)
    assert r.json()["disclaimer"]

def test_scan_rejects_localhost():
    r = client.post("/api/scan", json={"url": "http://localhost/"})
    assert r.status_code == 400
