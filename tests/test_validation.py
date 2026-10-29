"""Tests for Research Analyst Input Validation and Error Handling."""

from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_research_empty_payload():
    """Verify empty POST payload returns 422 Unprocessable Entity."""
    response = client.post("/research", json={})
    assert response.status_code == 422


def test_research_short_topic():
    """Verify topic below 4 characters is rejected with 422."""
    response = client.post("/research", json={"topic": "ai"})
    assert response.status_code == 422


def test_research_whitespace_only():
    """Verify topic containing only whitespace is rejected with 422."""
    response = client.post("/research", json={"topic": "          "})
    assert response.status_code == 422


def test_research_missing_api_key(monkeypatch):
    """Verify 503 Service Unavailable when API key is unconfigured."""
    monkeypatch.setattr("app.config.GROQ_API_KEY", "")
    monkeypatch.setattr("app.config.GEMINI_API_KEY", "")
    response = client.post("/research", json={"topic": "Analyze quantum error correction thresholds."})
    assert response.status_code == 503
    data = response.json()
    assert "API key is not configured" in data["detail"]


def test_research_success_with_mocked_workflow(monkeypatch):
    """Verify successful report formatting when multi-agent workflow returns an answer."""
    monkeypatch.setattr("app.config.GROQ_API_KEY", "mock_valid_key_123")

    mock_result = {
        "report": "### Executive Summary\nMulti-agent coordination reduces hallucinations by 42%.",
        "answer": "### Executive Summary\nMulti-agent coordination reduces hallucinations by 42%.",
        "sources": ["Autonomous Multi-Agent Architectures & LLM Reasoning Benchmarks (2025-2026)"],
        "topic": "Multi-agent LLM reasoning benchmarks",
        "agents": ["Research Agent", "Analysis & Verification Agent", "Report Generation Agent"],
    }

    with patch("app.main.run_research_workflow", return_value=mock_result):
        response = client.post(
            "/research",
            json={"topic": "Multi-agent LLM reasoning benchmarks"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "42%" in data["report"]
        assert len(data["sources"]) >= 1
        assert "Disclaimer:" in data["disclaimer"]
        assert "Research Agent" in data["agents"]

        # Also test backward-compatible /ask endpoint
        ask_response = client.post(
            "/ask",
            json={"question": "Multi-agent LLM reasoning benchmarks"}
        )
        assert ask_response.status_code == 200
        ask_data = ask_response.json()
        assert ask_data["status"] == "success"
        assert "42%" in ask_data["answer"]
