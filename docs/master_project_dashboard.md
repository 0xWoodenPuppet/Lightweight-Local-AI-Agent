# Master Project Dashboard: Edge AI Reliability Framework

This document comprehensively consolidates the project handoff summary and evaluation report for the B.E. Major Project investigating Edge AI Reliability. It serves as the definitive single source of truth, retaining all historical findings, architectural decisions, and future planning.

---

## Part A: Project Handoff & Architecture

### 1. Project Direction (Core Thesis & Edge AI Reliability)
This is a B.E. Major Project 1 (Mumbai University, spanning semesters 7 and 8) investigating **Edge AI Reliability**. 

The core premise is that **large models (70B–400B) have the massive parameter counts needed to absorb sloppy prompts and figure out what to do, whereas small on-device models (3B) do not.** To make a 3B model reliable on consumer hardware without cloud dependencies, you must replace missing parameter counts with **rigid software scaffolding**:
1. **Smart reasoning & offline tool routing:** Using a small, efficient local model (currently Qwen2.5 3B via Ollama) strictly for orchestrating tasks and routing requests to narrow "expert skills".
2. **Knowledge offloading:** Eliminating the knowledge-cutoff problem and model bloat by providing tools (web search / online database RAG) to dynamically fetch verified facts when needed, rather than storing all world knowledge inside model weights.
3. **Formal Thesis Statement:** *"We investigated the degradation of agentic reliability when scaling down to 3B models on consumer edge hardware, and demonstrated how deterministic scaffolding (AST sandboxing, dynamic routing, and grounded verification) closes the accuracy gap without cloud dependencies."*

**Industry Parallels:** This mirrors how frontier teams deploy edge AI:
* **Apple Intelligence:** Runs local ~3B models on iPhones using specialized adapters, rigid system routing, and local tool execution rather than open-ended reasoning.
* **Microsoft (Phi-3/4) & Google (Gemini Nano):** Rely heavily on structured output schemas and deterministic verification gates for edge tasks.

### 2. Decisions Made (Architectural Philosophy)
*   **Decoupled Cognitive Stages:** Routing $\rightarrow$ Sandboxed Execution $\rightarrow$ Synthesis $\rightarrow$ Verification are split into completely independent phases. The small model only ever has to make **one small decision at a time**, preventing context exhaustion.
*   **Deterministic Safety over LLM Guesswork:** Instead of asking the model *"Did your code execute safely?"*, Python code inspects the AST (Abstract Syntax Tree), sets OS execution timeouts, and runs deterministic grounding checks. Code handles what code is good at; the LLM only handles language.
*   **Model & Stack:** Currently Qwen2.5 3B via Ollama (planning to evaluate multiple other models). FastAPI backend with zero-dependency vanilla HTML/CSS/JS frontend.
*   **Memory & State:** Hybrid history (sliding window of 6 messages + incremental extractive summary triggered at ≥12 messages or ≥1500 tokens). Full transcripts are persisted to local SQLite (no cloud storage).
*   **Scope & Pitch:** Positioned as a research prototype demonstrating edge reliability. The upcoming demo showcases a focused loop with 2-3 skills.
*   **Documentation:** Created `PROJECT_BRIEF.md` as the single source of truth. Model fine-tuning (LoRA) is scheduled for Chapter 5 / Semester 8.

### 3. Architecture and Technical Details
*   **Model:** Ollama running local SLMs (starting with Qwen2.5 3B).
*   **Backend framework:** FastAPI (`server.py`).
*   **Pipeline:** User query $\rightarrow$ Router (rule-based prompt schema) $\rightarrow$ Defensive regex parsing $\rightarrow$ Subprocess sandbox execution $\rightarrow$ Grounded synthesis $\rightarrow$ Deterministic Verification badge.
*   **Storage:** SQLite (`agent/storage.py`), tracking conversation titles, transcripts, and a `summarized_count`.
*   **File Structure:** `agent/` (core orchestrator, memory, storage), `skills/` (sandboxed tools), `eval/` (benchmark & harness), `tests/` (unit & integration suite), `web/` (UI).

