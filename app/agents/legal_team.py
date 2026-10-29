"""Backward compatibility bridge for legal_team module."""

from app.agents.research_team import (
    AGENT_NAMES,
    create_model_instance,
    build_research_team,
    run_research_workflow,
    build_legal_team,
    run_legal_workflow,
)

__all__ = [
    "AGENT_NAMES",
    "create_model_instance",
    "build_research_team",
    "run_research_workflow",
    "build_legal_team",
    "run_legal_workflow",
]
