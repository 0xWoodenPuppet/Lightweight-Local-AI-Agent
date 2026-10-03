# orchestrator.py
# ─────────────────────────────────────────────────────────
# Orchestrator & Router
# 
# 1. Prompts the small LLM to select a skill via a rigid output format:
#      SKILL: <python|search|none> | <input for the skill>
# 2. Defensively parses the decision. Falls back to "none" on any failure.
# 3. Executes the chosen skill via registry.py.
# 4. Synthesizes a final natural language answer using the tool output.
# 5. Logs every query and intermediate step to console & JSONL.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import config
import llm
from registry import SKILL_REGISTRY, get_skill_runner, get_skills_prompt_description
from verification import verify_result


ROUTER_SYSTEM_PROMPT = """You are a smart decision-making router for an AI agent.
Your job is to examine the user query and decide if an external tool is required, or if you can answer directly.

Available skills:
{skills_description}
- none: Use when the query is general conversation, greeting, advice, or common knowledge that needs no computation or live data.

CRITICAL INSTRUCTION:
Your response MUST start with a line in this format:
SKILL: <python|search|none>

Then, starting on the NEXT line, provide the input for the skill. Do not write anything else before the SKILL line.

Examples:
User: What is 45 factorial?
SKILL: python
import math
print(math.factorial(45))

User: Who won the latest football world cup?
SKILL: search
latest football world cup winner

User: Hi, who are you?
SKILL: none
Hello! I am your AI assistant. How can I help you today?

Rules:
1. The first line must be exactly SKILL: <name>.
2. Everything after the first line is treated as the input.
3. For 'python', the input must be executable Python code that prints the result.
4. For 'search', the input must be a search query.
5. For 'none', the input must be a helpful direct answer.
"""


def build_router_prompt() -> str:
    """Build the system prompt containing currently registered skills."""
    return ROUTER_SYSTEM_PROMPT.format(
        skills_description=get_skills_prompt_description()
    )


def parse_router_response(raw_reply: str) -> tuple[str, str]:
    """
    Parse the model's rigid output:
        SKILL: <skill_name> | <input>

    Returns:
        (skill_name, skill_input)

    Defensive Fallback:
        If parsing fails, or skill name is unknown, returns ("none", fallback_text).
        Never crashes.
    """
    if not raw_reply or not raw_reply.strip():
        return "none", "I am ready to help. What would you like to know?"

    # Find the line containing "SKILL:"
    lines = raw_reply.strip().splitlines()
    skill_choice = "none"
    skill_input = raw_reply.strip()
    
    for i, line in enumerate(lines):
        if "SKILL:" in line.upper():
            # Regex to capture: SKILL: <name>
            match = re.match(r"^.*?SKILL:\s*([a-zA-Z0-9_\-]+)", line.strip(), re.IGNORECASE)
            if match:
                skill_choice = match.group(1).lower().strip()
                # The rest of the lines form the input
                skill_input = "\n".join(lines[i+1:]).strip()
            break

    # Check if the skill is known in our registry
    if skill_choice in SKILL_REGISTRY:
        return skill_choice, skill_input
    elif skill_choice == "none":
        return "none", skill_input
    else:
        # Unknown skill name -> fallback to none
        return "none", skill_input or raw_reply.strip()


def append_to_log(entry: dict) -> None:
    """Safely append an orchestration transaction to the JSONL log file."""
    try:
        log_path = Path(config.LOG_FILE)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[Logging Warning] Could not write to log file: {e}")


