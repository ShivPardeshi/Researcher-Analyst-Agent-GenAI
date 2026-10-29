"""FastAPI Application for Research Analyst Agents — Multi-Agent Intelligence System.

Provides:
- GET /: Serves the interactive research dashboard frontend.
- POST /research: Coordinates the three Agno agents (Research -> Analysis & Verification -> Report Generation).
- POST /ask: Backward-compatible alias for /research.
- GET /health: Reports health status, active model, and the 3 collaborating agents.
- GET /topics: Returns available research knowledge base domains and sample documents.
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any
import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.agents.research_team import AGENT_NAMES, run_research_workflow
from app.agents.tools import get_all_research_documents
from app.schemas import HealthResponse, ResearchRequest, ResearchResponse

# Configure structured logging without leaking sensitive credentials
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("research-analyst")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Research Analyst Agents",
    description=(
        "Autonomous multi-agent research analysis system powered by 3 collaborating agents: "
        "Research Agent, Analysis & Verification Agent, and Report Generation Agent."
    ),
    version="2.0.0",
)

# Enable CORS for browser clients and container networking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", summary="Serve Research Analyst Dashboard", response_class=FileResponse)
async def serve_frontend():
    """Serve the single-page HTML application."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend index.html file not found in static assets directory.",
        )
    return FileResponse(str(index_file), media_type="text/html")


