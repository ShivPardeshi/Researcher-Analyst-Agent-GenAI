"""Tests for Research Analyst Agent Architecture and Knowledge Base Retrieval."""

from app.agents.research_team import AGENT_NAMES, build_research_team
from app.agents.tools import (
    clear_consulted_sources,
    get_last_consulted_sources,
    search_research_knowledge_base,
    get_all_research_documents,
)


def test_agent_names_list():
    """Verify exactly 3 designated research agents are present."""
    assert len(AGENT_NAMES) == 3
    assert "Research Agent" in AGENT_NAMES
    assert "Analysis & Verification Agent" in AGENT_NAMES
    assert "Report Generation Agent" in AGENT_NAMES


def test_build_research_team():
    """Verify Agno Team composition and configuration."""
    team = build_research_team(api_key="mock_test_key_xyz")
    assert team.name == "Research Analyst Team"
    assert len(team.members) == 3

    member_names = [m.name for m in team.members]
    assert "Research Agent" in member_names
    assert "Analysis & Verification Agent" in member_names
    assert "Report Generation Agent" in member_names

    # Check that Research Agent has the search_research_knowledge_base tool
    research_agent = next(m for m in team.members if m.name == "Research Agent")
    assert research_agent.tools is not None
    assert len(research_agent.tools) >= 1


def test_search_research_knowledge_base_ai():
    """Verify search tool returns AI reasoning benchmarks."""
    clear_consulted_sources()
    result = search_research_knowledge_base("multi-agent coordination latency benchmark")
    assert "Autonomous Multi-Agent Architectures" in result
    sources = get_last_consulted_sources()
    assert any("Autonomous Multi-Agent Architectures" in s for s in sources)


def test_search_research_knowledge_base_energy():
    """Verify search tool returns clean tech and battery storage data."""
    clear_consulted_sources()
    result = search_research_knowledge_base("battery storage BESS solar grid")
    assert "Battery Storage" in result or "Renewable Energy" in result
    sources = get_last_consulted_sources()
    assert any("Battery Storage" in s or "Renewable Energy" in s for s in sources)


def test_search_research_knowledge_base_empty_query():
    """Verify graceful message on empty search query."""
    result = search_research_knowledge_base("")
    assert "No query provided" in result


def test_get_all_research_documents():
    """Verify knowledge base returns multiple curated whitepapers."""
    docs = get_all_research_documents()
    assert len(docs) >= 5
    assert any("Quantum" in d["title"] for d in docs)
    assert any("Semiconductor" in d["title"] for d in docs)