### 4. Current Implementation
*   **Exists and works:**
    * Full orchestration loop (decoupled routing, execution, synthesis, verification).
    * Python sandbox with AST security limits (`subprocess` blocked, `input()` intercepted, 5s timeout).
    * Web search (DuckDuckGo no-API integration).
    * Local SQLite persistence with full transcript and conversation management.
    * Web UI with collapsible sidebar, copy buttons, and memory inspection modal.
    * Academic evaluation benchmark of **300 curated questions** (`eval/dataset.json`) across GSM8K, SQuAD 2.0, and conversational queries.
    * Upgraded evaluation harness (`eval/eval_harness.py`) with incremental auto-saving, `--resume`, and `--limit`.
*   **Only Planned:** Expanding to multi-skill planner, document Q&A/CSV skills, and model fine-tuning (LoRA).

### 5. Ideas Considered and Rejected
*   **Frameworks & Platforms:** Repackaging Claude.ai, attaching Claude skills directly to the local model, or using heavy cloud frameworks like LangChain/CrewAI (which cause context bloat and freeze on 3B models).
*   **Features & Bloat:** Multi-turn routing, full-transcript prompt injection, routing trace, confidence flags, fallback chains, and repair demos were dropped to avoid feature bloat and context exhaustion.
*   **Deployment Tools:** Tauri was dropped because development is on a Mac Mini M2 8GB while the presentation is on a Windows laptop, leaving no time for cross-platform debugging. SerpAPI was dropped due to query limits and replaced with DuckDuckGo.

### 6. Engineering Trade-offs & Limitations (Upfront Technical Honesty)
To demonstrate honest engineering rigor to the panel, the following trade-offs are explicitly acknowledged:
*   **Single-Step vs. Multi-Step Execution:** The current system routes to one skill per turn. It does not yet perform multi-hop autonomous planning (e.g., *"Search the web, extract 3 numbers, then run Python on them in one flow"*). This is the primary subject for Chapter 5 / Future Scope.
*   **Sandbox Isolation Level:** The current Python sandbox uses AST analysis and subprocess timeouts. While effective against basic misuse, it is not a true OS-level hypervisor or containerized sandbox (like Docker or gVisor).
*   **Team / Authorship Framing:** Built solo, but presented under the team umbrella for academic requirements. 

### 7. Feedback or Constraints from the Panel or Teammates
*   **Panel Feedback:** The panel initially questioned the uniqueness (*"ChatGPT already does this"*) and demanded a working demo showing ~60% implementation. The response is framing the project around **Edge AI Reliability** and benchmarking 3B on-device models against raw baselines.
*   **Team Dynamics:** A teammate promised a complex demo (WhatsApp, LLM, schedule reading) but delivered a basic file-listing script, leaving you working alone.
*   **Hardware/Time constraints:** Must run entirely on a standard consumer laptop (no high-end discrete GPU). Demo is due on Monday, with the formal report to follow.

### 8. Contradictions or Gaps Identified
*   **Hallucination as the pitch:** Pitching that "it removes the need for reasoning" is stronger than the evidence; skills reduce reasoning load, but the model still needs to make a single reasoning decision to route correctly. That single routing decision can be optimized via LoRA fine-tuning later.

---

## Part B: Evaluation & Market Analysis

### 9. Verdict (Three Sentences)
The backend plumbing is competent: a working router, two isolated skills, defensive parsing, and a deterministic verification layer that correctly avoids LLM self-judgment. But initially, the project had **zero quantitative evidence** for its central research claim, meaning the thesis was an untested hypothesis. By building an automated evaluation harness and shifting from Streamlit to a custom UI, the project pivots from a theoretical toy to an empirically validated framework capable of surviving a demo.

