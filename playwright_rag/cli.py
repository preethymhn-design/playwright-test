# cli.py
# CLI for the Playwright RAG system (LangChain-backed).
#
# Usage:
#   python -m playwright_rag.cli ingest docs/
#   python -m playwright_rag.cli generate "user login flow"
#   python -m playwright_rag.cli generate "checkout process" --out tests/checkout.spec.ts

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from playwright_rag.vector_store import VectorStore
from playwright_rag.ingestor import Ingestor
from playwright_rag.generator import TestGenerator

_store = None


def get_store():
    global _store
    if _store is None:
        print("Initialising vector store (loading embedding model)...")
        _store = VectorStore()
    return _store


def cmd_ingest(args):
    store = get_store()
    ingestor = Ingestor(store, chunk_size=args.chunk_size, overlap=args.overlap)
    if os.path.isdir(args.source):
        ingestor.ingest_folder(args.source)
    else:
        ingestor.ingest_file(args.source)
    print(f"\nTotal chunks in store: {len(store)}")


def cmd_generate(args):
    store = get_store()

    # Auto-ingest docs if store is empty
    docs_source = getattr(args, 'docs', 'docs')
    if len(store) == 0:
        if docs_source and os.path.exists(docs_source):
            print(f"Auto-ingesting from: {docs_source}")
            ingestor = Ingestor(store, chunk_size=500, overlap=50)
            if os.path.isdir(docs_source):
                ingestor.ingest_folder(docs_source)
            else:
                ingestor.ingest_file(docs_source)
        else:
            print(f"Vector store is empty and docs path '{docs_source}' not found.")
            print("Either run 'ingest' first or use --docs <path> to specify your docs.")
            sys.exit(1)

    gen = TestGenerator(store, top_k=args.top_k, provider=args.provider)

    print(f"\nGenerating tests for: {args.query}\n")
    result = gen.generate_with_context(args.query)

    print("=== RETRIEVED CONTEXT ===")
    for i, chunk in enumerate(result["context"], 1):
        print(f"\n[{i}] (score={chunk['score']:.4f}) {chunk['metadata'].get('source', '')}")
        preview = chunk["text"][:300]
        print(preview + "..." if len(chunk["text"]) > 300 else preview)

    print("\n=== GENERATED TESTS ===\n")
    print(result["tests"])

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result["tests"])
        print(f"\nSaved to: {args.out}")


def main():
    parser = argparse.ArgumentParser(description="Playwright RAG Test Generator (LangChain)")
    sub = parser.add_subparsers(dest="command")

    p_ingest = sub.add_parser("ingest", help="Ingest documents into vector store")
    p_ingest.add_argument("source", help="File or folder to ingest")
    p_ingest.add_argument("--chunk-size", type=int, default=500)
    p_ingest.add_argument("--overlap", type=int, default=50)

    p_gen = sub.add_parser("generate", help="Generate Playwright tests from a query")
    p_gen.add_argument("query", help="What to test, e.g. 'user login flow'")
    p_gen.add_argument("--provider", default="groq", help="LLM provider (groq/gemini/openai/ollama)")
    p_gen.add_argument("--top-k", type=int, default=5)
    p_gen.add_argument("--out", default=None, help="Output .spec.ts file path")
    p_gen.add_argument("--docs", default="docs", help="Docs folder/file to auto-ingest if store is empty (default: docs/)")

    args = parser.parse_args()
    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "generate":
        cmd_generate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
