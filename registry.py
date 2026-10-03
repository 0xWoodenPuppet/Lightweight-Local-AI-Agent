# registry.py
# ─────────────────────────────────────────────────────────
# Skill Registry
# Maps short skill identifiers to their execution functions
# and human-readable descriptions.
#
# Modularity Principle:
# Adding a new skill only requires registering it here;
# the orchestrator and core logic remain untouched.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Callable
from pathlib import Path

# Import the run functions from each skill package
import skills.python_sandbox.run as python_skill
import skills.web_search.run as search_skill


# Load descriptions from skill.md files
def _load_skill_description(skill_dir: str) -> str:
    path = Path(__file__).parent / "skills" / skill_dir / "skill.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        # Extract 'When to use:' line
        for line in text.splitlines():
            if line.startswith("When to use:"):
                return line.replace("When to use:", "").strip()
        # Fallback to description
        for line in text.splitlines():
            if line.startswith("Description:"):
                return line.replace("Description:", "").strip()
    return "No description available."

# Registry dictionary mapping:
#   skill_key -> dict with:
#     - "name": human-friendly name
#     - "description": one-line summary of what it does and when to use it
#     - "run": callable function taking (input: str) -> str
SKILL_REGISTRY: dict[str, dict] = {
    "python": {
        "name": "Python Sandbox",
        "description": _load_skill_description("python_sandbox"),
        "run": python_skill.run,
    },
    "search": {
        "name": "Web Search",
        "description": _load_skill_description("web_search"),
        "run": search_skill.run,
    },
}


def get_skill_runner(skill_name: str) -> Callable[[str], str] | None:
    """
    Look up and return the execution function for a given skill name.
    Returns None if the skill is not found in the registry.
    """
    skill_entry = SKILL_REGISTRY.get(skill_name.lower().strip())
    if skill_entry:
        return skill_entry["run"]
    return None


def get_skills_prompt_description() -> str:
    """
    Format the available skills into a clean, concise string for the LLM system prompt.
    """
    lines = []
    for key, info in SKILL_REGISTRY.items():
        lines.append(f"- {key}: {info['description']}")
    return "\n".join(lines)