### 10. Uses
**Who would realistically use this, and for what:**
* A CS student or hobbyist who wants to understand how agentic AI works by reading ~600 lines of explicit Python. The code *is* genuinely readable and explainable.
* Someone who wants local, private math computation or quick web lookups without a cloud subscription.
* **Not yet** a power user replacing GPT4All or AnythingLLM—the system lacks an MCP/plugin ecosystem.
**Honest assessment:** The real "user" right now is the evaluator panel. The system's value is pedagogical and demonstrative.

### 11. Market Comparison
| Tool | Local? | Tool Use | Verification Layer | Skills/Plugins | UI Quality | Open Source |
|---|---|---|---|---|---|---|
| **GPT4All** | Yes, CPU-first | LocalDocs RAG, JS interpreter | None | Limited | Polished Qt desktop app | Yes |
| **AnythingLLM** | Yes | "Intelligent Tool Selection", RAG | None | Workspace agents, web scraping | Professional web UI | Yes |
| **Jan** | Yes, Hybrid | MCP-native, Jupyter, browser | None | MCP ecosystem (growing) | Clean desktop app | Yes |
| **Open Interpreter** | Yes | Sandboxed shell/code execution | None (approval-based safety) | Provider-agnostic, filesystem | Terminal-first | Yes |
| **Goose (AAIF)** | Yes | 70+ MCP extensions, parallel subagents | None | MCP-native, extensible | Web + CLI | Yes |
| **This project** | Yes | 2 skills (Python, Search) | **Yes: Deterministic, tool-grounded** | 2 skills, manual registry | Custom Vanilla Web App | Yes |

**Where differentiated:** The verification layer. None of the mature competitors have a deterministic, tool-grounded verification step that compares the model's claims against actual tool output before showing the answer. They rely on sandboxing and human approval instead.
**Where not differentiated:** Everything else. Two skills vs. 70+ MCP extensions. No plugin ecosystem.

### 12. Architectural Precedent: Deterministic AI and Jev AI
A major recent validation of this project's core hypothesis is the emergence of **Jev AI** (developed by TypeSafe AI, late 2026) and the broader shift toward **Deterministic AI Architectures**:
* **The "System 1" Decision Paradigm:** Jev departs from monolithic autoregressive generation by acting strictly as a fast, typed "System 1" decision engine. It evaluates input state against schema-bound questions and returns structured decisions rather than free-form prose.
* **Separation of Judgment from Execution:** Jev formalizes the principle that AI models are probabilistic judgment engines—they should classify intent, route workflows, and extract parameters, but **never execute arithmetic, state machines, or security controls in model weights**. All execution, mathematical calculation, and safety validation must remain in deterministic software code.
* **Direct Relevance to Our Thesis:** Our edge reliability framework implements this exact principle for Small Language Models (3B). Instead of relying on a 3B model to perform multi-step arithmetic mentally (which fails due to limited parameter capacity), the 3B model is constrained to typed routing, while the AST-sandboxed Python runtime and DuckDuckGo engine handle deterministic execution and factual grounding.

**The honest pitch:** "We are not competing on breadth or UX. Our contribution is demonstrating how deterministic scaffolding (inspired by the emerging Jev-style separation of judgment and execution) enables lightweight 3B models to achieve reliable performance on consumer edge hardware."

### 13. Research Paper Viability
**Current state: Not publishable at top-tier venues.** The paper would be rejected at venues like ACL/NeurIPS because it lacks massive benchmark scale across multi-hop tasks.
**Realistic venue:** If numbers are compelling, a workshop paper at a local/national conference.
**Your instinct is correct:** this is more of an engineering project with an empirical evaluation than a novel research contribution. That's fine for a B.E. project. The contribution is the **data**, not the technique. Own that framing.

### 14. Product/SaaS Viability
**Blunt assessment: No viable standalone product or SaaS here.**
The feature set (2 skills, keyword verification) is a subset of what competitors ship for free. "Verification layer" as a feature is real value, but it's a feature, not a product. The smallest viable slice for productization would be a verification plugin for an existing platform (e.g., an MCP server that other agents call to verify their outputs).

