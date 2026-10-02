# main_terminal.py
# ─────────────────────────────────────────────────────────
# Step 1: Minimal terminal chat with Ollama.
# A simple REPL that sends your messages to the model and
# prints the replies.  No skills, no routing — just chat.
# ─────────────────────────────────────────────────────────

import llm


def main():
    """Run a simple multi-turn chat loop in the terminal."""
    print("=== Lightweight Local AI Agent — Terminal Chat ===")
    print(f"(Type 'quit' or 'exit' to stop)\n")

    # Conversation history — keeps context across turns
    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Answer clearly and concisely."
            ),
        }
    ]

    while True:
        # ── Read user input ──────────────────────────────
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C or Ctrl+D — exit gracefully
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        # ── Send to Ollama and print the reply ───────────
        messages.append({"role": "user", "content": user_input})

        try:
            reply = llm.chat(messages)
        except ConnectionError as e:
            print(f"\n[ERROR] {e}\n")
            messages.pop()  # Remove the failed user message
            continue

        messages.append({"role": "assistant", "content": reply})
        print(f"\nAssistant: {reply}\n")


if __name__ == "__main__":
    main()
