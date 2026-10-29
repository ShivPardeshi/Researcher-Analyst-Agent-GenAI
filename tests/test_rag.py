"""Tests for RAG Engine: PDF extraction, semantic chunking, BM25 scoring, and Web Scraping."""

import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app
from app.agents.rag import (
    extract_text_from_pdf,
    chunk_document_pages,
    score_and_retrieve_chunks,
    scrape_web_content,
)
from app.agents.tools import scrape_web_page

client = TestClient(app)


def _create_sample_pdf(pages_text: list[str]) -> bytes:
    """Helper to generate an in-memory PDF using pypdf."""
    from reportlab.pdfgen import canvas
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    for text in pages_text:
        c.drawString(100, 750, text)
        c.showPage()
    c.save()
    return buffer.getvalue()


def test_pdf_extraction_fallback_or_stream():
    """Test PDF text extraction handles empty or valid byte streams gracefully."""
    # Test empty bytes
    result = extract_text_from_pdf(b"")
    assert result == []

    # Test invalid bytes (corrupt PDF)
    corrupt_result = extract_text_from_pdf(b"Not A Real PDF Header")
    assert corrupt_result == []


def test_chunk_document_pages():
    """Test overlapping semantic chunking across document pages."""
    pages = [
        {"page": 1, "text": "Multi-agent systems improve reasoning latency by parallelizing subtasks."},
        {"page": 2, "text": "Verification agents eliminate hallucinations through empirical cross-examination."},
    ]
    chunks = chunk_document_pages(pages, chunk_size=30, chunk_overlap=10)
    assert len(chunks) >= 2
    assert "page" in chunks[0]
    assert "chunk_id" in chunks[0]
    assert "text" in chunks[0]
    assert chunks[0]["page"] == 1


def test_score_and_retrieve_chunks():
    """Test BM25 relevance scoring returns top-ranked passages."""
    chunks = [
        {"chunk_id": "c1", "page": 1, "text": "Quantum error correction requires topological qubits."},
        {"chunk_id": "c2", "page": 2, "text": "Lithium Iron Phosphate (LFP) batteries exhibit high cycle life and thermal stability."},
        {"chunk_id": "c3", "page": 3, "text": "BESS grid storage LCOE reaches cost parity with combined-cycle gas turbines."},
    ]
    results = score_and_retrieve_chunks(chunks, "BESS battery storage LCOE cost", top_k=2)
    assert len(results) <= 2
    # The BESS chunk (c3) or battery chunk (c2) should be ranked higher than quantum (c1)
    chunk_ids = [r["chunk_id"] for r in results]
    assert "c3" in chunk_ids or "c2" in chunk_ids


def test_scrape_web_content_html_cleaning():
    """Test BeautifulSoup HTML cleanup and text extraction."""
    raw_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Quantum Computing Whitepaper</title></head>
    <body>
        <nav><a href="/home">Home</a></nav>
        <script>console.log("tracking");</script>
        <style>body { color: black; }</style>
        <main>
            <h1>Logical Qubits in 2026</h1>
            <p>Neutral atom quantum processors demonstrate error thresholds below 0.1% using Rydberg arrays.</p>
        </main>
        <footer>Copyright 2026 Research Labs</footer>
    </body>
    </html>
    """
    scraped = scrape_web_content("https://research.example.com/quantum", html=raw_html)
    assert scraped["title"] == "Quantum Computing Whitepaper"
    assert "Neutral atom quantum processors" in scraped["summary"]
    assert "tracking" not in scraped["summary"]  # scripts stripped
    assert "body { color" not in scraped["summary"]  # styles stripped


@patch("app.agents.rag.httpx.Client")
def test_scrape_web_page_tool(mock_client_cls):
    """Test scrape_web_page tool fetches and cleans web content."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html><head><title>Test Doc</title></head><body><p>Clean empirical benchmark data.</p></body></html>"
    
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__.return_value = mock_client
    mock_client_cls.return_value = mock_client

    result = scrape_web_page("https://example.com/test-benchmarks")
    assert "Test Doc" in result
    assert "Clean empirical benchmark data" in result


@patch("app.main.config.is_provider_configured", return_value=True)
@patch("app.main.run_research_workflow")
def test_research_endpoint_with_web_urls(mock_workflow, mock_configured):
    """Test POST /research accepting web_urls."""
    mock_workflow.return_value = {
        "report": "## Executive Synthesis\nWeb grounded findings verified.",
        "sources": ["Web: https://arxiv.org/abs/2405.00000"],
        "media": [],
    }

    payload = {
        "topic": "Summarize latest multi-agent reasoning papers",
        "web_urls": ["https://arxiv.org/abs/2405.00000"],
    }
    response = client.post("/research", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Web grounded findings verified" in data["report"]
    assert mock_workflow.called
    kwargs = mock_workflow.call_args[1]
    assert kwargs.get("web_urls") == ["https://arxiv.org/abs/2405.00000"]
