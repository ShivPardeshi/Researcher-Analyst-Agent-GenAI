"""Streamlit Frontend for Research Analyst Agents.

Autonomous 3-Agent Investigation, Verification & Synthesis System:
- Agent 1: Research Agent (Searches and gathers information)
- Agent 2: Analysis & Verification Agent (Analyzes evidence, validates claims, and identifies insights)
- Agent 3: Report Generation Agent (Produces the final research report)
"""

import os
import sys
from pathlib import Path

# Ensure root directory is on Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from app import config
from app.agents.research_team import AGENT_NAMES, run_research_workflow
from app.data.research_knowledge_base import SAMPLE_RESEARCH_DOCUMENTS

# Page configuration
st.set_page_config(
    page_title="Research Analyst Agents — Autonomous Multi-Agent System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar: Branding, System Overview & Engine Status
with st.sidebar:
    st.title("🔬 Research Analyst")
    st.caption("Autonomous 3-Agent Investigation System")
    st.markdown(
        "<div style='font-size: 0.85rem; color: #60a5fa; font-weight: 600; line-height: 1.4; margin-top: -4px; margin-bottom: 12px;'>"
        "Multi-Agent Intelligence &bull; Agno Orchestration"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Engine Status
    st.subheader("System Status")
    is_ready = config.is_provider_configured()
    active_model = config.get_active_model_name()
    if is_ready:
        st.success(f"● Connected: {active_model}")
        st.caption(f"Provider: `{config.MODEL_PROVIDER.upper()}`")
    else:
        st.error(f"● {config.MODEL_PROVIDER.capitalize()} API Key Missing")
        if config.MODEL_PROVIDER == "google":
            st.info("Please add `GEMINI_API_KEY` to `.env` (free from [Google AI Studio](https://aistudio.google.com/apikey)).")
        else:
            st.info("Please set `GROQ_API_KEY` in `.env`.")

    st.divider()

    # The 3 Mandatory Agents
    st.subheader("Collaborating 3 Agents")
    st.markdown(
        """
        1. **Agent 1: Research Agent**  
           *Searches and gathers information across scientific, market, and technical benchmarks.*
        
        2. **Agent 2: Analysis & Verification Agent**  
           *Analyzes evidence, validates claims, filters hallucinations, and identifies strategic insights.*
        
        3. **Agent 3: Report Generation Agent**  
           *Produces the final executive, publication-grade research report.*
        """
    )

    st.divider()

    # Grounding Library
    with st.expander("📚 Grounding Knowledge Base", expanded=False):
        for doc in SAMPLE_RESEARCH_DOCUMENTS:
            st.markdown(f"**{doc['title']}**")
            st.caption(f"Category: {doc.get('category', 'General')}")
            st.caption(doc["summary"])
            st.markdown("---")


# Permanent Professional Dark Theme Stylesheet
st.markdown(
    """
    <style>
    #MainMenu { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }

    header {
        background: transparent !important;
    }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        display: flex !important;
        color: #93c5fd !important;
        z-index: 999999 !important;
    }

    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    .research-banner {
        background-color: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.25);
        color: #bfdbfe;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 0.88rem;
        margin-bottom: 20px;
    }
    .academic-tag {
        display: inline-block;
        background-color: rgba(99, 102, 241, 0.12);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .memo-card-header {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 12px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #3b82f6;
    }
    .memo-tag {
        background-color: rgba(59, 130, 246, 0.15);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.35);
        font-weight: 700;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }
    .audit-seal {
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34d399;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.84rem;
        font-weight: 600;
        margin-top: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .evidence-badge {
        background-color: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #c7d2fe;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 12px;
    }
    .disclaimer-foot {
        color: #94a3b8;
        font-size: 0.78rem;
        line-height: 1.45;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state persistence
if "topic_text" not in st.session_state:
    st.session_state.topic_text = ""
if "response_data" not in st.session_state:
    st.session_state.response_data = None
if "attached_doc_name" not in st.session_state:
    st.session_state.attached_doc_name = None

# Main Page Content
st.title("🔬 Research Analyst Multi-Agent System")
st.markdown(
    '<div class="academic-tag">Autonomous Multi-Agent Investigation &bull; 3-Agent Collaborative Pipeline</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="research-banner">'
    '<strong>Architecture:</strong> Agent 1 (Research Agent) gathers empirical literature &bull; '
    'Agent 2 (Analysis & Verification Agent) audits evidence and extracts insights &bull; '
    'Agent 3 (Report Generation Agent) synthesizes the publication-ready executive report.'
    '</div>',
    unsafe_allow_html=True,
)

# Quick preset topic buttons
st.write("**Curated Research Inquiries:**")
col1, col2 = st.columns(2)
with col1:
    if st.button("🤖 Multi-Agent LLM Benchmarks & Hallucination Mitigation", use_container_width=True):
        st.session_state.topic_text = (
            "Evaluate multi-agent coordination architectures, LLM reasoning benchmarks, and hallucination reduction vs single-prompt models."
        )
    if st.button("⚡ Grid-Scale BESS & Clean Energy Transition", use_container_width=True):
        st.session_state.topic_text = (
            "Analyze global grid-scale battery storage (BESS) dynamics, LCOE parity with gas peakers, and LFP vs Sodium-ion chemistry transitions."
        )

with col2:
    if st.button("⚛️ Post-Quantum Cryptography & NIST FIPS Roadmap", use_container_width=True):
        st.session_state.topic_text = (
            "Assess quantum computing fault-tolerance timelines, Shor's algorithm threat horizon, and NIST post-quantum cryptography (FIPS 203/204/205) migration."
        )
    if st.button("🔬 2nm GAA Transistors & CoWoS Packaging Bottlenecks", use_container_width=True):
        st.session_state.topic_text = (
            "Examine 2nm Gate-All-Around (GAA) nanosheets, TSMC CoWoS advanced packaging bottlenecks, and thermal cooling requirements in AI accelerators."
        )

st.write("")

# Query Input Form with Media Upload
with st.form("research_form"):
    user_topic = st.text_area(
        "Enter your research topic, hypothesis, or analytical question:",
        value=st.session_state.topic_text,
        height=130,
        placeholder="E.g., Evaluate state-of-the-art multi-agent LLM reasoning benchmarks, coordination latency overhead, and hallucination reduction mechanisms.",
        max_chars=2500,
    )

    # Document Image Upload
    uploaded_image = st.file_uploader(
        "📊 Upload Supporting Chart / Document / Benchmark Photo (Optional):",
        type=["png", "jpg", "jpeg", "webp"],
        help="Attach a screenshot of a benchmark graph, architecture diagram, data table, or technical whitepaper excerpt.",
    )

    if uploaded_image:
        st.caption(f"📎 Attached artifact: `{uploaded_image.name}` ({uploaded_image.size // 1024} KB)")

    btn_col1, btn_col2, _ = st.columns([1.5, 1, 4])
    with btn_col1:
        submitted = st.form_submit_button("Deploy Research Agents", type="primary", use_container_width=True)
    with btn_col2:
        cleared = st.form_submit_button("Clear", use_container_width=True)

if cleared:
    st.session_state.topic_text = ""
    st.session_state.response_data = None
    st.session_state.attached_doc_name = None
    st.rerun()

if submitted:
    cleaned_topic = user_topic.strip()
    if not cleaned_topic and not uploaded_image:
        st.error("Please enter a research topic or upload a data chart to analyze.")
    elif cleaned_topic and len(cleaned_topic) < 4 and not uploaded_image:
        st.error("Please enter a research topic with at least 4 characters.")
    elif not config.is_provider_configured():
        st.error(f"API Key for {config.MODEL_PROVIDER.upper()} is not configured. Please add your key to `.env`.")
    else:
        if not cleaned_topic and uploaded_image:
            cleaned_topic = f"Analyze the data, benchmarks, and claims in the attached image ({uploaded_image.name}) and generate a verified research report."

        st.session_state.topic_text = cleaned_topic
        st.session_state.attached_doc_name = uploaded_image.name if uploaded_image else None

        img_bytes = uploaded_image.getvalue() if uploaded_image else None
        img_name = uploaded_image.name if uploaded_image else None
        img_mime = uploaded_image.type if uploaded_image else None

        progress_placeholder = st.empty()
        with progress_placeholder.container():
            st.info("Coordinating 3 Agents: [1] Research Agent ➔ [2] Analysis & Verification Agent ➔ [3] Report Generation Agent...")

        try:
            with st.spinner("Executing multi-agent investigation, verification, and report synthesis..."):
                result = run_research_workflow(
                    cleaned_topic,
                    image_bytes=img_bytes,
                    image_filename=img_name,
                    image_mime_type=img_mime,
                )
                st.session_state.response_data = result
        except Exception as e:
            st.error(f"Error during research synthesis: {str(e)}")
        finally:
            progress_placeholder.empty()


# Display Response
if st.session_state.response_data:
    resp = st.session_state.response_data
    report_text = resp.get("report") or resp.get("answer", "")
    sources = resp.get("sources", [])

    st.write("---")

    # Research Report Card
    st.markdown(
        """
        <div class="memo-card-header">
            <div>
                <span class="memo-tag">RESEARCH INTELLIGENCE REPORT</span>
                <span style="font-size: 0.85rem; font-weight: 600; margin-left: 10px;">Executive Findings</span>
            </div>
            <div style="font-size: 0.78rem; opacity: 0.8;">
                Pipeline: Research &bull; Analysis & Verification &bull; Report Generation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.attached_doc_name:
        st.markdown(
            f'<div class="evidence-badge">📎 <strong>Analyzed Artifact:</strong> {st.session_state.attached_doc_name}</div>',
            unsafe_allow_html=True,
        )

    # Sources panel
    if sources:
        with st.expander(f"📚 Consulted Knowledge Base Sources & Benchmarks ({len(sources)})", expanded=True):
            for s in sources:
                st.markdown(f"- **{s}**")

    # Report Markdown
    st.markdown("### Executive Synthesis & Analysis")
    st.markdown(report_text)

    # Verification seal
    st.markdown(
        """
        <div class="audit-seal">
            <span>✓</span>
            <span>Audited & Verified by Analysis &amp; Verification Agent &bull; Grounded in Empirical Benchmarks</span>
        </div>
        <p class="disclaimer-foot">
            <strong>Disclaimer:</strong> Research Analyst Agents synthesizes empirical data, published literature, and 
            analytical models for strategic intelligence. Validate critical findings independently.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Download report option
    evidence_note = f"\nAttached Artifact: {st.session_state.attached_doc_name}\n" if st.session_state.attached_doc_name else ""
    st.download_button(
        label="Download Research Report (.md)",
        data=(
            f"# Executive Research Report\n\n**Topic:**\n{st.session_state.topic_text}\n"
            f"{evidence_note}\n\n{report_text}\n\n## References & Sources\n"
            + "\n".join(f"- {s}" for s in sources)
            + f"\n\n---\n*{config.RESEARCH_DISCLAIMER}*"
        ),
        file_name="executive_research_report.md",
        mime="text/markdown",
    )