@app.get("/health", summary="Health Check", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Report application health, active model, and multi-agent system readiness."""
    return HealthResponse(
        status="healthy",
        app_name=f"{config.APP_NAME} — {config.APP_DESCRIPTION}",
        groq_configured=config.is_provider_configured(),
        model=config.get_active_model_name(),
        agents=AGENT_NAMES,
    )


@app.get("/topics", summary="Available Research Knowledge Base Domains")
async def list_topics() -> List[Dict[str, Any]]:
    """List curated topics and whitepapers available in the local knowledge base."""
    return get_all_research_documents()


@app.post("/research", summary="Execute Research Analysis Workflow", response_model=ResearchResponse)
async def execute_research(request: ResearchRequest) -> ResearchResponse:
    """Process a research topic through the 3 collaborating agents:
    1. Research Agent: Searches and gathers empirical information.
    2. Analysis & Verification Agent: Analyzes evidence, validates claims, and identifies insights.
    3. Report Generation Agent: Produces the final research report.
    """
    if not config.is_provider_configured():
        logger.warning("Invocation rejected: No valid API key configured in environment.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "API key is not configured. Please add your GEMINI_API_KEY (from https://aistudio.google.com/apikey) "
                "or GROQ_API_KEY (from https://console.groq.com/keys) to the .env file."
            ),
        )

    topic_query = request.topic or request.question or ""
    image_bytes = None
    image_filename = request.image_filename
    image_mime = request.image_mime_type or "image/jpeg"

    # Decode base64 image if attached
    if request.image_base64:
        try:
            b64_str = request.image_base64
            if "," in b64_str:
                header, b64_str = b64_str.split(",", 1)
                if "data:" in header and ";base64" in header:
                    extracted_mime = header.split("data:")[1].split(";base64")[0]
                    if extracted_mime:
                        image_mime = extracted_mime
            image_bytes = base64.b64decode(b64_str)
            if not image_filename:
                ext = image_mime.split("/")[-1] if "/" in image_mime else "jpg"
                image_filename = f"research_artifact.{ext}"
        except Exception as e:
            logger.warning("Failed to decode base64 image: %s", e)

    # Fetch image from URL if provided and no base64 was supplied
    elif request.image_url:
        try:
            clean_img_url = request.image_url.strip()
            if clean_img_url.startswith("/static/"):
                static_path = Path(__file__).parent / clean_img_url.lstrip("/")
                if static_path.exists():
                    image_bytes = static_path.read_bytes()
                    if static_path.suffix.lower() == ".svg":
                        image_mime = "image/svg+xml"
                    elif static_path.suffix.lower() == ".png":
                        image_mime = "image/png"
                    elif static_path.suffix.lower() in [".jpg", ".jpeg"]:
                        image_mime = "image/jpeg"
                    elif static_path.suffix.lower() == ".webp":
                        image_mime = "image/webp"
                    if not image_filename:
                        image_filename = static_path.name
                else:
                    logger.warning("Local static image path not found: %s", static_path)
            else:
                async with httpx.AsyncClient(timeout=10.0) as http_client:
                    resp = await http_client.get(clean_img_url)
                    if resp.status_code == 200:
                        image_bytes = resp.content
                        image_mime = resp.headers.get("content-type", "image/jpeg")
                        if not image_filename:
                            image_filename = clean_img_url.split("/")[-1].split("?")[0] or "web_chart.jpg"
        except Exception as e:
            logger.warning("Failed to download image from URL '%s': %s", request.image_url, e)

    # Decode PDF attachment if provided
    pdf_bytes = None
    pdf_filename = request.pdf_filename
    if request.pdf_base64:
        try:
            pdf_str = request.pdf_base64
            if "," in pdf_str:
                _, pdf_str = pdf_str.split(",", 1)
            pdf_bytes = base64.b64decode(pdf_str)
            if not pdf_filename:
                pdf_filename = "attached_research_whitepaper.pdf"
        except Exception as e:
            logger.warning("Failed to decode base64 PDF attachment: %s", e)

    logger.info(
        "Executing research inquiry (topic_len=%d, has_image=%s, has_pdf=%s, web_urls=%s)...",
        len(topic_query),
        bool(image_bytes),
        bool(pdf_bytes),
        len(request.web_urls) if request.web_urls else 0,
    )

    try:
        workflow_task = asyncio.to_thread(
            run_research_workflow,
            topic=topic_query,
            image_bytes=image_bytes,
            image_filename=image_filename,
            image_mime_type=image_mime,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename,
            web_urls=request.web_urls,
            focus_areas=request.focus_areas,
        )
        result = await asyncio.wait_for(workflow_task, timeout=config.REQUEST_TIMEOUT)

        report_content = result.get("report") or result.get("answer", "No report generated.")

        # Assemble media items (user attachment + PDF document + any grounding diagrams)
        media_items = []
        if image_bytes:
            preview_src = (
                request.image_base64
                if request.image_base64
                else f"data:{image_mime};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            )
            media_items.append({
                "type": "image",
                "role": "user_attachment",
                "title": image_filename or "Attached Research Artifact",
                "caption": "User-submitted research chart or empirical evidence artifact inspected by multimodal agent.",
                "url": preview_src,
                "mime_type": image_mime,
            })

        if pdf_bytes:
            media_items.append({
                "type": "pdf",
                "role": "user_attachment",
                "title": pdf_filename or "Attached Research PDF Document",
                "caption": f"User-submitted PDF document ingested via RAG parser ({len(pdf_bytes) // 1024} KB).",
                "url": "/static/media/multi_agent_benchmarks.svg",  # fallback preview
                "mime_type": "application/pdf",
            })

        grounding_media = result.get("media", [])
        if grounding_media:
            for gm in grounding_media:
                media_items.append({
                    "type": gm.get("type", "chart"),
                    "role": "grounding_diagram",
                    "title": gm.get("title", "Grounding Benchmark Diagram"),
                    "caption": gm.get("caption", "Verified empirical benchmark diagram from research library."),
                    "url": gm.get("url", ""),
                })

        return ResearchResponse(
            status="success",
            topic=topic_query,
            report=report_content,
            answer=report_content,
            sources=result.get("sources", []),
            agents=AGENT_NAMES,
            disclaimer=config.RESEARCH_DISCLAIMER,
            media=media_items,
        )

    except asyncio.TimeoutError:
        logger.error("Research workflow timed out after %d seconds.", config.REQUEST_TIMEOUT)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Research analysis timed out after {config.REQUEST_TIMEOUT} seconds. Please try a more specific topic.",
        )

    except Exception as exc:
        error_msg = str(exc)
        if config.GROQ_API_KEY and config.GROQ_API_KEY in error_msg:
            error_msg = error_msg.replace(config.GROQ_API_KEY, "[REDACTED]")
        if config.GEMINI_API_KEY and config.GEMINI_API_KEY in error_msg:
            error_msg = error_msg.replace(config.GEMINI_API_KEY, "[REDACTED]")

        logger.exception("Error occurred during multi-agent research analysis: %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while coordinating the research agents: {error_msg}",
        )


@app.post("/ask", summary="Backward Compatible Ask Endpoint", response_model=ResearchResponse)
async def ask_alias(request: ResearchRequest) -> ResearchResponse:
    """Alias for /research endpoint to maintain backward compatibility."""
    return await execute_research(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