### 15. The "HQ" Vision (B.6)
**Verdict: Scope creep that dilutes the verification thesis.**
The "HQ" vision (local hub that sits in front of all your apps, files, notes, and other AI tools) is essentially describing what Goose, Jan, and macOS/Windows Copilot are already building with massive engineering teams. Claiming this vision in a B.E. project with 2 skills and a web UI will invite skepticism, not admiration. The smallest credible slice right now is focusing entirely on the verification layer. The "HQ" vision belongs in a Future Work slide, explicitly labelled as aspirational.

### 16. Answers to Inline Questions in the Document
* **"scaffolding sounds weak"**: Use **"orchestration framework"** or **"agentic scaffold"**. In the literature, "scaffold" is the accepted term (CRITIC, VerifiAgent, and the NVIDIA position paper all use it). Don't fight the terminology; own it.
* **"can we do something better here?" (one-line summary)**: *"A verification-first orchestration layer that lets a 3B-parameter local model match cloud-scale accuracy on tool-use tasks—fully offline, private, and free."*
* **"verify this claim...is the market moving towards local LLMs?"**: Yes. The NVIDIA "SLMs are the Future of Agentic AI" paper (2025), the Goose/AAIF foundation launch, Jan's hybrid architecture, and Apple/Google's on-device model pushes all confirm this trend. The claim is defensible.
* **"i feel this is not a research paper...no novelty here"**: Your instinct is correct for top-tier venues. But for a B.E. project, empirical validation of an existing technique on a new setting (small local models) is entirely appropriate. The contribution is the **data**, not the technique. Own that framing.

---

## Part C: Actionable Findings & Planning

### 17. Where It Is Lacking (Code-Level Issues)
*(Note: Many of these were identified in the preliminary report and have since been addressed or triaged)*

| File | Issue | Severity |
|---|---|---|
| `verification.py` L37–49 | **Search verification is a weak keyword-overlap heuristic.** `_extract_keywords` removes words under 4 chars and a small stop-word set. The 50% threshold is arbitrary and untested. | High |
| `verification.py` L80–96 | **Python verification only checks number presence, not semantic correctness.** If stdout prints `1000` and the model says "The answer is 1000 but I think it should be 999", verification passes. | Medium |
| `orchestrator.py` L120–227 | **No conversation memory.** Each call to `run_pipeline()` is stateless. *(Note: Since fixed by Hybrid Memory system)* | Medium |
| `orchestrator.py` L26–55 | **Router prompt has no negative examples.** The few-shot examples are all happy-path. A small 3B model needs to see what *not* to do. | Medium |
| `orchestrator.py` L163 | `skill_output: str | None = None` uses Python 3.10+ union syntax without `from __future__ import annotations`. **Docstring is stale.** | Low |
| `skills/python_sandbox/run.py` | **No blocked imports.** The sandbox can run `import os; os.system('rm -rf /')`. *(Note: Since fixed by AST Sandbox)* | High |
| `app.py` | **No latency/token metrics displayed.** The Ollama API returns `eval_count`, `eval_duration` but the UI discards them. | Medium |
| `registry.py` | **Progressive disclosure is claimed but not implemented.** `skill.md` files exist but are never read by the orchestrator. | Low |

### 18. Improvements to Current Implementation
**Must-fix (code correctness):**
1. Make `llm.py` return the full Ollama response dict.
2. Add conversation history to `run_pipeline()`. *(Done)*
3. Fix the stale docstring in `orchestrator.py`.

**Should-fix (verification quality):**
4. Search verification: check that **specific named entities and numbers** from the answer appear in the snippets, not just generic 4+ letter words.
5. Python verification: check that the model's answer doesn't **contradict** the stdout.

**Nice-to-fix (demo polish):**
6. Show verification status prominently (above the answer, not hidden in an expander). *(Done)*
7. Display latency and token metrics from Ollama.

