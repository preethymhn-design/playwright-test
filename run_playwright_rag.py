# run_playwright_rag.py
# Demo: ingest docs and generate Playwright tests using LangChain RAG.
#
# Run:
#   python run_playwright_rag.py

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from playwright_rag.vector_store import VectorStore
from playwright_rag.ingestor import Ingestor
from playwright_rag.generator import TestGenerator

# ── 1. Vector store (FAISS + HuggingFace embeddings via LangChain) ───────────
print("Initialising vector store...")
store = VectorStore()  # loads all-MiniLM-L6-v2 locally

# ── 2. Ingest documents ───────────────────────────────────────────────────────
print("\nIngesting documents from docs/")
ingestor = Ingestor(store, chunk_size=500, overlap=50)
ingestor.ingest_folder("docs/")
print(f"Total chunks stored: {len(store)}")

# ── 3. Generator (LangChain LCEL chain with Groq) ────────────────────────────
gen = TestGenerator(store, top_k=5, provider="groq")

# ── 4. Generate tests ─────────────────────────────────────────────────────────
queries = [
    "user login with valid and invalid credentials",
    "checkout flow from cart to order confirmation",
]

os.makedirs("generated_tests", exist_ok=True)

for query in queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print("="*60)

    result = gen.generate_with_context(query)

    print("\n--- Retrieved Context ---")
    for i, chunk in enumerate(result["context"], 1):
        src = chunk["metadata"].get("source", "unknown")
        print(f"  [{i}] score={chunk['score']:.4f}  source={src}")

    print("\n--- Generated Test ---\n")
    print(result["tests"])

    safe_name = query.replace(" ", "_").replace("/", "_")[:50]
    out_path = f"generated_tests/{safe_name}.spec.ts"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result["tests"])
    print(f"\nSaved: {out_path}")
