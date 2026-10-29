"""RAG (Retrieval-Augmented Generation) & Web Scraping Engine.

Provides:
1. PDF Document Parsing & Passage Chunking
2. Relevance Scoring & Top-K Retrieval
3. Live Web Scraping with HTML boilerplate cleaning & metadata extraction
"""

import io
import re
import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger("research-analyst.rag")


# =========================================================
# PDF Parsing & Chunking Engine
# =========================================================

def extract_text_from_pdf(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """Extract page-indexed text passages from raw PDF bytes.

    Returns:
        List of dicts: [{"page": 1, "text": "..."}, ...]
    """
    if not pdf_bytes:
        return []

    pages_data: List[Dict[str, Any]] = []

    # 1. Try pypdf
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = re.sub(r"[ \t]+", " ", text).strip()
            if text:
                pages_data.append({"page": page_num, "text": text})

        if pages_data:
            return pages_data
    except Exception as e:
        logger.warning("pypdf extraction failed, attempting fallback: %s", e)

    # 2. Pure Python text stream fallback for stream-based PDFs
    try:
        raw_text = pdf_bytes.decode("latin-1", errors="ignore")
        # Extract text within BT ... ET blocks
        bt_blocks = re.findall(r"BT[\r\n]+(.*?)[\r\n]+ET", raw_text, re.DOTALL)
        extracted_strings = []
        for block in bt_blocks:
            for s in re.findall(r"\((.*?)\)[\r\n]*Tj", block):
                extracted_strings.append(s)

        if extracted_strings:
            combined = " ".join(extracted_strings)
            combined = re.sub(r"\s+", " ", combined).strip()
            if len(combined) > 20:
                pages_data.append({"page": 1, "text": combined})
    except Exception as e:
        logger.error("Fallback PDF extraction also failed: %s", e)

    return pages_data


def chunk_document_pages(
    pages: List[Dict[str, Any]], chunk_size: int = 500, overlap: int = 100, chunk_overlap: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Partition extracted document pages into overlapping semantic passages."""
    actual_overlap = chunk_overlap if chunk_overlap is not None else overlap
    chunks: List[Dict[str, Any]] = []

    for item in pages:
        page_num = item["page"]
        text = item["text"]

        words = text.split()
        if not words:
            continue

        start = 0
        chunk_idx = 1
        while start < len(words):
            end = min(start + chunk_size, len(words))
            passage = " ".join(words[start:end])
            chunks.append({
                "page": page_num,
                "chunk_id": f"p{page_num}_c{chunk_idx}",
                "text": passage,
            })
            if end >= len(words):
                break
            start += chunk_size - actual_overlap
            chunk_idx += 1

    return chunks


def score_and_retrieve_chunks(
    chunks: List[Dict[str, Any]], query: str, top_k: int = 4
) -> List[Dict[str, Any]]:
    """Retrieve top-K most relevant chunks using BM25-style token overlap and density."""
    if not chunks:
        return []

    tokens = [t.lower().strip("?,.;:\"'()") for t in query.split() if len(t) > 2]
    if not tokens:
        return chunks[:top_k]

    scored = []
    for chunk in chunks:
        chunk_text_lower = chunk["text"].lower()
        score = 0
        matches = 0

        for token in tokens:
            count = chunk_text_lower.count(token)
            if count > 0:
                matches += 1
                score += min(count, 5) * 2

        # Bonus for matching multiple distinct query tokens
        score += matches * 4

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    if scored:
        return [c for _, c in scored[:top_k]]
    return chunks[:top_k]


# =========================================================
# Live Web Scraping Engine
# =========================================================

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_web_content(
    url: str, max_chars: int = 6000, html: Optional[str] = None
) -> Dict[str, Any]:
    """Scrape and clean a web page URL.

    Returns dict with:
        url: target URL
        title: page title
        summary: clean extracted text content
        status: 'success' or 'error'
    """
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    try:
        if html is None:
            with httpx.Client(
                headers=DEFAULT_HEADERS,
                follow_redirects=True,
                timeout=12.0,
                verify=False,
            ) as client:
                resp = client.get(clean_url)

            if resp.status_code >= 400:
                return {
                    "url": clean_url,
                    "title": clean_url,
                    "summary": f"HTTP {resp.status_code} Error: Unable to retrieve web page.",
                    "status": "error",
                }

            html = resp.text

        # 1. Parse with BeautifulSoup
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Remove noise elements
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else clean_url

            # Prioritize article, main, or content containers
            content_root = soup.find("article") or soup.find("main") or soup.find("body") or soup
            text = content_root.get_text(separator="\n")

        except Exception:
            # Fallback regex-based HTML cleaner
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else clean_url
            no_scripts = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", no_scripts)

        # Clean whitespace and compress
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + "\n... [Content truncated for analysis]"

        return {
            "url": clean_url,
            "title": title,
            "summary": clean_text,
            "status": "success",
        }

    except Exception as exc:
        logger.warning("Failed to scrape URL %s: %s", clean_url, exc)
        return {
            "url": clean_url,
            "title": clean_url,
            "summary": f"Scrape Error: {exc}",
            "status": "error",
        }
