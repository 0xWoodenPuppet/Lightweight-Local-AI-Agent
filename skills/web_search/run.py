# skills/web_search/run.py
# ─────────────────────────────────────────────────────────
# Skill: web_search
# Keyless web search using DuckDuckGo (duckduckgo_search).
# Returns top snippets as plain text. No API keys required.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

from ddgs import DDGS
import config


def run(query: str) -> str:
    """
    Search the web using DuckDuckGo and return plain text snippets.

    Args:
        query: Search string or keywords.

    Returns:
        Formatted plain text with top search results (title, snippet, link),
        or a descriptive error message if search fails. Never crashes.
    """
    if not query or not query.strip():
        return "[Search Error] Empty search query provided."

    cleaned_query = query.strip().strip('"').strip("'")

    try:
        results = []
        with DDGS() as ddgs:
            # Query DuckDuckGo text search
            search_gen = ddgs.text(
                cleaned_query,
                max_results=config.SEARCH_NUM_RESULTS,
            )
            if search_gen:
                results = list(search_gen)

    except Exception as e:
        return f"[Search Error] DuckDuckGo search failed: {str(e)}"

    if not results:
        return f"[Search Result] No search results found for query: '{cleaned_query}'"

    # Format snippets clearly
    formatted_snippets: list[str] = []
    for idx, item in enumerate(results[:config.SEARCH_NUM_RESULTS], start=1):
        title = item.get("title", "No Title")
        snippet = item.get("body", "No description available")
        link = item.get("href", "")
        formatted_snippets.append(
            f"[{idx}] {title}\n    {snippet}\n    Source: {link}"
        )

    return "\n\n".join(formatted_snippets)
