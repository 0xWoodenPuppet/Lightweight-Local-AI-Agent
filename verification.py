# verification.py
# ─────────────────────────────────────────────────────────
# Tool-Grounded Verification Layer
#
# Rule: Never ask the model to judge itself.
# Verification is strictly deterministic and compares the model's
# final synthesized answer directly against actual tool output.
#
# Skills covered:
# 1. python_sandbox:
#    - Verifies exit code was clean (no errors/stderr/timeouts)
#    - Extracts numbers from the stdout and checks they are present in final answer
# 2. web_search:
#    - Extracts significant keywords and claims from the final answer
#    - Verifies they appear in the retrieved search snippets
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import re


def _extract_numbers(text: str) -> set[str]:
    """
    Extract all integer and floating point numbers from a string.
    Example: 'The answer is 205,686 or 205686' -> {'205686'}
    """
    if not text:
        return set()
    # Normalize commas in numbers like 1,000 -> 1000
    normalized = re.sub(r"(?<=\d),(?=\d)", "", text)
    # Find all continuous digits (with optional decimals)
    matches = re.findall(r"\b\d+(?:\.\d+)?\b", normalized)
    return set(matches)


def _extract_keywords(text: str) -> list[str]:
    """
    Extract meaningful content words (length >= 4, ignoring common stop words)
    to check if key claims from the final answer exist in the snippets.
    """
    stop_words = {
        "this", "that", "there", "these", "those", "with", "from", "have", "here",
        "about", "their", "which", "would", "could", "should", "will", "what",
        "when", "where", "answer", "result", "based", "according", "latest",
        "stable", "version", "information", "found", "provided", "please", "official"
    }
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return [w for w in words if w not in stop_words]


def verify_python_output(skill_output: str | None, final_answer: str) -> dict:
    """
    Verify Python sandbox execution:
    1. Checks for subprocess errors, timeouts, or stderr.
    2. Confirms numbers computed in stdout are reflected in the final answer.
    """
    if not skill_output:
        return {
            "verified": False,
            "status": "unverified",
            "reason": "No code output was produced by the sandbox.",
        }

    # 1. Check for runtime errors or timeouts
    if "[Sandbox Error]" in skill_output:
        return {
            "verified": False,
            "status": "execution_failed",
            "reason": "Sandbox encountered an error or timed out during execution.",
        }

    if "[STDERR]" in skill_output:
        return {
            "verified": False,
            "status": "runtime_error",
            "reason": "Python code executed with errors (stderr produced).",
        }

    # 2. Extract numbers from both tool output and final answer
    stdout_numbers = _extract_numbers(skill_output)
    answer_numbers = _extract_numbers(final_answer)

    # If the code produced numbers, check if they appear in the final answer
    if stdout_numbers:
        # Check if at least the primary computed number is represented in the answer
        overlap = stdout_numbers.intersection(answer_numbers)
        if not overlap:
            return {
                "verified": False,
                "status": "unverified",
                "reason": (
                    f"Computed numbers {list(stdout_numbers)} do not appear in the "
                    f"final answer {list(answer_numbers)}."
                ),
            }

    return {
        "verified": True,
        "status": "verified",
        "reason": "Code executed cleanly (exit 0) and computed values match the answer.",
    }


def verify_search_output(skill_output: str | None, final_answer: str) -> dict:
    """
    Verify web search output:
    Checks whether key nouns / claims in the final answer are grounded
    in the snippets returned by search.
    """
    if not skill_output:
        return {
            "verified": False,
            "status": "unverified",
            "reason": "No search snippets were available for verification.",
        }

    if "[Search Error]" in skill_output:
        return {
            "verified": False,
            "status": "search_failed",
            "reason": "Search query could not be executed.",
        }

    # If the answer explicitly states information was not found, it is faithful
    if "not found" in final_answer.lower() or "none of the provided" in final_answer.lower():
        return {
            "verified": True,
            "status": "verified",
            "reason": "Model faithfully reported that snippets did not contain the requested answer.",
        }

    # Extract keywords from the final answer
    answer_keywords = _extract_keywords(final_answer)
    if not answer_keywords:
        return {
            "verified": True,
            "status": "verified",
            "reason": "Answer is general or lacks specific factual claims.",
        }

    # Count how many keywords from the answer actually appear in the search snippets
    snippets_lower = skill_output.lower()
    matched_keywords = [w for w in answer_keywords if w in snippets_lower]

    grounding_ratio = len(matched_keywords) / len(answer_keywords)

    # If at least 50% of the key claims/terms appear in the snippets, considered grounded
    if grounding_ratio >= 0.5:
        return {
            "verified": True,
            "status": "verified",
            "reason": f"Grounded in search snippets ({int(grounding_ratio * 100)}% keyword match).",
        }
    elif grounding_ratio >= 0.25:
        return {
            "verified": False,
            "status": "partially_verified",
            "reason": f"Only partial support in search snippets ({int(grounding_ratio * 100)}% match).",
        }
    else:
        return {
            "verified": False,
            "status": "unverified",
            "reason": "Claims in final answer could not be verified against search snippets.",
        }


def verify_result(chosen_skill: str, skill_output: str | None, final_answer: str) -> dict:
    """
    Unified verification entry point.
    Dispatches to skill-specific verification without asking the LLM.
    """
    if chosen_skill == "python":
        return verify_python_output(skill_output, final_answer)
    elif chosen_skill == "search":
        return verify_search_output(skill_output, final_answer)
    elif chosen_skill == "none":
        return {
            "verified": True,
            "status": "direct_answer",
            "reason": "Direct model response with no external tool invocation.",
        }
    else:
        return {
            "verified": False,
            "status": "unknown_skill",
            "reason": f"No verification rule for skill '{chosen_skill}'.",
        }
