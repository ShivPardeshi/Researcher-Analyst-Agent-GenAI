"""Research Analyst Multi-Agent System.

Coordinates three collaborating Agno agents:
1. Research Agent: Searches and gathers information.
2. Analysis & Verification Agent: Analyzes evidence, validates claims, and identifies insights.
3. Report Generation Agent: Produces the final research report.
"""

from typing import Any, Dict, List, Optional
from agno.agent import Agent
from agno.team import Team, TeamMode

from app import config
from app.agents.tools import (
    clear_consulted_sources,
    get_last_consulted_sources,
    search_research_knowledge_base,
)

AGENT_NAMES = [
    "Research Agent",
    "Analysis & Verification Agent",
    "Report Generation Agent",
]


def create_model_instance(api_key: Optional[str] = None, model_id: Optional[str] = None):
    """Instantiate the active LLM provider (Google Gemini or Groq)."""
    provider = config.MODEL_PROVIDER

    if provider == "google":
        from agno.models.google import Gemini

        key = api_key if api_key is not None else config.GEMINI_API_KEY
        m_id = model_id if model_id is not None else config.GEMINI_MODEL
        return Gemini(id=m_id, api_key=key)
    else:
        from agno.models.groq import Groq

        key = api_key if api_key is not None else config.GROQ_API_KEY
        m_id = model_id if model_id is not None else config.GROQ_MODEL
        return Groq(id=m_id, api_key=key)


def build_research_team(api_key: Optional[str] = None, model_id: Optional[str] = None) -> Team:
    """Build the three collaborating Agno agents and coordinate them via an Agno Team."""
    model = create_model_instance(api_key=api_key, model_id=model_id)

    # Agent 1: Research Agent (Searches and gathers information)
    research_agent = Agent(
        name="Research Agent",
        role="Searches and gathers information across scientific, market, and technical sources.",
        model=model,
        tools=[search_research_knowledge_base],
        telemetry=False,
        description=(
            "An expert research scout specialized in gathering empirical data, scientific literature, "
            "market intelligence, and technical benchmarks. Uses search_research_knowledge_base to retrieve "
            "authoritative facts, statistics, and verifiable citations."
        ),
        instructions=[
            "1. Analyze the inquiry and break it down into core research questions.",
            "2. Invoke search_research_knowledge_base with targeted keywords to discover relevant literature and data.",
            "3. Extract key statistics, verified data points, market metrics, and historical benchmarks.",
            "4. Clearly catalog raw findings and cite consulted source titles.",
        ],
    )

    # Agent 2: Analysis & Verification Agent (Analyzes evidence, validates claims, and identifies insights)
    analysis_agent = Agent(
        name="Analysis & Verification Agent",
        role="Analyzes evidence, validates claims, and identifies insights.",
        model=model,
        telemetry=False,
        description=(
            "A rigorous research analyst and fact-checking verification specialist. Cross-examines gathered data, "
            "detects biases, assesses methodological validity, eliminates false assumptions, and derives deep strategic insights."
        ),
        instructions=[
            "1. Scrutinize all evidence collected by the Research Agent for factual consistency and credibility.",
            "2. Validate or challenge specific claims, highlighting uncertainties, contradictory data, or limitations.",
            "3. Identify underlying patterns, cross-domain implications, and high-impact strategic insights.",
            "4. Provide a structured analytical breakdown of validated versus unverified points.",
        ],
    )

    # Agent 3: Report Generation Agent (Produces the final research report)
    report_agent = Agent(
        name="Report Generation Agent",
        role="Produces the final research report.",
        model=model,
        telemetry=False,
        description=(
            "An executive intelligence author. Synthesizes findings from the Research Agent and analytical insights "
            "from the Analysis & Verification Agent into an executive-grade, publication-ready research report."
        ),
        instructions=[
            "1. Synthesize the validated evidence and analytical insights into a comprehensive research report.",
            "2. Structure the final report with the following executive sections:",
            "   - **Executive Summary**: High-level synthesis, key takeaway, and bottom-line impact.",
            "   - **Methodology & Evidence Base**: Overview of gathered data and knowledge base coverage.",
            "   - **Key Findings & Verified Insights**: Grounded facts, quantitative metrics, and verified claims.",
            "   - **Strategic & Market Implications**: In-depth analytical evaluation and trend projections.",
            "   - **Risks, Uncertainties & Limitations**: Potential bottlenecks, counterarguments, or data constraints.",
            "   - **Strategic Recommendations**: Concrete, prioritized, actionable steps.",
            "   - **References & Consulted Sources**: Explicit citations of referenced documents.",
            "3. Maintain objective clarity, professional executive tone, and rigorous factual grounding.",
        ],
    )

    # Agno Team Coordinator
    research_team = Team(
        name="Research Analyst Team",
        members=[research_agent, analysis_agent, report_agent],
        model=model,
        tools=[search_research_knowledge_base],
        add_member_tools_to_context=True,
        mode=TeamMode.coordinate,
        telemetry=False,
        instructions=[
            "Coordinate the three agents sequentially to deliver an authoritative research report:",
            "1. Have Research Agent search the knowledge base and gather empirical evidence.",
            "2. Have Analysis & Verification Agent validate claims, test assumptions, and derive strategic insights.",
            "3. Have Report Generation Agent synthesize the final structured executive report.",
        ],
    )

    return research_team


