# test_verification.py
# ─────────────────────────────────────────────────────────
# Test script for Step 5: Verification Layer
# Tests unit logic for Python & Search verification (both positive
# and negative failure cases), then tests end-to-end integration.
# ─────────────────────────────────────────────────────────

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.verification import verify_python_output, verify_search_output, verify_result
from agent.orchestrator import run_pipeline


def test_verification_unit():
    print("=== Testing Verification Layer (Unit Tests) ===\n")

    # ── 1. Python Verification Tests ─────────────────────
    print("1. Python: matching number in answer...")
    v1 = verify_python_output("205686", "The answer is 205686.")
    print("   Result:", v1)
    assert v1["verified"] is True
    print("   => Passed!\n")

    print("2. Python: hallucinated number in answer (mismatch)...")
    v2 = verify_python_output("205686", "The answer is 999999.")
    print("   Result:", v2)
    assert v2["verified"] is False
    assert v2["status"] == "unverified"
    print("   => Passed! (Successfully caught hallucinated number)\n")

    print("3. Python: runtime error in stdout...")
    v3 = verify_python_output("[STDERR]\nZeroDivisionError", "Error occurred.")
    print("   Result:", v3)
    assert v3["verified"] is False
    assert v3["status"] == "runtime_error"
    print("   => Passed! (Successfully flagged runtime error)\n")

    # ── 2. Search Verification Tests ─────────────────────
    print("4. Search: answer grounded in snippets...")
    mock_snippet = (
        "[1] Python 3.14.8 Release\n"
        "    The Python Software Foundation announced the official release of Python 3.14.8."
    )
    v4 = verify_search_output(
        mock_snippet,
        "Python 3.14.8 was officially announced by the Python Software Foundation."
    )
    print("   Result:", v4)
    assert v4["verified"] is True
    print("   => Passed! (Recognized grounded claim)\n")

    print("5. Search: answer hallucinating external claims not in snippet...")
    v5 = verify_search_output(
        mock_snippet,
        "The President of France signed a treaty with Brazil on quantum computing."
    )
    print("   Result:", v5)
    assert v5["verified"] is False
    assert v5["status"] == "unverified"
    print("   => Passed! (Successfully flagged ungrounded claim)\n")

    print("6. Direct Answer: none skill...")
    v6 = verify_result("none", None, "Hello! I am ready to help.")
    print("   Result:", v6)
    assert v6["verified"] is True
    print("   => Passed!\n")


def test_verification_end_to_end():
    print("=== Testing Verification Layer (End-to-End Orchestrator) ===\n")
    query = "Calculate 125 * 8"
    print(f"Running pipeline for: '{query}'...")
    result = run_pipeline(query)

    print("\nOrchestrator Result:")
    print("  Chosen Skill:", result["chosen_skill"])
    print("  Tool Output :", result["skill_output"])
    print("  Final Answer:", result["final_answer"])
    print("  Verification:", result["verification"])

    assert result["chosen_skill"] == "python"
    assert "1000" in result["skill_output"]
    assert result["verification"]["verified"] is True
    print("\n🎉 End-to-end verification passed!")


if __name__ == "__main__":
    test_verification_unit()
    test_verification_end_to_end()
