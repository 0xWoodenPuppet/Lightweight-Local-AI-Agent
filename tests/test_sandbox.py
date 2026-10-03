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

    print("🎉 All python_sandbox tests passed successfully!")


if __name__ == "__main__":
    test_sandbox()
