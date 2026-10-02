# llm.py
# ─────────────────────────────────────────────────────────
# Thin wrapper around the Ollama REST API.
# Sends messages and streams back the assistant's reply.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import requests
import config


def chat(messages: list[dict], temperature: float | None = None) -> str:
    """
    Send a list of messages to Ollama and return the assistant's reply.

    Each message is a dict with 'role' ('system' | 'user' | 'assistant')
    and 'content' (str).

    Returns the full response text as a single string.
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
    return data["message"]["content"]
