from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_clarify_for_vague_input() -> None:
    payload = {"messages": [{"role": "user", "content": "I need an assessment"}]}
    resp = client.post("/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["reply"], str)
    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False


def test_chat_returns_shl_recommendations_for_specific_input() -> None:
    payload = {
        "messages": [
            {"role": "user", "content": "Hiring mid-level Java developer with stakeholder communication needs"}
        ]
    }
    resp = client.post("/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert 1 <= len(data["recommendations"]) <= 10
    for rec in data["recommendations"]:
        assert rec["url"].startswith("https://www.shl.com/")


def test_off_topic_refusal() -> None:
    payload = {"messages": [{"role": "user", "content": "Give legal advice on labor law"}]}
    resp = client.post("/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["recommendations"] == []

