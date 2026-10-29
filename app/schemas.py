"""Pydantic schemas for Research Analyst Agents API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class ResearchRequest(BaseModel):
    """Schema for incoming research inquiry or topic."""
    topic: Optional[str] = Field(
        default=None,
        description="The research topic, inquiry, or hypothesis to analyze.",
        examples=["Evaluate state-of-the-art multi-agent LLM reasoning benchmarks and latency."]
    )
    question: Optional[str] = Field(
        default=None,
        description="Backward-compatible alias for topic."
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific sub-domains or focus pillars."
    )
    depth: Optional[str] = Field(
        default="comprehensive",
        description="Depth of research: 'comprehensive', 'executive', or 'technical'."
    )

    @model_validator(mode="before")
    @classmethod
    def reconcile_topic_or_question(cls, data: dict):
        if not isinstance(data, dict):
            return data
        topic_val = data.get("topic") or data.get("question")
        if not topic_val or not str(topic_val).strip():
            raise ValueError("A research topic or inquiry must be provided.")
        trimmed = str(topic_val).strip()
        if len(trimmed) < 4:
            raise ValueError("Research topic must contain at least 4 non-whitespace characters.")
        data["topic"] = trimmed
        data["question"] = trimmed
        return data


class ResearchResponse(BaseModel):
    """Schema for multi-agent synthesized research report response."""
    status: str = Field(default="success", description="Status of the research analysis.")
    topic: str = Field(..., description="The research topic analyzed.")
    report: str = Field(..., description="Synthesized, verified comprehensive research report.")
    answer: str = Field(..., description="Compatibility alias containing the report.")
    sources: List[str] = Field(default_factory=list, description="Citations and research library references.")
    agents: List[str] = Field(default_factory=list, description="Names of collaborating agents involved.")
    disclaimer: str = Field(..., description="System analytical disclaimer.")


class HealthResponse(BaseModel):
    """Schema for application health check endpoint."""
    status: str = Field(default="healthy")
    app_name: str
    groq_configured: bool
    model: str
    agents: List[str]


# Backward compatibility aliases
LegalQuestionRequest = ResearchRequest
LegalBotResponse = ResearchResponse
