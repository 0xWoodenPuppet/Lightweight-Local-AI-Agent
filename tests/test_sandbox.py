# test_sandbox.py
# ─────────────────────────────────────────────────────────
# Test script for Step 2: python_sandbox
# Runs hand-written test cases to verify normal execution,
# error capturing, and timeout protection.
# ─────────────────────────────────────────────────────────

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skills.python_sandbox.run import run


def test_sandbox():
    print("=== Testing python_sandbox Skill ===\n")

    # 1. Normal execution with math and print
    print("1. Testing normal code execution (math calculation)...")
    code_1 = """
def factorial(n):
    return 1 if n <= 1 else n * factorial(n - 1)

print(f"5! = {factorial(5)}")
"""
    result_1 = run(code_1)
    print("Output:\n", result_1)
    assert "5! = 120" in result_1, "Failed normal calculation test"
    print("=> Passed!\n")

    # 2. Syntax/Runtime error capture
    print("2. Testing error capture (ZeroDivisionError)...")
    code_2 = "print(10 / 0)"
    result_2 = run(code_2)
    print("Output:\n", result_2)
    assert "[STDERR]" in result_2 and "ZeroDivisionError" in result_2, "Failed error capture test"
    print("=> Passed!\n")

    # 3. Code with markdown formatting
    print("3. Testing code with markdown ticks (```python)...")
    code_3 = "```python\nprint('Hello from inside markdown blocks!')\n```"
    result_3 = run(code_3)
    print("Output:\n", result_3)
    assert "Hello from inside markdown blocks!" in result_3, "Failed markdown stripping test"
    print("=> Passed!\n")

    # 4. Timeout test (infinite loop)
    print("4. Testing timeout protection (infinite loop)... (will wait up to timeout seconds)")
    code_4 = """
import time
while True:
    time.sleep(0.5)
"""
    result_4 = run(code_4)
    print("Output:\n", result_4)
    assert "timed out" in result_4.lower(), "Failed timeout test"
    print("=> Passed!\n")

    # 5. Auto-print test (unprinted expression & assignment)
    print("5. Testing auto-print on bare expression and unprinted assignment...")
    code_5a = "125 * 8"
    result_5a = run(code_5a)
    print("Output 5a:", result_5a)
    assert "1000" in result_5a, "Failed auto-print on expression"

    code_5b = "computed_val = 50 * 4"
    result_5b = run(code_5b)
    print("Output 5b:", result_5b)
    assert "200" in result_5b, "Failed auto-print on assignment"
    print("=> Passed!\n")

    # 6. Interactive input() blocking
    print("6. Testing interactive input() blocking...")
    code_6 = "name = input('Enter name: ')\nprint(name)"
    result_6 = run(code_6)
    print("Output:\n", result_6)
    assert "interactive" in result_6.lower() or "input()" in result_6, "Failed input() block test"
    print("=> Passed!\n")

    # 7. Security guardrail blocking dangerous modules
    print("7. Testing security guardrail blocking dangerous import...")
    code_7 = "import subprocess\nsubprocess.run(['ls'])"
    result_7 = run(code_7)
    print("Output:\n", result_7)
    assert "security restriction" in result_7.lower() or "blocked" in result_7.lower(), "Failed security guardrail test"
    print("=> Passed!\n")

    # 8. Auto-imports test
    print("8. Testing safe auto-imports (math without explicit import)...")
    code_8 = "math.sqrt(144)"
    result_8 = run(code_8)
    print("Output:\n", result_8)
    assert "12" in result_8, "Failed auto-imports test"
    print("=> Passed!\n")

    print("🎉 All 8 python_sandbox tests passed successfully!")


if __name__ == "__main__":
    test_sandbox()

