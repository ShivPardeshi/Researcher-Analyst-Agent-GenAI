"""Tests for Media and Image Support in Research Analyst Agents."""

import base64
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.agents.tools import search_research_knowledge_base, get_last_consulted_media, clear_consulted_sources

client = TestClient(app)


def test_static_media_svg_files_accessible():
    """Verify that sample benchmark SVGs are served properly by static file mount."""
    svgs = [
        "/static/media/multi_agent_benchmarks.svg",
        "/static/media/bess_cost_curve.svg",
        "/static/media/gaa_nanosheet_2nm.svg",
        "/static/media/quantum_qubit_scaling.svg",
    ]
    for path in svgs:
        response = client.get(path)
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers.get("content-type", "")
        assert b"<svg" in response.content


def test_knowledge_base_returns_grounding_media():
    """Verify that searching knowledge base records associated media diagrams."""
    clear_consulted_sources()
    # Search for multi-agent reasoning
    output = search_research_knowledge_base("multi-agent reasoning benchmarks")
    assert "Autonomous Multi-Agent" in output

    media = get_last_consulted_media()
    assert len(media) >= 1
    assert any("/static/media/multi_agent_benchmarks.svg" in m.get("url", "") for m in media)


def test_research_with_base64_image(monkeypatch):
    monkeypatch.setattr("app.config.is_provider_configured", lambda: True)

    # 1x1 transparent GIF in base64
    sample_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    mock_result = {
        "report": "### Key Findings\nAnalysis of the attached benchmark chart confirms 94.6% accuracy.",
        "answer": "### Key Findings\nAnalysis of the attached benchmark chart confirms 94.6% accuracy.",
        "sources": ["Autonomous Multi-Agent Architectures"],
        "topic": "Analyze benchmark chart",
        "agents": ["Research Agent", "Analysis & Verification Agent", "Report Generation Agent"],
        "media": [
            {
                "type": "chart",
                "url": "/static/media/multi_agent_benchmarks.svg",
                "title": "Multi-Agent Benchmarks",
                "caption": "Reasoning benchmark comparison.",
            }
        ],
    }

    with patch("app.main.run_research_workflow", return_value=mock_result):
        response = client.post(
            "/research",
            json={
                "topic": "Analyze the attached benchmark chart.",
                "image_base64": sample_b64,
                "image_filename": "test_chart.png",
                "image_mime_type": "image/png",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["media"]) >= 2  # 1 user attachment + 1 grounding diagram
        # Check user attachment
        user_att = next(m for m in data["media"] if m.get("role") == "user_attachment")
        assert user_att["title"] == "test_chart.png"
        assert "data:image/png;base64" in user_att["url"]


def test_research_image_only_auto_generates_topic(monkeypatch):
    """Verify that providing an image without topic automatically constructs a research query."""
    monkeypatch.setattr("app.config.is_provider_configured", lambda: True)

    sample_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    mock_result = {
        "report": "### Report on Attached Image",
        "answer": "### Report on Attached Image",
        "sources": [],
        "topic": "Auto generated",
        "agents": ["Research Agent"],
        "media": [],
    }

    with patch("app.main.run_research_workflow", return_value=mock_result):
        response = client.post(
            "/research",
            json={
                "image_base64": sample_b64,
                "image_filename": "hardware_diagram.png",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "hardware_diagram.png" in data["topic"]
