"""
In-memory conversation memory for the Student Support Assistant.
Stores chat history per session in a Python variable (no database).
"""

from langchain_core.messages import HumanMessage, AIMessage


class ConversationMemory:
    """
    Simple in-memory conversation store.
    Each session_id maps to a list of message dicts.
    """

    def __init__(self, max_history: int = 20):
        """
        Args:
            max_history: Maximum number of message pairs to retain per session.
        """
        self._store: dict[str, list] = {}
        self.max_history = max_history

    # ── Public API ────────────────────────────────────────

    def get_history(self, session_id: str = "default") -> list:
        """Return the LangChain message list for a session."""
        return self._store.get(session_id, [])

    def add_user_message(self, content: str, session_id: str = "default"):
        """Append a user message to the session history."""
        self._ensure_session(session_id)
        self._store[session_id].append(HumanMessage(content=content))
        self._trim(session_id)

    def add_ai_message(self, content: str, session_id: str = "default"):
        """Append an AI message to the session history."""
        self._ensure_session(session_id)
        self._store[session_id].append(AIMessage(content=content))
        self._trim(session_id)

    def clear(self, session_id: str = "default"):
        """Clear the history for a specific session."""
        self._store[session_id] = []

    def clear_all(self):
        """Clear all session histories."""
        self._store.clear()

    def list_sessions(self) -> list[str]:
        """Return all active session IDs."""
        return list(self._store.keys())

    def get_summary(self, session_id: str = "default") -> str:
        """Return a formatted string of recent conversation for context."""
        history = self.get_history(session_id)
        if not history:
            return "No previous conversation."
        
        lines = []
        for msg in history[-10:]:  # Last 10 messages for summary
            role = "Student" if isinstance(msg, HumanMessage) else "Assistant"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)

    # ── Internals ─────────────────────────────────────────

    def _ensure_session(self, session_id: str):
        if session_id not in self._store:
            self._store[session_id] = []

    def _trim(self, session_id: str):
        """Keep only the last `max_history * 2` messages (pairs)."""
        max_msgs = self.max_history * 2
        if len(self._store[session_id]) > max_msgs:
            self._store[session_id] = self._store[session_id][-max_msgs:]
