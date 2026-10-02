# Lightweight Local AI Agent

A small LLM (via Ollama) acts as a "brain", picks from a set of skills, and results are verified before being shown.

## Prerequisites

1. **Python 3.10+**
2. **Ollama** — install from [ollama.com](https://ollama.com)
3. Pull the model:
   ```bash
   ollama pull qwen2.5:3b
   ```

## Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running

### Step 1 — Terminal Chat (no skills)

Make sure Ollama is running (`ollama serve` in another terminal), then:

```bash
python main_terminal.py
```

Type messages and get replies. Type `quit` to exit.