# Where is the LLM Used?

This document explains exactly where the LLM (Large Language Model) is and is NOT used in the pipeline.

Short answer: **The LLM is used only during test generation. It is NOT used during vector store creation or retrieval.**

---

## The Three Stages and What Powers Each

```
Stage 1 — Building the Vector Store    → NO LLM  (uses Embedding Model)
Stage 2 — Retrieving from Vector Store → NO LLM  (uses Math / FAISS)
Stage 3 — Generating Tests             → YES LLM (uses Groq / ChatGroq)
```

---

## Stage 1 — Building the Vector Store (No LLM)

**What happens:** Your docs are read, split into chunks, and each chunk is converted into a vector (a list of 384 numbers).

**What does the conversion:** A local embedding model called `all-MiniLM-L6-v2`, not an LLM.

**File:** `playwright_rag/vector_store.py`, line 20
```python
self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

**File:** `playwright_rag/vector_store.py`, line 31
```python
self._db = FAISS.from_documents(docs, self.embeddings)
```

### What is an embedding model vs an LLM?

| | Embedding Model | LLM |
|--|----------------|-----|
| What it does | Converts text → numbers (vector) | Reads text → generates new text |
| Example | all-MiniLM-L6-v2 | llama-3.1-8b-instant (Groq) |
| Output | `[0.12, -0.45, 0.88, ...]` (384 numbers) | `"await page.fill('input#email', ...)"` |
| Runs where | Locally on your CPU | Groq's cloud servers |
| Needs API key | No | Yes |
| Used for | Finding similar text | Writing / reasoning |

The embedding model is a much smaller, simpler model. It does not understand language the way an LLM does — it just maps text to a point in mathematical space so similar texts end up near each other.

**No API call is made to Groq at this stage.**

---

## Stage 2 — Retrieving from the Vector Store (No LLM)

**What happens:** Your query (`"amazon login flow"`) is converted to a vector using the same embedding model, then FAISS finds the 5 stored vectors closest to it.

**What does the search:** Pure mathematics — FAISS computes L2 (Euclidean) distance between vectors.

**File:** `playwright_rag/vector_store.py`, line 44
```python
results = self._db.similarity_search_with_score(query, k=top_k)
```

Internally this does:
1. Embed the query → `[0.10, -0.44, 0.87, ...]`
2. Compare that vector against every stored vector using distance formula
3. Return the 5 closest matches

This is entirely local computation. No network call, no LLM, no API key needed.

**No API call is made to Groq at this stage.**

---

## Stage 3 — Generating Tests (LLM is used here)

**What happens:** The 5 retrieved chunks are formatted into a context block and sent to the Groq LLM along with your query and a strict system prompt. The LLM reads the context and writes the Playwright TypeScript test code.

**What does the generation:** `ChatGroq` — a cloud LLM running `llama-3.1-8b-instant` on Groq's servers.

**File:** `playwright_rag/generator.py`, line 55
```python
self.lc_llm = ChatGroq(
    api_key=simple.api_key,
    model=simple.model,
    temperature=0,
)
```

**File:** `playwright_rag/generator.py`, line 74–80
```python
chain = (
    {"context": retriever | format_docs, "query": RunnablePassthrough()}
    | PROMPT_TEMPLATE    # system prompt + retrieved context + query
    | self.lc_llm        # ← LLM called HERE
    | StrOutputParser()
)
```

**File:** `playwright_rag/generator.py`, line 96
```python
return self._clean_output(chain.invoke(query))  # ← API call to Groq happens here
```

This is the only point in the entire pipeline where a network request is made to Groq's API. The LLM receives:
- A system prompt telling it to only use what's in the context
- The retrieved chunks from your docs
- Your query

And it returns raw TypeScript test code.

**This is the only stage where the GROQ_API_KEY is used.**

---

## Visual Summary

```
docs/*.md
    │
    ▼
Ingestor reads files
    │
    ▼
RecursiveCharacterTextSplitter
splits into chunks
    │
    ▼
HuggingFaceEmbeddings          ← Embedding model (local, no API key)
converts chunks to vectors
    │
    ▼
FAISS stores vectors in memory ← Pure math, no model
    │
    │   ← your query arrives
    ▼
HuggingFaceEmbeddings          ← Same embedding model (local, no API key)
converts query to vector
    │
    ▼
FAISS similarity search        ← Pure math, no model
returns top-5 chunks
    │
    ▼
ChatGroq (llama-3.1-8b)        ← LLM called HERE (needs GROQ_API_KEY)
reads context + query
writes TypeScript tests
    │
    ▼
generated_tests/*.spec.ts
```

---

## Why This Design?

Using a small local embedding model for storage and retrieval, and only calling the LLM for generation, is intentional:

- **Speed:** Embedding and retrieval are fast local operations (milliseconds). The LLM call is the only slow step (~2–5 seconds).
- **Cost:** Embedding models are free. LLM API calls cost tokens. By doing retrieval locally, you only pay for one LLM call per test generation.
- **Privacy:** Your docs never leave your machine during the embedding and retrieval stages. Only the retrieved chunks (not your full docs) are sent to the LLM.
- **Accuracy:** The embedding model is specifically trained for semantic similarity — it is better at finding relevant text than an LLM would be. The LLM is better at writing code — so each tool is used for what it does best.
