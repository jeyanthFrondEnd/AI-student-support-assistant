"""
Student Support Assistant — Main Entry Point
Interactive CLI chatbot with RAG, Tools, and Memory.
"""

from memory import ConversationMemory
from agent import create_agent, chat


def print_banner():
    """Print a welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎓  STUDENT SUPPORT ASSISTANT  🎓                     ║
║                                                              ║
║   Ask me about:                                              ║
║     📋 Regulations  │  📚 Syllabus                           ║
║     ❓ FAQs         │  📢 Notices                            ║
║                                                              ║
║   Commands:                                                  ║
║     /clear   — Clear conversation history                    ║
║     /history — Show conversation history                     ║
║     /help    — Show this help message                        ║
║     /quit    — Exit the assistant                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print available commands."""
    print("""
📌 Available Commands:
  /clear   — Clear the current conversation history
  /history — Show recent conversation history
  /help    — Show available commands
  /quit    — Exit the assistant
    """)


def main():
    print_banner()

    # Initialize memory (in-variable, no database)
    memory = ConversationMemory(max_history=20)
    session_id = "default"

    # Create the agent
    print("⏳ Initializing agent...")
    agent_executor = create_agent(memory, session_id)
    print("✅ Agent ready! Ask me anything.\n")

    while True:
        try:
            user_input = input("🧑‍🎓 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye! Good luck with your studies!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.lower() == "/quit":
            print("\n👋 Goodbye! Good luck with your studies!")
            break
        elif user_input.lower() == "/clear":
            memory.clear(session_id)
            print("🗑️  Conversation history cleared.\n")
            continue
        elif user_input.lower() == "/history":
            summary = memory.get_summary(session_id)
            print(f"\n📜 Conversation History:\n{summary}\n")
            continue
        elif user_input.lower() == "/help":
            print_help()
            continue

        # Run the agent
        try:
            response = chat(user_input, memory, agent_executor, session_id)
            print(f"\n🤖 Assistant: {response}\n")
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print("   Please try again or rephrase your question.\n")


if __name__ == "__main__":
    main()