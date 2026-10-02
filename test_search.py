# test_search.py
# ─────────────────────────────────────────────────────────
# Test script for Step 3: web_search (DuckDuckGo keyless)
# Runs a live query and prints the snippets retrieved.
# ─────────────────────────────────────────────────────────

from skills.web_search.run import run


def test_search():
    print("=== Testing web_search Skill (DuckDuckGo Keyless) ===\n")

    # 1. Test empty query handling
    print("1. Testing empty query handling...")
    empty_result = run("   ")
    print("Output:", empty_result)
    assert "[Search Error]" in empty_result
    print("=> Passed!\n")

    # 2. Test live search
    query = "Python programming language latest features"
    print(f"2. Testing live search for: '{query}'...")
    result = run(query)

    print("\n=== Search Results ===")
    print(result)
    print("======================\n")

    assert len(result) > 0, "No content returned"
    assert "[1]" in result, "Snippet formatting expected '[1]'"
    print("🎉 DuckDuckGo web_search test passed successfully!")


if __name__ == "__main__":
    test_search()
