# Playwright RAG Test Generator

Automatically generate Playwright TypeScript test cases from your documentation using RAG (Retrieval-Augmented Generation).

Drop in your specs, user stories, or any docs — the system embeds them into a vector store, retrieves the most relevant context for your query, and generates ready-to-run Playwright tests via an LLM.

---

## How It Works

```
Your Docs (.md / .txt / .pdf)
        ↓
   LangChain Document Loaders
        ↓
   RecursiveCharacterTextSplitter
        ↓
   HuggingFace Embeddings (all-MiniLM-L6-v2, local)
        ↓
   FAISS Vector Store
        ↓
   LangChain LCEL Retrieval Chain
        ↓
   ChatGroq LLM → Playwright TypeScript Tests
```

---

## Project Structure

```
playwright_rag/
  vector_store.py     # In-memory vector DB with cosine similarity search
  ingestor.py         # Loads and chunks .md / .txt / .pdf files
  generator.py        # Retrieves context and generates Playwright tests
  cli.py              # Command-line interface

ragas_simple/         # RAG evaluation framework (faithfulness, precision, recall)
docs/                 # Put your spec/documentation files here
generated_tests/      # Generated .spec.ts files land here
run_playwright_rag.py # Demo script
run_groq_eval.py      # RAG evaluation script
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install langchain langchain-community langchain-groq langchain-huggingface faiss-cpu sentence-transformers
```

For PDF support:
```bash
pip install pypdf
```

### 2. API Keys

The app uses **Groq** (free) as the default LLM provider. The key is pre-configured in `ragas_simple/llm.py`.

To use a different provider, set the environment variable:

| Provider | Environment Variable | Free Tier |
|----------|---------------------|-----------|
| Groq     | `GROQ_API_KEY`      | Yes       |
| Gemini   | `GEMINI_API_KEY`    | Yes       |
| OpenAI   | `OPENAI_API_KEY`    | No        |
| Ollama   | *(none needed)*     | Local     |

---

## Usage

### Option A — Python Script (quickest)

1. Add your docs to the `docs/` folder
2. Run:

```bash
python run_playwright_rag.py
```

Generated tests are saved to `generated_tests/`.

To change the queries, edit the `queries` list in `run_playwright_rag.py`:

```python
queries = [
    "user login with valid and invalid credentials",
    "checkout flow from cart to order confirmation",
    "password reset flow",
]
```

---

### Option B — CLI

**Ingest documents:**

```bash
# Ingest a whole folder
python -m playwright_rag.cli ingest docs/

# Ingest a single file
python -m playwright_rag.cli ingest docs/my_spec.md

# Custom chunk size
python -m playwright_rag.cli ingest docs/ --chunk-size 400 --overlap 40
```

**Generate tests:**

```bash
# Minimal — auto-ingests docs/ and prints to terminal
python -m playwright_rag.cli generate "checkout process"

# With output file
python -m playwright_rag.cli generate "checkout process" --out generated_tests/checkout.spec.ts

# With custom docs folder + output file
python -m playwright_rag.cli generate "checkout process" --docs docs/ --out generated_tests/checkout.spec.ts
```

---

### Option C — Python API

```python
from playwright_rag import VectorStore, Ingestor, TestGenerator

# 1. Setup — FAISS + HuggingFace embeddings (LangChain)
store = VectorStore()  # loads all-MiniLM-L6-v2 locally

# 2. Ingest your docs
ingestor = Ingestor(store, chunk_size=500, overlap=50)
ingestor.ingest_folder("docs/")          # folder
ingestor.ingest_file("my_spec.md")       # single file
ingestor.ingest_text("raw text...", source="inline")  # raw string

# 3. Generate tests (LangChain LCEL chain + ChatGroq)
gen = TestGenerator(store, top_k=5, provider="groq")

tests = gen.generate("user registration flow")
print(tests)

# With context visibility
result = gen.generate_with_context("login page validation")
print(result["tests"])    # generated TypeScript
print(result["context"])  # retrieved chunks with scores
```

---

## Adding Your Own Documents

Just drop files into `docs/` — any of these formats work:

- `.md` — Markdown specs, user stories, feature descriptions
- `.txt` — Plain text documentation
- `.pdf` — PDF specs or design documents (requires `pip install pypdf`)

The more detail your docs contain (selectors, URLs, expected messages, flows), the better the generated tests will be.

---

## Evaluating RAG Quality

The `ragas_simple` module evaluates how well the RAG pipeline performs across four metrics:

| Metric | What it measures |
|--------|-----------------|
| Faithfulness | Are generated answers grounded in the retrieved context? |
| Context Precision | Are retrieved chunks actually relevant? |
| Context Recall | Does the context cover the reference answer? |
| Answer Relevancy | Does the answer address the question? |

Run the evaluation:

```bash
python run_groq_eval.py
```

Results are saved to `eval_results.csv`.

---

## Supported LLM Providers

```python
# Groq (free, fast — default)
llm = SimpleLLM(provider="groq")

# Google Gemini (free tier)
llm = SimpleLLM(provider="gemini")

# OpenAI
llm = SimpleLLM(provider="openai", model="gpt-4o-mini")

# Ollama (fully local, no API key)
# First run: ollama pull llama3.2
llm = SimpleLLM(provider="ollama")
```