### 19. Candidate Features Assessment (B.5)
| Feature | Verdict | Rationale |
|---|---|---|
| **Self-debugging sandbox** (run, read error, fix, retry) | **Build now** | Directly strengthens the verification thesis. Shows the scaffold *acting* on verification failure. High demo impact. |
| **Artifact window** (side panel for generated code) | **Build now** | Makes the system feel like a real tool, not a chat toy. |
| **Model auto-switching** | **Defer** | Interesting but needs benchmarking infrastructure that doesn't exist yet. |
| **Interview mode** | **Defer** | Cool UX idea but orthogonal to the verification thesis. |
| **Word doc skill** | **Defer** | Adds breadth, not depth. Doesn't test verification. |
| **Voice mode** | **Drop** | Scope creep. No research value. |
| **Drag-and-drop file input** | **Defer** | Nice UX but needs a file-processing skill that doesn't exist. |
| **Local files / PKM / Zettelkasten** | **Drop for now** | This is a different product (NotebookLM competitor). |
| **NotebookLM-style notebooks** | **Drop** | Same: different product. |
| **Software engineer skill** | **Defer** | Ambitious. Needs robust sandbox, file I/O, and multi-step planning that a 3B model will struggle with. |

### 20. Top 5 Things to Do in 2 Days (Ranked)
| Rank | Task | Effort | Impact | Rationale |
|---|---|---|---|---|
| **1** | **Build a 30-question evaluation harness** with ground-truth answers. Run raw vs. scaffolded on `qwen2.5:3b`. | ~2–3h | **Critical** | *(Note: Completed with 300 questions)* Without this, the project has no evidence for its thesis. |
| **2** | **Replace Streamlit with a polished FastAPI + HTML/CSS/JS frontend.** Three-pane layout. | ~3–4h | **High** | *(Note: Completed)* The UI is the first thing evaluators see. |
| **3** | **Add self-retry on Python sandbox failure.** When verification detects error, let model try once more. | ~1h | **High** | Directly demonstrates the CRITIC loop actually working. |
| **4** | **Run the evaluation on a second model** (`qwen3:1.7b` or `phi4-mini:3.8b`). | ~1h | **Medium** | Extends thesis to the 1–4B range. |
| **5** | **Add 1–2 more skills** (e.g., `datetime` or `file_reader`). | ~1–2h | **Medium** | Shows the registry architecture actually scales. |

### 21. Comprehensive Future Scope & What to Label as Future Work
Explicitly label these in slides/docs as **"Future Work / Next Phase"**:
* **Multi-Step Autonomous Planning (DAGs):** Expanding from single-turn routing to chained multi-skill execution.
* **Model Fine-Tuning (LoRA):** Training a dedicated low-rank adapter on routing schemas to push routing precision toward 99%.
* **Hybrid Local/Cloud Backend Dispatch (Online API Key Option):** An architecture for seamlessly switching the inference engine between local SLMs (via Ollama on-device) and frontier cloud models (OpenAI `gpt-4o-mini`, Anthropic `claude-3-5-haiku`, or Google Gemini) when the user inputs an API key. In the UI, the status pill dynamically reflects data sovereignty:
    - *Local Mode (Default):* Displays `🟢 Running locally | Qwen2.5 3B | private` (zero data leaves the edge).
    - *Online API Mode:* Displays `🌐 Cloud API | gpt-4o-mini | online` with an indicator of cloud transmission.
* **Containerized Sandbox:** Upgrading from Python AST limits to gVisor or Docker sandboxing.
* **Model & Quantization Benchmarks:** Comparing Qwen2.5 3B against Llama-3.2 3B and Phi-3.5 across 4-bit and 8-bit quantizations.
* **Online Database Integration (RAG):** Connecting the reasoning agent to verified external knowledge bases to eliminate cutoff completely.
* Vector-based skill search (FAISS/Chroma)
* Skill Builder meta-skill
* Desktop app (Tauri)
* Memory / knowledge graph
* Obsidian integration
* Background tasks / proactive suggestions
* GSM8K / MMLU formal benchmarking
