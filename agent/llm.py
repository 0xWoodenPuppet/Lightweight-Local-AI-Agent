# llm.py
# ─────────────────────────────────────────────────────────
# Thin wrapper around the Ollama REST API.
# Sends messages and streams back the assistant's reply.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import requests
from . import config


def chat(messages: list[dict], temperature: float | None = None) -> tuple[str, dict]:
    """
    Send a list of messages to Ollama and return the assistant's reply.

    Each message is a dict with 'role' ('system' | 'user' | 'assistant')
    and 'content' (str).

    Returns a tuple of (response_text, telemetry_dict).
    Raises an exception if the Ollama server is unreachable or errors out.
    """
    url = f"{config.OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "stream": False,                     # Get the full reply in one shot
        "options": {
            "temperature": temperature if temperature is not None else config.LLM_TEMPERATURE,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
    except requests.ConnectionError:
        raise ConnectionError(
            f"Cannot reach Ollama at {config.OLLAMA_BASE_URL}. "
            "Is the server running?  Start it with:  ollama serve"
        )

    data = response.json()
    telemetry = {
        "eval_count": data.get("eval_count", 0),
        "eval_duration": data.get("eval_duration", 0),
        "total_duration": data.get("total_duration", 0),
    }
    return data["message"]["content"], telemetry
