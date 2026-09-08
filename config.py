"""
Configuration module for the Student Support Assistant.
Loads environment variables and provides centralized config.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Pinecone ──────────────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_6Dftyr_TRQYE9XVmPgmoL58hf34iHqXtMXNhaSYoYJnc3njonYn1xUzss1oUQcsvvkxF4x")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "student-assistant")

# ── Ollama ────────────────────────────────────────────────
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


# ── Embedding ─────────────────────────────────────────────
EMBEDDING_MODEL = "nomic-embed-text"  # Ollama embedding model
EMBEDDING_DIMENSION = 768             # Dimension for nomic-embed-text

# ── Document Namespaces in Pinecone ───────────────────────
NAMESPACES = {
    "regulation": "regulation",
    "syllabus": "syllabus",
    "faq": "faq",
    "notice": "notice",
}
