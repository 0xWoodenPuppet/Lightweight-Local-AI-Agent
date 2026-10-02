# skills/python_sandbox/run.py
# ─────────────────────────────────────────────────────────
# Skill: python_sandbox
# Runs arbitrary Python code inside an isolated subprocess.
# Captures standard output and standard error with a timeout.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import subprocess
import config


def run(code: str) -> str:
    """
    Execute Python code in a separate subprocess.

    Args:
        code: String containing the Python source code to execute.

    Returns:
        A string containing stdout and/or stderr, formatted clearly.
        If a timeout occurs, returns an explanatory error message.
    """
    if not code or not code.strip():
        return "[Sandbox Error] No code provided to execute."

    # Pre-clean input in case the model wraps code in markdown code blocks ```python ... ```
    cleaned_code = code.strip()
    if cleaned_code.startswith("```"):
        lines = cleaned_code.splitlines()
        # Drop first line (``` or ```python) and last line if it is ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned_code = "\n".join(lines).strip()

    try:
        # Run code using the exact same python interpreter running this process (sys.executable)
        # Never uses shell=True for security and OS consistency across Mac and Windows
        result = subprocess.run(
            [sys.executable, "-c", cleaned_code],
            capture_output=True,
            text=True,
            timeout=config.SANDBOX_TIMEOUT_SECONDS,
        )

        output_parts: list[str] = []

        if result.stdout:
            output_parts.append(result.stdout.rstrip())
        if result.stderr:
            output_parts.append(f"[STDERR]\n{result.stderr.rstrip()}")

        if not output_parts:
            return "[Executed successfully with no output]"

        return "\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return f"[Sandbox Error] Code timed out after {config.SANDBOX_TIMEOUT_SECONDS} seconds."
    except Exception as e:
        return f"[Sandbox Error] Failed to execute code: {str(e)}"
