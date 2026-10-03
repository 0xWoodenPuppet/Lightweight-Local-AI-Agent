# Lightweight Local AI Agent (30-40% Demo Prototype)

A small local LLM (`qwen2.5:3b` running via Ollama) acts as the "brain". It selects from isolated skills, and all outputs are deterministically verified before being presented to the user.

---

## Architecture Overview

```
User Query
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Router (Ollama qwen2.5:3b)                             │
│ Output: SKILL: <python|search|none>                    │
│         <input>                                        │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ python_sandbox│   │  web_search   │   │     none      │
│ (Subprocess,  │   │  (DuckDuckGo  │   │(Direct Answer)│
│  10s Timeout) │   │   Keyless)    │   │               │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│ Synthesis: Model produces answer grounded in output    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Verification Layer (Tool-Grounded, Non-Self-Judging)   │
│ - Python: Exit code 0 & number preservation check      │
│ - Search: Grounding check against retrieved snippets   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
               Final Verified Answer + Logs
```

---

## Features

- **Decoupled Skill Registry (`registry.py`)**: Adding skills never touches core orchestrator logic.
- **Python Sandbox (`skills/python_sandbox/`)**: Executes code in an isolated subprocess with 10s timeout protection and stdout/stderr capture.
- **Web Search (`skills/web_search/`)**: Live search powered by DuckDuckGo with zero API keys required and resilient HTTP fallback.
- **Deterministic Verification (`verification.py`)**: Verifies tool output without asking the model to judge itself.
- **Full Traceability**: Every transaction logged to `agent_log.jsonl`.
- **Interactive Web UI (`server.py` + `web/`)**: Features a clean interface with real-time verification status, tool telemetry, and execution traces in a slide-out inspection drawer.

---

## Setup & Installation

### 1. Prerequisites
- **Python 3.10+** (or Python 3.9+)
- **Ollama**: [Download from ollama.com](https://ollama.com)

Pull the model:
```bash
ollama pull qwen2.5:3b
```

### 2. Virtual Environment Setup
```bash
# Create venv
python3 -m venv .venv

# Activate venv
# macOS / Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Application

### Option A: Web UI (FastAPI Server)
```bash
python server.py
```
Open `http://127.0.0.1:8000` in your browser.
- Inspect intermediate tool inputs, execution stdout, and verification badges in real-time.
- View live router and synthesis latency metrics.

### Option B: Terminal Interactive REPL
```bash
python main_terminal.py
```

### Option C: Automated Test Suites
```bash
# Test Python Sandbox
python test_sandbox.py

# Test Web Search
python test_search.py

# Test Router & Orchestrator
python test_orchestrator.py

# Test Verification Layer
python test_verification.py
```