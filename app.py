# app.py
# ─────────────────────────────────────────────────────────
# Streamlit Web UI for Lightweight Local AI Agent
#
# Features:
# 1. Full Scaffolded Agent Mode (Router -> Tool -> Verification -> Answer)
# 2. Side-by-Side Comparison Mode (Raw Model vs Scaffolded System)
# 3. Transparent Inspection: Shows router decision, tool I/O, & verification
# 4. JSONL Log Viewer in sidebar
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import json
from pathlib import Path
import streamlit as st

import config
import llm
from orchestrator import run_pipeline


# Page configuration
st.set_page_config(
    page_title="Lightweight Local AI Agent",
    page_icon="🤖",
    layout="wide",
)

# Custom minimal CSS for badges and clean cards
st.markdown(
    """
    <style>
    .badge-verified {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-unverified {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-direct {
        background-color: #e0e7ff;
        color: #3730a3;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .skill-pill {
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 3px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar():
    """Sidebar with configuration status, view toggle, and transaction logs."""
    st.sidebar.title("🤖 Local AI Agent")
    st.sidebar.caption("Final-Year Project Prototype (30-40% Demo)")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ System Configuration")
    st.sidebar.markdown(f"**Brain Model:** `{config.MODEL_NAME}`")
    st.sidebar.markdown(f"**Sandbox Timeout:** `{config.SANDBOX_TIMEOUT_SECONDS}s`")
    st.sidebar.markdown("**Search Engine:** `DuckDuckGo (Keyless)`")

    st.sidebar.markdown("---")
    mode = st.sidebar.radio(
        "Select Interaction Mode:",
        ["Scaffolded Agent Mode", "Raw vs Scaffolded Comparison"],
        help=(
            "Compare how a raw 3B model performs vs the verified tool-augmented system."
        ),
    )

    if st.sidebar.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["comparisons"] = []
        st.rerun()

    # Recent activity logs preview
    st.sidebar.markdown("---")
    with st.sidebar.expander("📄 View Activity Logs (agent_log.jsonl)", expanded=False):
        log_path = Path(config.LOG_FILE)
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            st.caption(f"Total transactions logged: {len(lines)}")
            for raw_line in reversed(lines[-5:]):
                try:
                    entry = json.loads(raw_line)
                    st.code(
                        f"[{entry.get('chosen_skill')}] {entry.get('user_query')}\n"
                        f"Status: {entry.get('verification', {}).get('status', 'N/A')}",
                        language="text",
                    )
                except Exception:
                    pass
        else:
            st.caption("No log entries yet.")

    return mode


def render_scaffold_details(result: dict):
    """Render the tool execution details, reasoning, and verification status."""
    chosen_skill = result.get("chosen_skill", "none")
    skill_output = result.get("skill_output")
    verification = result.get("verification", {})

    with st.expander("🔍 System Trace & Tool Execution", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Selected Skill:** `{chosen_skill}`")
            if result.get("skill_input"):
                st.markdown("**Tool Input:**")
                st.code(result["skill_input"], language="python" if chosen_skill == "python" else "text")

        with col2:
            st.markdown("**Verification:**")
            if verification.get("verified"):
                badge_class = "badge-verified"
                icon = "✅"
            elif verification.get("status") == "direct_answer":
                badge_class = "badge-direct"
                icon = "💬"
            else:
                badge_class = "badge-unverified"
                icon = "⚠️"

            st.markdown(
                f'<span class="{badge_class}">{icon} {verification.get("status", "unknown").upper()}</span>',
                unsafe_allow_html=True,
            )
            st.caption(verification.get("reason", "No verification details."))

        if skill_output:
            st.markdown("**Raw Tool Output:**")
            st.code(skill_output, language="text")


def main():
    mode = render_sidebar()

    # Initialize state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "comparisons" not in st.session_state:
        st.session_state["comparisons"] = []

    # ─────────────────────────────────────────────────────
    # Mode 1: Scaffolded Agent Mode
    # ─────────────────────────────────────────────────────
    if mode == "Scaffolded Agent Mode":
        st.title("🤖 Lightweight Local AI Agent")
        st.markdown(
            "An autonomous local agent powered by `qwen2.5:3b`. "
            "It selects external tools (`python_sandbox`, `web_search`), runs them in isolation, "
            "and verifies outputs before presenting answers."
        )

        # Display conversation history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "result" in msg:
                    render_scaffold_details(msg["result"])

        # Chat input box
        user_query = st.chat_input("Ask a math question, request recent facts, or chat...")
        if user_query:
            # Display user message
            st.session_state["messages"].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            # Run agent pipeline
            with st.chat_message("assistant"):
                with st.spinner("Deciding skill & verifying output..."):
                    result = run_pipeline(user_query)
                st.markdown(result["final_answer"])
                render_scaffold_details(result)

            st.session_state["messages"].append(
                {"role": "assistant", "content": result["final_answer"], "result": result}
            )

    # ─────────────────────────────────────────────────────
    # Mode 2: Side-by-Side Comparison Mode
    # ─────────────────────────────────────────────────────
    else:
        st.title("⚖️ Raw Model vs Scaffolded System Comparison")
        st.markdown(
            "Demonstrates the power of the agentic scaffold. "
            "See how a **raw 3B LLM** struggles with computation or current knowledge compared to the "
            "**verified, tool-augmented scaffold**."
        )

        user_query = st.text_input(
            "Enter a test query for comparison:",
            placeholder="e.g. Calculate 245 * 892 - 144, or What is the latest Python release?",
        )

        compare_btn = st.button("🚀 Run Side-by-Side Comparison", type="primary")

        if compare_btn and user_query:
            col_raw, col_scaffold = st.columns(2)

            with col_raw:
                st.subheader("🔴 Raw Model (No Tools)")
                st.caption(f"Direct response from {config.MODEL_NAME} with no skills.")
                with st.spinner("Generating raw reply..."):
                    raw_messages = [
                        {"role": "user", "content": user_query}
                    ]
                    try:
                        raw_reply, raw_telemetry = llm.chat(raw_messages, temperature=0.7)
                    except Exception as e:
                        raw_reply = f"Error: {e}"
                st.info(raw_reply)

            with col_scaffold:
                st.subheader("🟢 Full Agent System (Scaffolded)")
                st.caption("Router + Isolated Tool Execution + Deterministic Verification")
                with st.spinner("Running scaffolded pipeline..."):
                    agent_result = run_pipeline(user_query)

                st.success(agent_result["final_answer"])
                render_scaffold_details(agent_result)

            # Store comparison in history
            st.session_state["comparisons"].append({
                "query": user_query,
                "raw": raw_reply,
                "scaffold": agent_result,
            })

        # History of comparisons
        if st.session_state["comparisons"]:
            st.markdown("---")
            st.subheader("📜 Comparison History")
            for idx, comp in enumerate(reversed(st.session_state["comparisons"]), start=1):
                with st.expander(f"Comparison: {comp['query']}"):
                    c1, c2 = st.columns(2)
                    c1.markdown("**Raw Model:**")
                    c1.write(comp["raw"])
                    c2.markdown("**Scaffolded Agent:**")
                    c2.write(comp["scaffold"]["final_answer"])
                    c2.caption(
                        f"Skill: `{comp['scaffold']['chosen_skill']}` | "
                        f"Verification: `{comp['scaffold']['verification']['status']}`"
                    )


if __name__ == "__main__":
    main()
