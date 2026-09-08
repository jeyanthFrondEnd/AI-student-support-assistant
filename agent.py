"""
Agent module — creates the student support agent with tools, memory, and RAG.
"""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent as create_langchain_agent

from config import OLLAMA_MODEL, OLLAMA_BASE_URL
from tools import ALL_TOOLS
from memory import ConversationMemory


# ─────────────────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a friendly Student Support Assistant for a college.

IMPORTANT:

You MUST call a tool before answering every college-related question.

Tool routing rules:

- Regulations -> search_regulations
- Syllabus -> search_syllabus
- FAQs -> search_faq
- Notices -> search_notices
- If the category is unclear -> search_all

FAQ examples:

- hostel fees
- admission fees
- hostel availability
- library timings
- scholarship
- placement questions
- college timing

For example:

User: "What are the hostel fees?"

Action: call search_faq with the query "hostel fees"

NEVER answer a college-related question from your own knowledge.

NEVER say you don't have information until the appropriate tool
has been called and returned no useful results.

After receiving the tool result:

- Answer only using the retrieved information.
- Do not invent missing information.

If the tool returns no results:

"I'm sorry, I couldn't find information about that in the college documents."

For unrelated questions, politely redirect.
"""


def create_agent(
    memory: ConversationMemory,
    session_id: str = "default"
):
    """
    Create and return a LangChain agent.
    """

    # ─────────────────────────────────────────────────────
    # LLM
    # ─────────────────────────────────────────────────────

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    # ─────────────────────────────────────────────────────
    # Create Agent
    # ─────────────────────────────────────────────────────

    agent = create_langchain_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT.format(
            conversation_summary=memory.get_summary(session_id)
        ),
    )

    return agent


def chat(
    user_input: str,
    memory: ConversationMemory,
    agent_executor,
    session_id: str = "default",
) -> str:
    """
    Process a user message through the agent with memory.
    """

    # Get conversation history
    chat_history = memory.get_history(session_id)

    # Build messages
    messages = []

    # Add previous conversation
    messages.extend(chat_history)

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_input,
    })

    # ─────────────────────────────────────────────────────
    # Run agent
    # ─────────────────────────────────────────────────────

    result = agent_executor.invoke({
        "messages": messages
    })

    # ─────────────────────────────────────────────────────
    # Check Tool Calls
    # ─────────────────────────────────────────────────────

    print("\n========== TOOL CALL DEBUG ==========")

    tool_call_found = False

    for msg in result["messages"]:

        # Check whether this message contains tool calls
        if hasattr(msg, "tool_calls") and msg.tool_calls:

            tool_call_found = True

            print("✅ TOOL CALL FOUND")
            print("Tool calls:")

            for tool_call in msg.tool_calls:
                print("  Tool name:", tool_call.get("name"))
                print("  Arguments:", tool_call.get("args"))
                print("  ID:", tool_call.get("id"))

    # if not tool_call_found:
    #     print("❌ NO TOOL CALL FOUND")

    # print("=====================================\n")

    # ─────────────────────────────────────────────────────
    # Get final response
    # ─────────────────────────────────────────────────────

    response = result["messages"][-1].content

    # Save memory
    memory.add_user_message(
        user_input,
        session_id
    )

    memory.add_ai_message(
        response,
        session_id
    )

    return response