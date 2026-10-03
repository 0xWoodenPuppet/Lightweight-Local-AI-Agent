# config.py
# ─────────────────────────────────────────────────────────
# Single source of truth for every configurable value.
# Change settings HERE, not scattered across the codebase.
# ─────────────────────────────────────────────────────────

# ── LLM settings ──────────────────────────────────────────
MODEL_NAME = "qwen2.5:3b"              # Ollama model tag
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama server address
LLM_TEMPERATURE = 0.7                  # Sampling temperature

# ── Python sandbox settings ──────────────────────────────
SANDBOX_TIMEOUT_SECONDS = 10           # Max runtime for user code

# ── Web search settings ──────────────────────────────────
# DuckDuckGo keyless search settings
SEARCH_NUM_RESULTS = 5                 # How many snippets to return

from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Logging settings ──────────────────────────────────────
LOG_FILE = str(BASE_DIR / "agent_log.jsonl")           # JSONL log file path
