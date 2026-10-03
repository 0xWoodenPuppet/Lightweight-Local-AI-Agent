# skills/web_search/run.py
# ─────────────────────────────────────────────────────────
# Skill: web_search
# Keyless web search using DuckDuckGo.
# Includes resilient fallback to handle macOS LibreSSL / TLS hiccups.
# Returns top snippets as plain text. No API keys required.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import re
import urllib.parse
import requests
from agent import config

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


def _fallback_duckduckgo_search(query: str) -> list[dict]:
    """
    Direct HTTP fallback using standard requests to DuckDuckGo HTML endpoint.
    Used when primp/ddgs hits macOS LibreSSL protocol negotiation issues.
    """
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    data = {"q": query}
    resp = requests.post(url, data=data, headers=headers, timeout=10)
    resp.raise_for_status()

    # Extract result snippets from DuckDuckGo HTML output
    html = resp.text
    results = []

    # Simple regex parsing of duckduckgo HTML results: title, href, snippet
    pattern = re.compile(
        r'<a class="result__url"[^>]*href="(?P<url>[^"]+)"[^>]*>.*?</a>.*?'
        r'<a class="result__snippet"[^>]*href="[^"]*"[^>]*>(?P<snippet>.*?)</a>',
        re.DOTALL
    )

    for match in pattern.finditer(html):
        raw_url = match.group("url").strip()
        raw_snippet = match.group("snippet").strip()
        # Clean HTML tags like <b> from snippet
        clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
        # Unquote DDG redirect URLs if needed
        clean_url = raw_url
        if "uddg=" in clean_url:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(clean_url).query)
            clean_url = parsed.get("uddg", [clean_url])[0]

        results.append({
            "title": clean_snippet[:50] + "..." if len(clean_snippet) > 50 else clean_snippet,
            "body": clean_snippet,
            "href": clean_url
        })
        if len(results) >= config.SEARCH_NUM_RESULTS:
            break

    return results


def run(query: str) -> str:
    """
    Search the web using DuckDuckGo and return plain text snippets.

    Args:
        query: Search string or keywords.

    Returns:
        Formatted plain text with top search results (title, snippet, link),
        or a descriptive message if no results found. Never crashes.
    """
    if not query or not query.strip():
        return "[Search Error] Empty search query provided."

    cleaned_query = query.strip().strip('"').strip("'")
    results = []

    # Attempt 1: ddgs package
    if DDGS is not None:
        try:
            with DDGS() as ddgs:
                search_gen = ddgs.text(cleaned_query, max_results=config.SEARCH_NUM_RESULTS)
                if search_gen:
                    results = list(search_gen)
        except Exception:
            # Silently drop into resilient fallback
            pass

    # Attempt 2: Resilient direct HTTP fallback if Attempt 1 had TLS/socket issues
    if not results:
        try:
            results = _fallback_duckduckgo_search(cleaned_query)
        except Exception as e:
            return f"[Search Error] Search request failed: {str(e)}"

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
