"""
Tools module — defines LangChain tools the agent can invoke.
Each tool searches a specific Pinecone namespace (regulation, syllabus, faq, notice).
"""

from langchain_core.tools import tool
from vectorstore import search_documents
from config import NAMESPACES


@tool
def search_regulation(query: str) -> str:
    """
    Search college regulation documents. Use this when the student asks about
    academic rules, attendance policies, exam regulations, grading systems,
    conduct policies, credit requirements, or any official college regulation.
    """
    results = search_documents(query, namespace=NAMESPACES["regulation"], top_k=4)
    if not results:
        return "No relevant regulation documents found."
    
    output = "📋 **Regulation Documents Found:**\n\n"
    for i, doc in enumerate(results, 1):
        source = doc["metadata"].get("source", "Unknown")
        output += f"**[{i}]** (Source: {source})\n{doc['content']}\n\n"
    print('output',output)
    return output


@tool
def search_syllabus(query: str) -> str:
    """
    Search syllabus documents. Use this when the student asks about
    course content, subjects, semester curriculum, course outcomes,
    textbooks, reference materials, or academic syllabus details.
    """
    results = search_documents(query, namespace=NAMESPACES["syllabus"], top_k=4)
    if not results:
        return "No relevant syllabus documents found."
    
    output = "📚 **Syllabus Documents Found:**\n\n"
    for i, doc in enumerate(results, 1):
        source = doc["metadata"].get("source", "Unknown")
        output += f"**[{i}]** (Source: {source})\n{doc['content']}\n\n"
    return output


@tool
def search_faq(query: str) -> str:
    """
    Search frequently asked questions. Use this when the student asks
    common questions about admissions, fees, hostel, library, placements,
    scholarships, exam schedules, or general college information.
    """
    results = search_documents(query, namespace=NAMESPACES["faq"], top_k=4)
    if not results:
        return "No relevant FAQ entries found."
    
    output = "❓ **FAQ Entries Found:**\n\n"
    for i, doc in enumerate(results, 1):
        source = doc["metadata"].get("source", "Unknown")
        output += f"**[{i}]** (Source: {source})\n{doc['content']}\n\n"
    return output


@tool
def search_notice(query: str) -> str:
    """
    Search college notice board / announcements. Use this when the student asks
    about recent announcements, exam dates, holiday schedules, event notices,
    deadlines, or any official college notifications.
    """
    results = search_documents(query, namespace=NAMESPACES["notice"], top_k=4)
    if not results:
        return "No relevant notices found."
    
    output = "📢 **Notices Found:**\n\n"
    for i, doc in enumerate(results, 1):
        source = doc["metadata"].get("source", "Unknown")
        output += f"**[{i}]** (Source: {source})\n{doc['content']}\n\n"
    return output


@tool
def search_all(query: str) -> str:
    """
    Search across ALL document categories (regulation, syllabus, FAQ, notices).
    Use this when the student's question is general or could span multiple categories.
    """
    all_results = []
    for category, namespace in NAMESPACES.items():
        results = search_documents(query, namespace=namespace, top_k=2)
        for doc in results:
            doc["category"] = category
            all_results.append(doc)

    if not all_results:
        return "No relevant documents found across any category."

    output = "🔍 **Search Results (All Categories):**\n\n"
    for i, doc in enumerate(all_results, 1):
        source = doc["metadata"].get("source", "Unknown")
        category = doc["category"].upper()
        output += f"**[{i}] [{category}]** (Source: {source})\n{doc['content']}\n\n"
    return output


# Collect all tools for the agent
ALL_TOOLS = [
    search_regulation,
    search_syllabus,
    search_faq,
    search_notice,
    search_all,
]
