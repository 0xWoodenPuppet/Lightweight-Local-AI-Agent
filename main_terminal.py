# main_terminal.py
# ─────────────────────────────────────────────────────────
# Terminal Chat with Agentic Orchestrator
# Connects the terminal REPL directly to orchestrator.py.
# ─────────────────────────────────────────────────────────

from orchestrator import run_pipeline


def main():
    """Run an interactive agent session in the terminal."""
    print("======================================================")
    print("  Lightweight Local AI Agent — Orchestrator REPL")
    print("  (Routes queries to python_sandbox, web_search, or none)")
    print("  Type 'quit' or 'exit' to stop.")
    print("======================================================\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        # Run the full agent pipeline
        result = run_pipeline(user_input)

        print("\n" + "=" * 50)
        print(f"🤖 Assistant:\n{result['final_answer']}")
        print("=" * 50)


if __name__ == "__main__":
    main()

