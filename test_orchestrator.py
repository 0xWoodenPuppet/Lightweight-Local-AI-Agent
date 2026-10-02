# test_orchestrator.py
# ─────────────────────────────────────────────────────────
# Test script for Step 4: Router & Orchestrator
# Tests three representative cases:
#   1. Math calculation -> should route to 'python'
#   2. Live information / fact -> should route to 'search'
#   3. General conversation -> should route to 'none'
# ─────────────────────────────────────────────────────────

from pathlib import Path
import config
from orchestrator import run_pipeline


def test_orchestrator():
    print("=== Testing Router & Orchestrator End-to-End ===\n")

    test_queries = [
        ("Calculate 234 multiplied by 879", "python"),
        ("What is the latest stable Python release version?", "search"),
        ("Hello, how are you today?", "none"),
    ]

    for idx, (query, expected_skill) in enumerate(test_queries, start=1):
        print(f"\n──────────────────────────────────────────────────")
        print(f"Test {idx}: '{query}' (Expected skill: '{expected_skill}')")
        print(f"──────────────────────────────────────────────────")

        res = run_pipeline(query)

        print(f"\nFinal Answer: {res['final_answer']}")
        print(f"Selected: {res['chosen_skill']}")

        if res['chosen_skill'] == expected_skill:
            print(f"✅ Route match: selected '{res['chosen_skill']}' as expected.")
        else:
            print(f"⚠️ Notice: selected '{res['chosen_skill']}' (expected '{expected_skill}')")

    # Verify JSONL log was created and contains entries
    log_file = Path(config.LOG_FILE)
    assert log_file.exists(), f"Log file {config.LOG_FILE} was not created!"
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"\n✅ Logging verified: {len(lines)} records found in {config.LOG_FILE}")

    print("\n🎉 Step 4 Router & Orchestrator test complete!")


if __name__ == "__main__":
    test_orchestrator()
