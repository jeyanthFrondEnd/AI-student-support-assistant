"""
Student Support Assistant — Flask Web Application
Serves the chat UI and exposes REST API routes for the AI agent.
"""

from flask import Flask, render_template, request, jsonify
from memory import ConversationMemory
from agent import create_agent, chat

# ── Flask App ─────────────────────────────────────────────
app = Flask(__name__)

# ── Shared State ──────────────────────────────────────────
# In-memory conversation store (shared across requests)
memory = ConversationMemory(max_history=20)

# Cache agent executors per session to avoid re-creating on every request
_agent_cache: dict = {}


def get_agent(session_id: str):
    """Get or create an agent executor for the given session."""
    if session_id not in _agent_cache:
        _agent_cache[session_id] = create_agent(memory, session_id)
    return _agent_cache[session_id]


# ── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Process a chat message through the AI agent.

    Request JSON:
        { "message": "...", "session_id": "..." }

    Response JSON:
        { "response": "..." }
    """
    data = request.get_json()

    if not data or not data.get("message"):
        return jsonify({"error": "Message is required."}), 400

    user_message = data["message"]
    session_id = data.get("session_id", "default")

    try:
        agent_executor = get_agent(session_id)
        response = chat(user_message, memory, agent_executor, session_id)
        return jsonify({"response": response})
    except Exception as e:
        print(f"⚠️  Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_history():
    """
    Get conversation history for a session.

    Query params:
        session_id (optional, default: "default")

    Response JSON:
        { "history": [ { "role": "...", "content": "..." }, ... ] }
    """
    session_id = request.args.get("session_id", "default")
    history = memory.get_history(session_id)

    messages = []
    for msg in history:
        role = "user" if msg.type == "human" else "assistant"
        messages.append({"role": role, "content": msg.content})

    return jsonify({"history": messages})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    """
    Clear conversation history for a session.

    Request JSON:
        { "session_id": "..." }

    Response JSON:
        { "status": "cleared" }
    """
    data = request.get_json()
    session_id = data.get("session_id", "default") if data else "default"

    memory.clear(session_id)

    # Also remove cached agent so it gets a fresh context
    _agent_cache.pop(session_id, None)

    return jsonify({"status": "cleared"})


# ── Run ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 Starting Student Support Assistant (Flask)...")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
