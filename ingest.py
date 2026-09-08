"""
Document ingestion script — loads text/PDF files into Pinecone by namespace.

Usage:
    python ingest.py --source ./data/regulations --namespace regulation
    python ingest.py --source ./data/syllabus    --namespace syllabus
    python ingest.py --source ./data/faqs         --namespace faq
    python ingest.py --source ./data/notices      --namespace notice

Supported formats: .txt, .pdf, .md
"""

import argparse
import os
import sys

from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from vectorstore import get_vectorstore, init_pinecone_index
from config import NAMESPACES


# ── Loader map by extension ──────────────────────────────

LOADER_MAP = {
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".md":  UnstructuredMarkdownLoader,
}


def load_documents(source_path: str):
    """Load documents from a file or directory."""
    if os.path.isfile(source_path):
        ext = os.path.splitext(source_path)[1].lower()
        loader_cls = LOADER_MAP.get(ext)
        if not loader_cls:
            print(f"❌ Unsupported file type: {ext}")
            sys.exit(1)
        loader = loader_cls(source_path)
        return loader.load()

    all_docs = []
    for ext, loader_cls in LOADER_MAP.items():
        try:
            dir_loader = DirectoryLoader(
                source_path,
                glob=f"**/*{ext}",
                loader_cls=loader_cls,  # type: ignore
                show_progress=True,
                use_multithreading=True,
            )
            docs = dir_loader.load()
            all_docs.extend(docs)
            print(f"  📄 Loaded {len(docs)} {ext} file(s)")
        except Exception as e:
            print(f"  ⚠️  Error loading {ext} files: {e}")

    return all_docs


def split_documents(documents, chunk_size=800, chunk_overlap=200):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest(source_path: str, namespace: str):
    """Main ingestion pipeline."""
    print(f"\n{'='*60}")
    print(f"🚀 Ingesting documents into namespace: {namespace}")
    print(f"   Source: {source_path}")
    print(f"{'='*60}\n")

    # 1. Initialize Pinecone index
    init_pinecone_index()

    # 2. Load documents
    print("📂 Loading documents...")
    documents = load_documents(source_path)
    if not documents:
        print("❌ No documents found. Check the source path.")
        return
    print(f"   ✅ Loaded {len(documents)} document(s)\n")

    # 3. Split into chunks
    print("✂️  Splitting into chunks...")
    chunks = split_documents(documents)
    print(f"   ✅ Created {len(chunks)} chunk(s)\n")

    # 4. Add metadata
    for chunk in chunks:
        chunk.metadata["namespace"] = namespace
        chunk.metadata["category"] = namespace

    # 5. Upload to Pinecone
    print("☁️  Uploading to Pinecone...")
    vectorstore = get_vectorstore(namespace)
    vectorstore.add_documents(chunks)
    print(f"   ✅ Successfully uploaded {len(chunks)} chunks to '{namespace}'\n")
    print("🎉 Ingestion complete!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest documents into Pinecone for the Student Assistant"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a file or directory of documents to ingest",
    )
    parser.add_argument(
        "--namespace",
        required=True,
        choices=list(NAMESPACES.keys()),
        help="Pinecone namespace (regulation, syllabus, faq, notice)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Chunk size for text splitting (default: 800)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chunk overlap for text splitting (default: 200)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"❌ Source path does not exist: {args.source}")
        sys.exit(1)

    ingest(args.source, args.namespace)


if __name__ == "__main__":
    main()