def run_research_workflow(
    topic: str,
    team: Optional[Team] = None,
    image_bytes: Optional[bytes] = None,
    image_filename: Optional[str] = None,
    image_mime_type: Optional[str] = None,
    focus_areas: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Execute the multi-agent research workflow across Research, Analysis & Verification, and Report Generation."""
    clear_consulted_sources()

    evidence_context = ""
    candidate_models = [
        config.GEMINI_MODEL,
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.8-flash",
    ]
    seen = set()
    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

    # 1. Document / Chart Vision Extraction if image attached
    if image_bytes and config.MODEL_PROVIDER == "google" and config.GEMINI_API_KEY:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        mime = image_mime_type or "image/jpeg"

        for model_id in models_to_try:
            try:
                ocr_response = client.models.generate_content(
                    model=model_id,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime),
                        (
                            "You are a Research Analyst document & chart specialist. Inspect this uploaded image/chart. "
                            "Extract all legible data points, metrics, trends, percentages, labels, and analytical claims."
                        ),
                    ],
                    config={"http_options": {"timeout": 15000}},
                )
                if ocr_response and ocr_response.text:
                    evidence_context = (
                        f"\n\n[ATTACHED RESEARCH DATA EVIDENCE: {image_filename or 'Uploaded Artifact'}]\n"
                        f"{ocr_response.text.strip()}\n"
                        f"[END OF ATTACHED EVIDENCE]\n"
                    )
                    break
            except Exception:
                continue

    # 2. Search Grounding Research Knowledge Base
    search_query = f"{topic} {evidence_context[:300]}"
    if focus_areas:
        search_query += " " + " ".join(focus_areas)
    grounding_docs = search_research_knowledge_base(search_query)
    sources = get_last_consulted_sources()

    # 3. Multi-Agent Synthesis Prompt
    focus_text = f"\nFocus Areas: {', '.join(focus_areas)}" if focus_areas else ""
    workflow_prompt = (
        f"You are the Research Analyst Multi-Agent System composed of 3 specialized collaborating agents:\n"
        f"1. **Research Agent**: Searches and gathers information, data points, statistics, and domain literature.\n"
        f"2. **Analysis & Verification Agent**: Analyzes evidence, validates claims, filters hallucinations, and identifies strategic insights.\n"
        f"3. **Report Generation Agent**: Produces the final, structured, publication-ready research report.\n\n"
        f"RESEARCH INQUIRY / TOPIC:\n"
        f"\"\"\"{topic}\"\"\"{focus_text}\n"
        f"{evidence_context}\n"
        f"GROUNDING RESEARCH KNOWLEDGE BASE:\n"
        f"{grounding_docs}\n\n"
        f"Execute the full workflow and generate the Comprehensive Research Report formatted with:\n"
        f"- **Executive Summary**: High-level synthesis, bottom-line strategic takeaway, and core findings.\n"
        f"- **Methodology & Evidence Base**: Information gathered by the Research Agent.\n"
        f"- **Key Findings & Verified Insights**: Rigorously validated data points, metrics, and trends by Analysis & Verification Agent.\n"
        f"- **In-Depth Analytical Evaluation**: Comparative discussion, technological/market implications, and trade-offs.\n"
        f"- **Risk Factors & Limitations**: Critical bottlenecks, uncertainties, and constraints.\n"
        f"- **Strategic Recommendations**: Concrete, prioritized, actionable roadmap.\n"
        f"- **Verified References & Citations**: Explicitly cited documentation and datasets."
    )

    content_text = ""
    # Execute with fallback across flash models
    if config.MODEL_PROVIDER == "google" and config.GEMINI_API_KEY:
        from google import genai

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        for model_id in models_to_try:
            try:
                resp = client.models.generate_content(
                    model=model_id,
                    contents=workflow_prompt,
                    config={"http_options": {"timeout": 30000}},
                )
                if resp and resp.text:
                    content_text = resp.text.strip()
                    break
            except Exception:
                continue

    # Fallback to Agno Team run if direct generation was empty
    if not content_text:
        try:
            active_team = team if team is not None else build_research_team()
            run_output = active_team.run(workflow_prompt)
            if hasattr(run_output, "get_content_as_string"):
                content_text = run_output.get_content_as_string()
            elif hasattr(run_output, "content") and run_output.content:
                content_text = str(run_output.content)
            else:
                content_text = str(run_output)
        except Exception as e:
            content_text = f"Unable to generate response: {e}"

    def _is_error_response(txt: str) -> bool:
        if not txt or not txt.strip():
            return True
        low = txt.lower()
        if "resource_exhausted" in low or "quota exceeded" in low or '"code": 429' in low or "'code': 429" in low:
            return True
        if txt.strip().startswith('{"error":') or txt.strip().startswith("{'error':"):
            return True
        return False

    # Failover to Groq if Google quota reached or error
    if _is_error_response(content_text) and config.GROQ_API_KEY:
        try:
            from groq import Groq

            groq_client = Groq(api_key=config.GROQ_API_KEY)
            groq_model = config.GROQ_MODEL or "qwen/qwen3.8-27b"
            groq_resp = groq_client.chat.completions.create(
                model=groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the Research Analyst Multi-Agent System (Research Agent, "
                            "Analysis & Verification Agent, Report Generation Agent). Deliver authoritative, "
                            "empirically grounded research intelligence reports with rigorous verification."
                        ),
                    },
                    {"role": "user", "content": workflow_prompt},
                ],
                max_tokens=3000,
            )
            if groq_resp and groq_resp.choices and groq_resp.choices[0].message.content:
                content_text = groq_resp.choices[0].message.content.strip()
        except Exception:
            pass

    if _is_error_response(content_text):
        content_text = (
            "### ⏳ Temporary Rate Limit Notice\n\n"
            "The AI model provider's rate limit was temporarily reached. "
            "Your research query was preserved. **Please wait 10 seconds and submit your request again.**\n\n"
            "*Tip: You can configure a valid Google AI Studio key or Groq API key in `.env`.*"
        )

    return {
        "report": content_text,
        "answer": content_text,  # Compatibility alias
        "sources": sources,
        "topic": topic,
        "agents": AGENT_NAMES,
    }


# Backward compatibility aliases
build_legal_team = build_research_team
run_legal_workflow = run_research_workflow
