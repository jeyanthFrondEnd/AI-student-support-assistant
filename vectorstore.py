"""
Vector Store module — handles Pinecone index creation, embedding, and retrieval.
Uses Ollama's nomic-embed-text for embeddings and Pinecone as the vector DB.
"""

from langchain_ollama import OllamaEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    OLLAMA_BASE_URL,
)


def get_embeddings() -> OllamaEmbeddings:
    """Return the Ollama embedding model instance."""
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def init_pinecone_index():
    """
    Initialize the Pinecone client and ensure the index exists.
    Returns the Pinecone Index object.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create the index if it doesn't exist
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"✅ Created Pinecone index: {PINECONE_INDEX_NAME}")
    else:
        print(f"📌 Using existing Pinecone index: {PINECONE_INDEX_NAME}")

    return pc.Index(PINECONE_INDEX_NAME)


def get_vectorstore(namespace: str = "default") -> PineconeVectorStore:
    """
    Return a LangChain PineconeVectorStore for the given namespace.
    Namespaces separate regulation, syllabus, faq, notice documents.
    """
    embeddings = get_embeddings()
    return PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        namespace=namespace,
        pinecone_api_key=PINECONE_API_KEY,
    )


def search_documents(query: str, namespace: str, top_k: int = 4) -> list[dict]:
    """
    Search for relevant documents in the specified Pinecone namespace.
    Returns a list of dicts with 'content' and 'metadata' keys.
    """
    vectorstore = get_vectorstore(namespace)
    results = vectorstore.similarity_search(query, k=top_k)
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in results
    ]
