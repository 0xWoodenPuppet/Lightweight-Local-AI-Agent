# skills/python_sandbox/run.py
# ─────────────────────────────────────────────────────────
# Skill: python_sandbox (Hardened & Robust)
# 
# Robustness features:
# 1. AST Static Analysis: Fast syntax validation before spawning subprocess.
# 2. Interactive Hang Prevention: Detects and blocks input() upfront.
# 3. Security Guardrails: Blocks dangerous system calls (os.system, etc.).
# 4. Auto-print Last Value: Automatically prints the final expression or
#    assigned result if no print() was called by the model.
# 5. Standard Utility Pre-import: Prepend safe utility imports (math, datetime, re, json, statistics).
# 6. Isolated Temp Directory: Runs in a scratch directory to prevent repo file pollution.
# 7. Output Truncation: Caps stdout length to prevent buffer flooding.
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from agent import config

MAX_OUTPUT_LENGTH = 4000

SAFE_AUTO_IMPORTS = (
    "import math\n"
    "import datetime\n"
    "import re\n"
    "import json\n"
    "import statistics\n"
)

DANGEROUS_MODULES = {"subprocess", "pty", "shutil", "socket", "ctypes"}
DANGEROUS_ATTRIBUTES = {
    "system", "popen", "spawn", "fork", "kill", "remove", "unlink", "rmdir"
}


def _strip_markdown(code: str) -> str:
    """Strip markdown code fence blocks if present."""
    cleaned = code.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _analyze_and_transform(code: str) -> tuple[str | None, str | None]:
    """
    Statically analyzes Python code:
    - Catches syntax errors fast.
    - Blocks input() and unsafe system calls.
    - Injects print() for the last expression/assignment if no print exists.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        error_msg = f"[Sandbox Error] Syntax error on line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f"\n  {e.text.strip()}"
        return None, error_msg

    # Guardrails check
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Block input()
            if isinstance(node.func, ast.Name) and node.func.id == "input":
                return (
                    None,
                    "[Sandbox Error] Interactive 'input()' calls are not supported. "
                    "Please hardcode test values directly into the script.",
                )
            # Block dangerous attributes (e.g. os.system, os.remove)
            if isinstance(node.func, ast.Attribute) and node.func.attr in DANGEROUS_ATTRIBUTES:
                return (
                    None,
                    f"[Sandbox Error] Security restriction: Call to '{node.func.attr}' is blocked in sandbox.",
                )

        # Block dangerous imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in DANGEROUS_MODULES:
                    return None, f"[Sandbox Error] Security restriction: Importing '{root_module}' is blocked."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0]
                if root_module in DANGEROUS_MODULES:
                    return None, f"[Sandbox Error] Security restriction: Importing from '{root_module}' is blocked."

    # Check if there is already a print statement
    has_print = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print"
        for n in ast.walk(tree)
    )

    if not has_print and tree.body:
        last_stmt = tree.body[-1]
        # Case A: Last statement is an expression (e.g. `234 * 879` or `math.factorial(5)`)
        if isinstance(last_stmt, ast.Expr):
            print_node = ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[last_stmt.value],
                    keywords=[],
                )
            )
            tree.body[-1] = print_node
            ast.fix_missing_locations(tree)
            try:
                code = ast.unparse(tree)
            except Exception:
                pass
        # Case B: Last statement is an assignment (e.g. `result = 125 * 8`)
        elif isinstance(last_stmt, ast.Assign) and len(last_stmt.targets) == 1:
            target = last_stmt.targets[0]
            if isinstance(target, ast.Name):
                print_node = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="print", ctx=ast.Load()),
                        args=[ast.Name(id=target.id, ctx=ast.Load())],
                        keywords=[],
                    )
                )
                tree.body.append(print_node)
                ast.fix_missing_locations(tree)
                try:
                    code = ast.unparse(tree)
                except Exception:
                    pass

    return code, None


def run(code: str) -> str:
    """
    Execute Python code in an isolated, monitored subprocess sandbox.
    """
    if not code or not code.strip():
        return "[Sandbox Error] No code provided to execute."

    cleaned_code = _strip_markdown(code)

    # Static analysis & transformation
    transformed_code, error = _analyze_and_transform(cleaned_code)
    if error:
        return error

    # Combine auto-imports with transformed code
    executable_code = SAFE_AUTO_IMPORTS + (transformed_code or cleaned_code)

    try:
        # Run inside a disposable temporary scratch directory
        with tempfile.TemporaryDirectory(prefix="sandbox_run_") as scratch_dir:
            result = subprocess.run(
                [sys.executable, "-c", executable_code],
                cwd=scratch_dir,
                capture_output=True,
                text=True,
                timeout=config.SANDBOX_TIMEOUT_SECONDS,
            )

        output_parts: list[str] = []

        if result.stdout:
            stdout_text = result.stdout.rstrip()
            if len(stdout_text) > MAX_OUTPUT_LENGTH:
                stdout_text = stdout_text[:MAX_OUTPUT_LENGTH] + f"\n... [Output truncated at {MAX_OUTPUT_LENGTH} characters]"
            output_parts.append(stdout_text)

        if result.stderr:
            stderr_text = result.stderr.rstrip()
            if len(stderr_text) > MAX_OUTPUT_LENGTH:
                stderr_text = stderr_text[:MAX_OUTPUT_LENGTH] + f"\n... [STDERR truncated at {MAX_OUTPUT_LENGTH} characters]"
            output_parts.append(f"[STDERR]\n{stderr_text}")

        if not output_parts:
            return "[Executed successfully with no output]"

        return "\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return f"[Sandbox Error] Code timed out after {config.SANDBOX_TIMEOUT_SECONDS} seconds."
    except Exception as e:
        return f"[Sandbox Error] Failed to execute code: {str(e)}"
