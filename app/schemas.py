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
    image_base64: Optional[str] = Field(
        default=None,
        description="Optional base64 encoded image or chart attachment."
    )
    image_filename: Optional[str] = Field(
        default=None,
        description="Optional original filename of the attached image."
    )
    image_mime_type: Optional[str] = Field(
        default=None,
        description="Optional MIME type of the attached image (e.g. 'image/png', 'image/jpeg')."
    )
    image_url: Optional[str] = Field(
        default=None,
        description="Optional URL pointing to an online diagram or chart image."
    )
    pdf_base64: Optional[str] = Field(
        default=None,
        description="Optional base64 encoded PDF research paper or whitepaper."
    )
    pdf_filename: Optional[str] = Field(
        default=None,
        description="Optional original filename of the attached PDF."
    )
    web_urls: Optional[List[str]] = Field(
        default=None,
        description="Optional list of live web page URLs to scrape and ingest for RAG analysis."
    )

    @model_validator(mode="before")
    @classmethod
    def reconcile_topic_or_question(cls, data: dict):
        if not isinstance(data, dict):
            return data
        topic_val = data.get("topic") or data.get("question")
        has_attachment = bool(
            data.get("image_base64")
            or data.get("image_url")
            or data.get("pdf_base64")
            or data.get("web_urls")
        )

        if not topic_val or not str(topic_val).strip():
            if data.get("pdf_base64"):
                fname = data.get("pdf_filename") or "uploaded PDF document"
                topic_val = f"Analyze and synthesize the research findings, data points, and methodology from the attached document ({fname})."
            elif data.get("web_urls"):
                urls_str = ", ".join(data.get("web_urls")[:2])
                topic_val = f"Scrape, evaluate, and synthesize research intelligence from web source(s): {urls_str}."
            elif has_attachment:
                fname = data.get("image_filename") or "attached research document/chart"
                topic_val = f"Analyze the data, benchmarks, and claims in the attached image ({fname}) and generate a verified research report."
            else:
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
    media: List[dict] = Field(
        default_factory=list,
        description="List of attached or referenced visual media items (charts, diagrams, evidence)."
    )


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
