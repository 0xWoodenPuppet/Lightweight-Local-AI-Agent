# memory.py
# ─────────────────────────────────────────────────────────
# Compacted Memory System: Sliding window verbatim history
# and incremental extractive summarization
# ─────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from . import llm


def estimate_tokens(text: str) -> int:
    """Rough token estimation (~0.75 words per token or 4 chars per token)."""
    if not text:
        return 0
    words = len(text.split())
    return int(words * 1.33)


def format_messages_for_summary(messages: List[Dict[str, Any]]) -> str:
    """Format messages clearly for the extractive summarizer prompt."""
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "").strip()
        lines.append(f"{role}: {content}")
        # Include tool results if available
        if msg.get("chosen_skill") and msg.get("chosen_skill") != "none":
            skill = msg.get("chosen_skill")
            output = msg.get("skill_output")
            if output:
                lines.append(f"TOOL ({skill}) RESULT: {output.strip()}")
    return "\n".join(lines)


def summarize_chunk(existing_summary: str, messages_to_summarize: List[Dict[str, Any]]) -> str:
    """
    Call the local LLM once to merge unsummarized older messages into the running summary.
    Enforces strict extractive rules and word count limits.
    """
    formatted_chunk = format_messages_for_summary(messages_to_summarize)
    if not formatted_chunk.strip():
        return existing_summary

    prompt = (
        "You are an extractive summarizer for an AI conversation memory.\n"
        "Your task is to update the existing memory summary by merging facts from the new messages.\n\n"
        f"EXISTING SUMMARY:\n{existing_summary.strip() or '(None)'}\n\n"
        f"NEW MESSAGES TO INCORPORATE:\n{formatted_chunk}\n\n"
        "INSTRUCTIONS:\n"
        "- Be strictly extractive: bullet only facts the user stated (names, preferences, goals, decisions) "
        "and key results from tools (computed numbers, sources).\n"
        "- Never add anything not explicitly stated in the messages.\n"
        "- Cap the entire summary at about 150 words.\n"
        "- Format as concise bullet points (- fact).\n"
        "- Output ONLY the updated bullet points. Do not include any greeting or conversational filler."
    )

    try:
        updated_summary, _ = llm.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return updated_summary.strip()
    except Exception as e:
        print(f"[Memory Warning] Summarization call failed: {e}")
        return existing_summary


def process_memory(
    messages: List[Dict[str, Any]],
    current_summary: str,
    summarized_count: int
) -> Tuple[List[Dict[str, Any]], str, int]:
    """
    Process conversation history into:
      1. Last 6 messages verbatim for the active prompt window.
      2. Updated running extractive summary.
      3. Updated summarized_count index.

    Trigger condition: When unsummarized older messages exceed ~1,500 tokens
    or 12 messages, call the local model once to merge them into the summary.
    """
    total_msgs = len(messages)

    # If 6 or fewer total messages, all are verbatim and none are unsummarized older messages
    if total_msgs <= 6:
        verbatim_messages = messages
        return verbatim_messages, current_summary, summarized_count

    # The last 6 messages are always kept verbatim in the prompt
    verbatim_messages = messages[-6:]
    older_messages_boundary = total_msgs - 6

    # Unsummarized older messages lie between summarized_count and older_messages_boundary
    if older_messages_boundary > summarized_count:
        unsummarized = messages[summarized_count:older_messages_boundary]
        unsummarized_text = format_messages_for_summary(unsummarized)
        token_count = estimate_tokens(unsummarized_text)

        # Trigger check: >= 12 messages or >= 1500 tokens
        if len(unsummarized) >= 12 or token_count >= 1500:
            print(f"[Memory] Triggering incremental summarization on {len(unsummarized)} messages (~{token_count} tokens)...")
            new_summary = summarize_chunk(current_summary, unsummarized)
            new_summarized_count = older_messages_boundary
            return verbatim_messages, new_summary, new_summarized_count

    return verbatim_messages, current_summary, summarized_count
