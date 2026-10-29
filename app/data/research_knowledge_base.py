"""Research Knowledge Base for Research Analyst Agents.

Contains curated reference documents, benchmarks, industry datasets, and technical whitepapers
used by the Research Agent to search and gather high-fidelity evidence.
"""

from typing import Any, Dict, List

SAMPLE_RESEARCH_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "id": "RES-AI-001",
        "title": "Autonomous Multi-Agent Architectures & LLM Reasoning Benchmarks (2025-2026)",
        "category": "Artificial Intelligence & Multi-Agent Systems",
        "keywords": [
            "agent", "multi-agent", "reasoning", "llm", "agno", "benchmark",
            "latency", "context window", "coordination", "hallucination", "verification"
        ],
        "summary": "Empirical evaluation of multi-agent coordination frameworks, reasoning fidelity, and verification protocols.",
        "content": (
            "1. Architectural Paradigms:\n"
            "   Recent studies demonstrate that partitioned multi-agent systems (Specialized Researcher -> "
            "   Verifier -> Synthesizer) reduce factual hallucination rates by 42% compared to monolithic single-prompt LLMs.\n"
            "2. Latency vs. Reasoning Depth:\n"
            "   Coordinate team modes (sequential pipeline with verified context handoff) achieve a 94.6% factual consistency score "
            "   on complex synthesis tasks, with an average inference time overhead of only 1.8x relative to single-turn generation.\n"
            "3. Verification & Guardrail Protocols:\n"
            "   Automated cross-examination of citations against grounding knowledge bases catches 88.3% of synthetic assertions. "
            "   Structured tool retrieval (vector + token-based relevance scoring) provides verifiable provenance for analytical conclusions."
        ),
        "author": "Global AI Systems Institute",
        "date": "2025-11-15",
        "media": {
            "type": "chart",
            "url": "/static/media/multi_agent_benchmarks.svg",
            "title": "Multi-Agent Reasoning Benchmarks vs. Monolithic LLMs",
            "caption": "Empirical comparison of factual consistency (94.6% vs 58.2%) and hallucination reduction (-42%) in coordinate agent teams.",
        },
    },
    {
        "id": "RES-ENERGY-002",
        "title": "Global Renewable Energy Transition & Grid-Scale Battery Storage (BESS) Dynamics",
        "category": "Clean Technology & Energy Transition",
        "keywords": [
            "renewable energy", "solar", "wind", "bess", "battery storage",
            "grid modernization", "lcoe", "lithium-ion", "sodium-ion", "capacity"
        ],
        "summary": "Analysis of levelized cost of electricity (LCOE), battery chemistry transitions, and grid integration challenges.",
        "content": (
            "1. Capacity Growth & Projections:\n"
            "   Global utility-scale solar and wind additions reached 510 GW in 2024, on track to surpass 750 GW annually by 2027. "
            "   Battery Energy Storage System (BESS) deployments are compounding at a 33.4% CAGR through 2030.\n"
            "2. Cost Curves & Chemistry Shifts:\n"
            "   The Levelized Cost of Electricity (LCOE) for utility solar dropped to $36/MWh, while paired solar-plus-storage "
            "   is reaching parity with peaking gas plants ($65-$80/MWh). Lithium Iron Phosphate (LFP) accounts for 82% of stationary "
            "   storage, with Sodium-ion emerging for long-duration 8+ hour energy shifting by 2027.\n"
            "3. Grid Integration & Bottlenecks:\n"
            "   Interconnection queue delays remain the primary bottleneck in North America and Western Europe, with average wait times "
            "   exceeding 4.2 years. Dynamic line rating and AI-driven curtailment prediction mitigate up to 28% of transmission congestion."
        ),
        "author": "International Clean Tech Council",
        "date": "2025-08-20",
        "media": {
            "type": "chart",
            "url": "/static/media/bess_cost_curve.svg",
            "title": "Grid-Scale Battery Storage (BESS) LCOE Parity Dynamics",
            "caption": "Trajectory of paired solar-plus-storage cost curve reaching parity with gas peaking plants ($65-$80/MWh).",
        },
    },
    {
        "id": "RES-QUANTUM-003",
        "title": "Quantum Computing Scalability, Fault Tolerance & Post-Quantum Cryptography (PQC)",
        "category": "Quantum Information Science & Cybersecurity",
        "keywords": [
            "quantum", "qubit", "fault tolerance", "error correction", "pqc",
            "cryptography", "nist", "superconducting", "trapped ion", "fips"
        ],
        "summary": "State of physical vs. logical qubits, quantum error correction thresholds, and NIST PQC migration deadlines.",
        "content": (
            "1. Physical vs. Logical Qubit Scaling:\n"
            "   Leading architectures (superconducting transmon and neutral atom systems) have demonstrated physical qubit counts "
            "   exceeding 1,000, yet surface-code logical qubits with error rates below 10^-6 remain limited to experimental demonstrations (<100 logical qubits).\n"
            "2. Cryptographic Threat Horizon:\n"
            "   Shor's algorithm capable of breaking RSA-2048 and ECC is projected to require ~4,000 noise-free logical qubits "
            "   (representing ~1M physical qubits under standard surface code assumptions), placing the critical threat horizon beyond 2032-2035.\n"
            "3. NIST Post-Quantum Standards Migration:\n"
            "   NIST finalized primary PQC standards: ML-KEM (FIPS 203 for key encapsulation), ML-DSA (FIPS 204 for signatures), and "
            "   SLH-DSA (FIPS 205). Regulatory mandates require federal agencies and critical financial infrastructure to complete "
            "   hybrid classical-quantum cryptographic migration by 2030."
        ),
        "author": "Advanced Cryptographic & Quantum Research Group",
        "date": "2025-09-30",
        "media": {
            "type": "diagram",
            "url": "/static/media/quantum_qubit_scaling.svg",
            "title": "Quantum Fault-Tolerance & NIST Post-Quantum Timeline",
            "caption": "Physical to logical qubit scaling projections and NIST FIPS 203/204/205 post-quantum migration deadlines.",
        },
    },
    {
        "id": "RES-SEMI-004",
        "title": "Semiconductor Manufacturing, 2nm GAA Nodes & Advanced Packaging (CoWoS) Dynamics",
        "category": "Semiconductor Physics & Hardware Engineering",
        "keywords": [
            "semiconductor", "chip", "packaging", "cowos", "tsmc", "gaa",
            "2nm", "hbm", "wafer", "foundry", "euv", "gpu"
        ],
        "summary": "Technological roadmap for Gate-All-Around (GAA) nanosheet transistors and 2.5D/3D advanced packaging constraints.",
        "content": (
            "1. Transistor Architecture Transition:\n"
            "   The foundry transition from FinFET to Gate-All-Around (GAA) nanosheets at the 2nm and 1.8nm nodes provides a 15% performance "
            "   gain at constant power or 25-30% power reduction. High-NA EUV lithography (0.55 NA) enters volume manufacturing for critical layers.\n"
            "2. Advanced Packaging as the AI Scaling Vector:\n"
            "   Compute scaling for AI accelerators is predominantly constrained by 2.5D substrate interposers (such as TSMC CoWoS) "
            "   and High Bandwidth Memory (HBM3e/HBM4) integration. CoWoS packaging capacity has expanded at >100% year-over-year, yet remains tight.\n"
            "3. Supply Chain Geopolitics & CapEx:\n"
            "   Global semiconductor CapEx exceeds $180B annually, distributed across fab construction initiatives in Taiwan, the US, "
            "   Japan, and Europe. Thermal dissipation limits (TDP reaching 1,000W+ per package) necessitate widespread data center transition to direct-to-chip liquid cooling."
        ),
        "author": "Global Semiconductor Industry Consortium",
        "date": "2025-10-12",
        "media": {
            "type": "diagram",
            "url": "/static/media/gaa_nanosheet_2nm.svg",
            "title": "2nm Gate-All-Around (GAA) & CoWoS Packaging Architecture",
            "caption": "Structural comparison of 3-sided FinFET vs 4-sided 360-degree GAA Nanosheet channels and CoWoS packaging interposer.",
        },
    },
    {
        "id": "RES-HEALTH-005",
        "title": "Biomedical AI, Protein Folding & Clinical Trial Success Optimization",
        "category": "Life Sciences & Computational Biology",
        "keywords": [
            "biomedical", "healthcare", "protein folding", "drug discovery", "clinical trials",
            "alphafold", "genomics", "fda", "pharmacokinetics", "biomarker"
        ],
        "summary": "Impact of generative protein design models and generative chemical screening on drug discovery pipelines.",
        "content": (
            "1. Target Identification & Structural Biology:\n"
            "   Deep learning structural models have solved over 200 million protein 3D structures, compressing the computational target "
            "   discovery phase from years to weeks. De novo generative macromolecule design models produce binders with nanomolar affinity in first-round assays.\n"
            "2. Clinical Trial Attrition Rates:\n"
            "   Historically, 88% of drug candidates fail during clinical phases (Phase I-III). AI-guided biomarker matching and synthetic "
            "   control arms have demonstrated a 24% uplift in Phase II trial success rates among early biopharma cohorts.\n"
            "3. Regulatory Guidance:\n"
            "   The FDA and EMA have established dedicated frameworks for AI/ML-enabled drug manufacturing, requiring transparent model validation "
            "   audit trails, algorithmic bias mitigation in diverse demographic cohorts, and biological explainability."
        ),
        "author": "Computational Life Sciences Foundation",
        "date": "2025-07-18",
    },
    {
        "id": "RES-FIN-006",
        "title": "Macroeconomic Trends, Enterprise AI CapEx & Venture Capital Valuation Multiples",
        "category": "Macroeconomics & Financial Markets",
        "keywords": [
            "macroeconomics", "finance", "venture capital", "capex", "saas",
            "valuation", "interest rates", "roi", "enterprise", "productivity"
        ],
        "summary": "Analysis of corporate technology budgets, hyperscaler CapEx allocation, and enterprise generative AI return on investment.",
        "content": (
            "1. Hyperscaler Infrastructure Investment:\n"
            "   Combined capital expenditures by leading cloud hyperscalers surpassed $200B in 2025, with over 60% allocated to accelerated "
            "   computing infrastructure, custom ASICs, and data center electrical substation contracts.\n"
            "2. Enterprise Software Multiples & Monetization:\n"
            "   SaaS forward revenue multiples stabilized between 6.5x and 8.0x, with markets heavily penalizing seat-based models that fail to "
            "   integrate outcome-based agentic workflows. Enterprises reporting measurable productivity gains from AI agents cited automated customer operations, code generation, and research analysis.\n"
            "3. Interest Rate & Liquidity Environment:\n"
            "   Central bank policy normalization maintained terminal discount rates near 3.5%-4.0%, reinforcing disciplined hurdle rates "
            "   for corporate IT investments and favoring fast payback cycles (<14 months)."
        ),
        "author": "Capital Markets & Technology Economic Review",
        "date": "2025-12-05",
    },
]
