"""Tools for Research Analyst Agno Agents.

Provides access to the research knowledge base containing benchmarks, technical whitepapers,
and industry reports, allowing the Research Agent to search and cite verified sources.
"""

from typing import Any, Dict, List, Set
from app.data.research_knowledge_base import SAMPLE_RESEARCH_DOCUMENTS

# Thread-local / query-level source tracking container
_last_consulted_sources: Set[str] = set()
_last_consulted_media: List[Dict[str, Any]] = []


def get_last_consulted_sources() -> List[str]:
    """Retrieve the document titles consulted during the most recent research session."""
    return sorted(list(_last_consulted_sources))


def get_last_consulted_media() -> List[Dict[str, Any]]:
    """Retrieve the media diagrams and charts associated with consulted documents."""
    return list(_last_consulted_media)


def clear_consulted_sources() -> None:
    """Reset the consulted sources and media trackers before starting a new inquiry."""
    _last_consulted_sources.clear()
    _last_consulted_media.clear()


def search_research_knowledge_base(query: str) -> str:
    """Search the research knowledge base for relevant benchmarks, statistics, and whitepapers.

    Args:
        query: The research keywords, topic, hypothesis, or technical questions to search for.

    Returns:
        A formatted string containing relevant excerpts, metrics, and citations from the research library.
    """
    if not query or not query.strip():
        return "No query provided. Please specify research topics, keywords, or hypotheses."

    query_tokens = [w.lower().strip("?,.;:\"'()") for w in query.split() if len(w) > 2]
    matched_docs = []

    for doc in SAMPLE_RESEARCH_DOCUMENTS:
        score = 0
        doc_keywords = [k.lower() for k in doc.get("keywords", [])]
        title_lower = doc.get("title", "").lower()
        content_lower = doc.get("content", "").lower()
        category_lower = doc.get("category", "").lower()

        for token in query_tokens:
            if token in doc_keywords:
                score += 4
            if token in title_lower:
                score += 5
            if token in category_lower:
                score += 3
            if token in content_lower:
                score += 1

        if score > 0:
            matched_docs.append((score, doc))

    if not matched_docs:
        available_titles = ", ".join(f"'{d['title']}'" for d in SAMPLE_RESEARCH_DOCUMENTS)
        return (
            f"No direct matches found in research library for '{query}'. "
            f"Available knowledge domains in library include: {available_titles}."
        )

    # Sort descending by relevance score
    matched_docs.sort(key=lambda item: item[0], reverse=True)

    results: List[str] = []
    for _, doc in matched_docs[:3]:  # Top 3 most relevant documents
        _last_consulted_sources.add(doc["title"])
        if doc.get("media"):
            media_item = doc["media"]
            if not any(m.get("url") == media_item.get("url") for m in _last_consulted_media):
                _last_consulted_media.append(media_item)

        content_preview = doc["content"][:400] + ("..." if len(doc["content"]) > 400 else "")
        results.append(
            f"[{doc['title']}]\nCategory: {doc.get('category', 'General')}\n"
            f"Source: {doc.get('author', 'Research Institute')} ({doc.get('date', 'Recent')})\n"
            f"Executive Summary: {doc['summary']}\nKey Findings & Evidence:\n{content_preview}\n"
        )

    return "\n".join(results)


# Backward compatibility aliases
def search_legal_library(query: str) -> str:
    """Compatibility alias mapping legal queries to research knowledge base."""
    return search_research_knowledge_base(query)


def get_all_research_documents() -> List[Dict[str, Any]]:
    """Return all available research documents metadata."""
    return [
        {
            "id": d["id"],
            "title": d["title"],
            "category": d["category"],
            "summary": d["summary"],
            "author": d.get("author", "N/A"),
            "date": d.get("date", "N/A"),
        }
        for d in SAMPLE_RESEARCH_DOCUMENTS
    ]


def scrape_web_page(url: str) -> str:
    """Scrape and extract readable research content from a live web page URL.

    Args:
        url: The web URL to fetch and analyze.

    Returns:
        Cleaned text extract and metadata from the webpage.
    """
    from app.agents.rag import scrape_web_content

    result = scrape_web_content(url)
    title = result.get("title", url)
    _last_consulted_sources.add(f"Web Source: {title} ({url})")

    if result.get("status") == "error":
        return f"[Web Scraping Error for {url}]: {result.get('summary')}"

    return (
        f"[LIVE SCRAPED WEB SOURCE: {title}]\n"
        f"URL: {url}\n"
        f"Content Extract:\n{result.get('summary')}\n"
        f"[END OF WEB SOURCE]"
    )
