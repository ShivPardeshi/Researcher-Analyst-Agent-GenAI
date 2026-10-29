"""Configuration management for Research Analyst Agents System.

Supports both Google Gemini (recommended for fast reasoning & long context) and Groq.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if present
load_dotenv(BASE_DIR / ".env", override=True)

APP_NAME: str = "Research Analyst Agents"
APP_DESCRIPTION: str = "Autonomous 3-Agent Investigation, Verification & Synthesis System"

# Provider selection: "google" or "groq"
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()

# Default to google if GEMINI_API_KEY is provided, else fallback to groq
default_provider = "google" if GEMINI_API_KEY else "groq"
MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", default_provider).strip().lower()

GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()

HOST: str = os.getenv("HOST", "0.0.0.0").strip()
PORT: int = int(os.getenv("PORT", "8000").strip())
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "90").strip())

RESEARCH_DISCLAIMER: str = (
    "Disclaimer: Research Analyst Agents synthesizes empirical data, published literature, and "
    "analytical models for strategic and research intelligence purposes. Independent validation "
    "is recommended before mission-critical capital or operational decisions."
)

# Backward compatibility alias
LEGAL_DISCLAIMER: str = RESEARCH_DISCLAIMER


def is_provider_configured() -> bool:
    """Check if the active model provider has a valid API key configured."""
    dummy_values = {"", "your_groq_api_key_here", "your_gemini_api_key_here", "placeholder"}
    if MODEL_PROVIDER == "google":
        return bool(GEMINI_API_KEY and GEMINI_API_KEY not in dummy_values)
    return bool(GROQ_API_KEY and GROQ_API_KEY not in dummy_values)


def is_groq_configured() -> bool:
    """Backward compatibility helper for health checks."""
    return is_provider_configured()


def get_active_model_name() -> str:
    """Return the name of the currently active model."""
    if MODEL_PROVIDER == "google":
        return f"Google ({GEMINI_MODEL})"
    return f"Groq ({GROQ_MODEL})"