def run_pipeline(user_query: str) -> dict:
    """
    Execute the full end-to-end agentic pipeline for a user query.

    Returns a dict with:
        - user_query: str
        - router_raw: str
        - chosen_skill: str ("python" | "search" | "none")
        - skill_input: str
        - skill_output: str | None
        - final_answer: str
        - timestamp: str
    """
    timestamp = datetime.now().isoformat()

    print(f"\n[Agent] Received query: {user_query}")

    # ── Phase 1: Router decision ──────────────────────────────
    router_messages = [
        {"role": "system", "content": build_router_prompt()},
        {"role": "user", "content": f"User Query: {user_query}"},
    ]

    try:
        # Lower temperature for deterministic routing
        router_raw, router_telemetry = llm.chat(router_messages, temperature=0.1)
    except Exception as e:
        print(f"[Agent Error] LLM router call failed: {e}")
        return {
            "timestamp": timestamp,
            "user_query": user_query,
            "router_raw": "",
            "chosen_skill": "none",
            "skill_input": "",
            "skill_output": None,
            "final_answer": f"Error contacting model: {e}",
            "verification": {
                "verified": False,
                "status": "error",
                "reason": f"Model error: {e}",
            },
            "telemetry": {
                "router": None,
                "synthesis": None,
            },
        }

    chosen_skill, skill_input = parse_router_response(router_raw)
    print(f"[Router Choice] Skill: {chosen_skill}")
    if skill_input:
        print(f"[Skill Input]  {skill_input}")

    skill_output: str | None = None
    final_answer: str = ""

    # ── Phase 2: Tool execution (if applicable) ──────────────
    if chosen_skill == "none":
        # The model gave its direct answer in the input field
        final_answer = skill_input
    else:
        runner = get_skill_runner(chosen_skill)
        if runner:
            print(f"[Agent] Executing skill '{chosen_skill}'...")
            try:
                skill_output = runner(skill_input)
            except Exception as e:
                skill_output = f"[Execution Error] {e}"
            print(f"[Skill Output]\n{skill_output}")
            
            # ── Self-Retry Loop (CRITIC) ───────────────────────
            if chosen_skill == "python" and skill_output and ("[Sandbox Error]" in skill_output or "[STDERR]" in skill_output):
                print(f"[Agent] Detected error in Python execution. Retrying once...")
                retry_messages = router_messages + [
                    {"role": "assistant", "content": router_raw},
                    {"role": "user", "content": f"The Python code failed with this error:\n{skill_output}\n\nPlease fix the code and try again. Output MUST use the exact same SKILL format."}
                ]
                try:
                    retry_raw, retry_telemetry = llm.chat(retry_messages, temperature=0.2)
                    _, retry_input = parse_router_response(retry_raw)
                    if retry_input:
                        print(f"[Agent] Retrying with fixed code:\n{retry_input}")
                        skill_input = retry_input
                        skill_output = runner(skill_input)
                        print(f"[Skill Output (Retry)]\n{skill_output}")
                        # Update router_raw and telemetry for downstream logging
                        router_raw = retry_raw
                        router_telemetry = retry_telemetry
                except Exception as e:
                    print(f"[Agent Error] Retry failed: {e}")
            # ───────────────────────────────────────────────────
            
        else:
            skill_output = f"[Error] Skill '{chosen_skill}' runner not found."

        # ── Phase 3: Final answer synthesis ──────────────────
        synthesis_messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Use the tool execution results provided below to answer the user's question clearly and accurately. "
                    "Stay strictly grounded in the tool output. Do not make up facts."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User Query: {user_query}\n\n"
                    f"Tool Chosen: {chosen_skill}\n"
                    f"Tool Output:\n{skill_output}\n\n"
                    "Please provide the final answer to the user:"
                ),
            },
        ]

        try:
            final_answer, synthesis_telemetry = llm.chat(synthesis_messages, temperature=0.3)
        except Exception as e:
            final_answer = f"Error during answer synthesis: {e}\nRaw tool output:\n{skill_output}"

    # ── Phase 4: Deterministic Tool-Grounded Verification ────
    verification = verify_result(chosen_skill, skill_output, final_answer)
    status_icon = "✅" if verification["verified"] else "⚠️"
    print(f"[Verification] {status_icon} Status: {verification['status']} | Reason: {verification['reason']}")

    # ── Phase 5: Structured logging ──────────────────────────
    result_record = {
        "timestamp": timestamp,
        "user_query": user_query,
        "router_raw": router_raw,
        "chosen_skill": chosen_skill,
        "skill_input": skill_input,
        "skill_output": skill_output,
        "final_answer": final_answer,
        "verification": verification,
        "telemetry": {
            "router": router_telemetry if 'router_telemetry' in locals() else None,
            "synthesis": synthesis_telemetry if 'synthesis_telemetry' in locals() else None,
        }
    }

    append_to_log(result_record)
    return result_record
