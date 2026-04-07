# Playwright RAG Test Generator

A RAG (Retrieval-Augmented Generation) pipeline that reads your documentation, understands your application's UI, and generates executable Playwright TypeScript test cases — grounded strictly in what your docs describe.

No hallucination. Every selector, URL, and assertion in the generated tests comes directly from your documentation.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Understanding the Vector Database](#understanding-the-vector-database)
3. [Step-by-Step Deep Dive](#step-by-step-deep-dive)
4. [Architecture](#architecture)
5. [Project Structure](#project-structure)
6. [Prerequisites](#prerequisites)
7. [Installation](#installation)
8. [Configuration](#configuration)
9. [Writing Good Documentation](#writing-good-documentation)
10. [Generating Tests](#generating-tests)
11. [Running Tests](#running-tests)
12. [npm Scripts Reference](#npm-scripts-reference)
13. [Python CLI Reference](#python-cli-reference)
14. [RAG Evaluation](#rag-evaluation)
15. [Supported LLM Providers](#supported-llm-providers)
16. [Troubleshooting](#troubleshooting)

---

## How It Works

Think of this system like a very smart librarian. You give the librarian a shelf of books (your docs). When you ask a question ("generate tests for the login page"), the librarian doesn't read every book from scratch. Instead, they already have a mental map of every paragraph — they instantly find the most relevant pages and hand them to the AI, which then writes the tests based only on those pages.

Here is the full pipeline in plain terms:

```
Step 1 — You write documentation (.md / .txt / .pdf)
         Describe your app's pages, selectors, URLs, and expected behaviour

Step 2 — Document Loading (LangChain Loaders)
         TextLoader / UnstructuredMarkdownLoader / PyPDFLoader
         Reads raw text from each file in your docs/ folder

Step 3 — Chunking (RecursiveCharacterTextSplitter)
         Splits documents into overlapping 500-character chunks
         Preserves sentence and paragraph boundaries
         Overlap of 50 characters ensures context is not lost at boundaries

Step 4 — Embedding (HuggingFace all-MiniLM-L6-v2)
         Each chunk is converted to a 384-dimensional vector (a list of 384 numbers)
         Runs entirely on your local machine — no API key needed
         Model is downloaded once (~90MB) and cached

Step 5 — Vector Store (FAISS in-memory index)
         All chunk vectors are stored in a FAISS index
         Lives in RAM — fast to search, rebuilt each run from your docs

Step 6 — Retrieval (Similarity Search)
         Your query is embedded using the same model
         Top-5 most semantically similar chunks are retrieved
         Only content from YOUR docs is ever returned

Step 7 — Generation (LangChain LCEL chain + ChatGroq)
         Retrieved chunks are injected into a strict prompt
         LLM is instructed to use ONLY what is in the retrieved context
         Outputs raw TypeScript — no prose, no markdown fences

Step 8 — Output (.spec.ts file)
         A valid, executable Playwright test file is saved to generated_tests/
         Filename is derived from your query
```

### Why tests stay grounded in your docs

The LLM prompt enforces five strict rules:

1. Use ONLY selectors, URLs, field names, and error messages from the context
2. Do NOT invent, assume, or guess any UI element not in the context
3. If the context does not mention something, do not test it
4. Every locator must come directly from the context
5. Every URL, error message, and assertion must be copied exactly from the context

This means if your docs say `input#ap_email`, the test will use `input#ap_email`. If your docs don't mention a field, it won't appear in the test.

---

## Understanding the Vector Database

This is the heart of the system. Understanding it will help you write better docs and get better tests.

### What is a vector?

A vector is just a list of numbers. For example:

```
"Login page: input#ap_email"  →  [0.12, -0.45, 0.88, 0.03, ..., 0.67]
                                   ↑ 384 numbers total
```

The embedding model (all-MiniLM-L6-v2) converts any piece of text into 384 numbers. These numbers capture the *meaning* of the text — not just the words, but what the text is about.

Two pieces of text that mean similar things will produce vectors that are numerically close to each other. Two unrelated pieces of text will produce vectors that are far apart.

```
"user login form"          →  [0.12, -0.45, 0.88, ...]   ← close together
"sign in with email"       →  [0.11, -0.43, 0.90, ...]   ← (similar meaning)

"shopping cart subtotal"   →  [0.78,  0.22, -0.31, ...]  ← far away
                                                            (different topic)
```

### What is FAISS?

FAISS (Facebook AI Similarity Search) is the vector database used in this project. It is a library that:

- Stores thousands of vectors in memory
- Can search through all of them in milliseconds
- Finds the vectors most similar to a query vector (nearest neighbour search)

Think of it like a search engine, but instead of matching keywords, it matches *meaning*.

### Where is the vector database stored?

The FAISS index in this project is **in-memory only**. This means:

- It lives in RAM while the Python process is running
- It is rebuilt from scratch every time you run `npm run generate`
- It does not persist to disk between runs
- There is no database file to find on your filesystem

This is intentional — your docs are small enough that rebuilding takes only a few seconds, and it keeps the setup simple with no database management needed.

If you want to inspect what is in the store at runtime, the `VectorStore` class in `playwright_rag/vector_store.py` exposes:

```python
len(store)          # total number of chunks stored
store.search("login page", top_k=3)  # returns top 3 matching chunks
```

### What does the database look like internally?

Conceptually, the FAISS index holds a table like this:

```
┌────────┬──────────────────────────────────────────────────────────────────┬──────────────────────────────┐
│ Index  │ Vector (384 numbers)                                             │ Metadata                     │
├────────┼──────────────────────────────────────────────────────────────────┼──────────────────────────────┤
│   0    │ [0.12, -0.45, 0.88, 0.03, 0.71, -0.22, ..., 0.67]              │ source: amazon_login_spec.md │
│   1    │ [0.09, -0.41, 0.85, 0.07, 0.68, -0.19, ..., 0.71]              │ source: amazon_login_spec.md │
│   2    │ [0.78,  0.22, -0.31, 0.55, -0.44, 0.13, ..., 0.02]             │ source: amazon_cart_spec.md  │
│   3    │ [0.81,  0.19, -0.28, 0.51, -0.41, 0.17, ..., 0.05]             │ source: amazon_cart_spec.md  │
│   4    │ [0.33, -0.12,  0.55, 0.29,  0.60, -0.08, ..., 0.44]            │ source: amazon_search_spec.md│
│  ...   │ ...                                                              │ ...                          │
└────────┴──────────────────────────────────────────────────────────────────┴──────────────────────────────┘
```

Each row is one chunk of text from your docs, stored as its vector representation alongside the source filename.

### How does search work?

When you run `npm run generate -- "amazon login flow"`:

1. The query `"amazon login flow"` is converted to a vector: `[0.10, -0.44, 0.87, ...]`
2. FAISS computes the distance between this query vector and every stored vector
3. The 5 closest vectors are returned (top-K search)
4. The original text chunks for those vectors are retrieved
5. Those text chunks become the context sent to the LLM

```
Query vector:  [0.10, -0.44, 0.87, ...]

Distances:
  chunk 0 (login spec)   → distance 0.05  ← very close (relevant)
  chunk 1 (login spec)   → distance 0.08  ← close (relevant)
  chunk 2 (cart spec)    → distance 0.72  ← far (not relevant)
  chunk 3 (cart spec)    → distance 0.75  ← far (not relevant)
  chunk 4 (search spec)  → distance 0.41  ← medium

Top-5 returned: chunks 0, 1, 4, and 2 closest others
```

The distance metric used is L2 (Euclidean distance). Lower distance = more similar = more relevant.

### Why rebuild every run instead of persisting?

For this use case, rebuilding is the right choice because:

- Your docs folder is small (a few KB of markdown files)
- Rebuilding takes 2–5 seconds
- You always get a fresh, consistent index that reflects your latest docs
- No stale data from previous runs
- No database files to manage or version

If your docs grow very large (hundreds of files), you could save and load the FAISS index using LangChain's built-in persistence:

```python
# Save to disk
store._db.save_local("faiss_index")

# Load from disk next time
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
```

This would create a `faiss_index/` folder with two files:
- `faiss_index/index.faiss` — the binary vector index
- `faiss_index/index.pkl` — the text chunks and metadata

---

## Step-by-Step Deep Dive

This section walks through exactly what happens, step by step, when you run a single command.

### The command

```bash
npm run generate -- "amazon login flow"
```

---

### Step 1 — npm hands off to generate.js

`package.json` maps `npm run generate` to `node generate.js`. The `--` separator passes everything after it as arguments to the script.

`generate.js` does three things:

```javascript
const query = process.argv[2];
// query = "amazon login flow"

const filename = query.trim().toLowerCase()
  .replace(/\s+/g, '_')
  .replace(/[^a-z0-9_]/g, '') + '.spec.ts';
// filename = "amazon_login_flow.spec.ts"

const cmd = `python -m playwright_rag.cli generate "${query}" --docs docs/ --out generated_tests/${filename}`;
execSync(cmd, { stdio: 'inherit' });
```

It converts your query into a safe filename and calls the Python CLI.

---

### Step 2 — Python CLI starts up

`playwright_rag/cli.py` parses the arguments:

```
query   = "amazon login flow"
docs    = "docs/"
out     = "generated_tests/amazon_login_flow.spec.ts"
top_k   = 5
provider = "groq"
```

It then initialises the `VectorStore`, which loads the embedding model into memory.

---

### Step 3 — Embedding model loads

`playwright_rag/vector_store.py` creates a `HuggingFaceEmbeddings` instance:

```python
self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

The model `all-MiniLM-L6-v2` is a small, fast sentence transformer. It was trained to understand the semantic meaning of sentences. It runs entirely on your CPU — no GPU needed, no internet call.

First run: downloads ~90MB to `~/.cache/huggingface/hub/`
Subsequent runs: loads from cache in under 1 second.

---

### Step 4 — Documents are loaded from docs/

`playwright_rag/ingestor.py` walks the `docs/` folder and loads each file:

```
docs/amazon_login_spec.md     → UnstructuredMarkdownLoader
docs/amazon_search_spec.md    → UnstructuredMarkdownLoader
docs/amazon_product_spec.md   → UnstructuredMarkdownLoader
docs/amazon_cart_spec.md      → UnstructuredMarkdownLoader
docs/amazon_checkout_spec.md  → UnstructuredMarkdownLoader
docs/amazon_orders_spec.md    → UnstructuredMarkdownLoader
```

Each file is read as plain text. Markdown formatting (headers, bullets) is preserved as text.

---

### Step 5 — Documents are split into chunks

`RecursiveCharacterTextSplitter` splits each document into overlapping chunks:

```
chunk_size = 500 characters
chunk_overlap = 50 characters
separators = ["\n\n", "\n", ".", " ", ""]
```

Example — this section of `amazon_login_spec.md`:

```markdown
## UI Elements

### Email / Phone Step
- Email input: `input#ap_email`
- Continue button: `input#continue`
- Password input: `input#ap_password`
- Sign-In button: `input#signInSubmit`
- Error message container: `div.a-alert-content`

### Error Messages
- Invalid email: `div.a-alert-content` containing "We cannot find an account"
- Wrong password: `div.a-alert-content` containing "Your password is incorrect"
```

Gets split into chunks like:

```
Chunk 0: "## UI Elements\n\n### Email / Phone Step\n- Email input: `input#ap_email`\n
          - Continue button: `input#continue`\n- Password input: `input#ap_password`\n
          - Sign-In button: `input#signInSubmit`\n- Error message container: `div.a-alert-content`"

Chunk 1: "- Error message container: `div.a-alert-content`\n\n### Error Messages\n
          - Invalid email: `div.a-alert-content` containing \"We cannot find an account\"\n
          - Wrong password: `div.a-alert-content` containing \"Your password is incorrect\""
```

Notice chunk 1 starts with the last line of chunk 0 — that is the 50-character overlap, ensuring no information is lost at the boundary.

---

### Step 6 — Chunks are embedded and stored in FAISS

Each chunk is passed through the embedding model to produce a 384-number vector:

```
Chunk 0 text  →  model  →  [0.12, -0.45, 0.88, 0.03, ..., 0.67]  (384 numbers)
Chunk 1 text  →  model  →  [0.09, -0.41, 0.85, 0.07, ..., 0.71]  (384 numbers)
Chunk 2 text  →  model  →  [0.78,  0.22, -0.31, 0.55, ..., 0.02]  (384 numbers)
...
```

All vectors are added to the FAISS index in memory. The original text and source filename are stored alongside each vector.

For a typical docs folder with 6 files, this produces around 30–50 chunks total.

---

### Step 7 — Your query is embedded and searched

The query `"amazon login flow"` is converted to a vector using the same model:

```
"amazon login flow"  →  model  →  [0.10, -0.44, 0.87, 0.05, ..., 0.69]
```

FAISS computes the L2 distance between this query vector and every stored vector. The 5 chunks with the smallest distance (most similar meaning) are returned.

For the query `"amazon login flow"`, the top results would be chunks from `amazon_login_spec.md` because those chunks contain text about login — email inputs, passwords, sign-in buttons — which is semantically close to the query.

---

### Step 8 — Context is formatted and sent to the LLM

The 5 retrieved chunks are formatted into a context block:

```
[Source: amazon_login_spec.md]
## URL
Login page: https://www.amazon.in/ap/signin

---

[Source: amazon_login_spec.md]
### Email / Phone Step
- Email input: `input#ap_email`
- Continue button: `input#continue`
...

---

[Source: amazon_login_spec.md]
### Error Messages
- Wrong password: "Your password is incorrect"
...
```

This context block, along with the query and the strict system prompt, is sent to the Groq LLM via LangChain's LCEL chain:

```python
chain = (
    {"context": retriever | format_docs, "query": RunnablePassthrough()}
    | PROMPT_TEMPLATE   # system prompt + context + query
    | self.lc_llm       # ChatGroq (llama-3.1-8b-instant)
    | StrOutputParser() # extract text from response
)
```

---

### Step 9 — LLM generates the test code

The LLM receives the context and the strict system prompt that says:

> Use ONLY the selectors, URLs, field names, and error messages that appear verbatim in the CONTEXT. Do NOT invent anything.

The LLM outputs raw TypeScript:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Amazon Login Flow', () => {
  test('Successful login with valid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('https://www.amazon.in/ap/signin');
    // Enter email
    await page.fill('input#ap_email', 'user@example.com');
    // Click continue
    await page.click('input#continue');
    // Enter password
    await page.fill('input#ap_password', 'password123');
    // Click sign in
    await page.click('input#signInSubmit');
    // Verify redirect to home
    await expect(page).toHaveURL('https://www.amazon.in');
  });
  ...
});
```

Every selector (`input#ap_email`, `input#continue`, `input#signInSubmit`) came directly from the retrieved context. The LLM did not invent them.

---

### Step 10 — Output is cleaned and saved

`_clean_output()` strips any accidental markdown fences the LLM might add:

```python
fenced = re.search(r"```(?:typescript|ts)?\s*\n(.*?)```", text, re.DOTALL)
if fenced:
    return fenced.group(1).strip()
```

The clean TypeScript is written to `generated_tests/amazon_login_flow.spec.ts`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        npm run generate                             │
│                    "amazon login flow"                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                        generate.js
                  (derives filename from query)
                               │
                               ▼
         python -m playwright_rag.cli generate
              "amazon login flow"
              --docs docs/
              --out generated_tests/amazon_login_flow.spec.ts
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             VectorStore            Ingestor
          (FAISS + LangChain)   (LangChain Loaders)
                    │                     │
                    │    docs/*.md        │
                    │◄────────────────────┘
                    │
                    │  similarity_search("amazon login flow")
                    │
                    ▼
           Top-5 relevant chunks
           from your documentation
                    │
                    ▼
            TestGenerator
         (LangChain LCEL chain)
                    │
          ┌─────────┴──────────┐
          │                    │
          ▼                    ▼
   ChatPromptTemplate      ChatGroq LLM
   (strict no-hallucinate  (llama-3.1-8b-instant)
    system prompt)
          │
          ▼
   StrOutputParser
   + _clean_output()
   (strips any markdown fences)
          │
          ▼
   generated_tests/amazon_login_flow.spec.ts
```

---

## Execution Trace

A quick reference showing which file and function handles each stage of the pipeline, with the most important line highlighted.

```
npm run generate -- "amazon login flow"
```

| # | What happens | File | Function / Line | Key line |
|---|-------------|------|-----------------|----------|
| 1 | npm triggers the wrapper script | `package.json` | `scripts.generate` | `"generate": "node generate.js"` |
| 2 | Query received, filename derived | `generate.js` | top-level, line 7 | `const query = process.argv[2]` |
| 3 | Filename built from query | `generate.js` | line 16 | `query.trim().toLowerCase().replace(/\s+/g, '_')` |
| 4 | Python CLI invoked | `generate.js` | line 19–24 | `execSync(cmd, { stdio: 'inherit' })` |
| 5 | CLI args parsed | `playwright_rag/cli.py` | `main()`, line 78 | `args = parser.parse_args()` |
| 6 | VectorStore initialised | `playwright_rag/cli.py` | `get_store()`, line 22 | `_store = VectorStore()` |
| 7 | Embedding model loaded | `playwright_rag/vector_store.py` | `__init__()`, line 20 | `self.embeddings = HuggingFaceEmbeddings(model_name=model_name)` |
| 8 | FAISS index created (empty) | `playwright_rag/vector_store.py` | `__init__()`, line 21 | `self._db = None` |
| 9 | Auto-ingest triggered | `playwright_rag/cli.py` | `cmd_generate()`, line 42 | `ingestor.ingest_folder(docs_source)` |
| 10 | Each doc file loaded | `playwright_rag/ingestor.py` | `ingest_folder()`, line 47 | `self.ingest_file(os.path.join(root, fname))` |
| 11 | File read by LangChain loader | `playwright_rag/ingestor.py` | `ingest_file()`, line 35 | `docs = self._load_md(path)` |
| 12 | Text split into chunks | `playwright_rag/ingestor.py` | `ingest_file()`, line 38 | `chunks = self.splitter.split_documents(docs)` |
| 13 | Chunks embedded + stored in FAISS | `playwright_rag/vector_store.py` | `add_documents()`, line 31 | `self._db = FAISS.from_documents(docs, self.embeddings)` |
| 14 | TestGenerator created | `playwright_rag/cli.py` | `cmd_generate()`, line 50 | `gen = TestGenerator(store, top_k=args.top_k, provider=args.provider)` |
| 15 | ChatGroq LLM initialised | `playwright_rag/generator.py` | `__init__()`, line 55 | `self.lc_llm = ChatGroq(api_key=simple.api_key, model=simple.model, temperature=0)` |
| 16 | generate_with_context called | `playwright_rag/cli.py` | `cmd_generate()`, line 53 | `result = gen.generate_with_context(args.query)` |
| 17 | Top-5 chunks retrieved from FAISS | `playwright_rag/vector_store.py` | `search()`, line 44 | `results = self._db.similarity_search_with_score(query, k=top_k)` |
| 18 | LangChain LCEL chain built | `playwright_rag/generator.py` | `_build_chain()`, line 74 | `chain = ({"context": retriever \| format_docs, "query": RunnablePassthrough()} \| PROMPT_TEMPLATE \| self.lc_llm \| StrOutputParser())` |
| 19 | Chain invoked with query | `playwright_rag/generator.py` | `generate()`, line 96 | `return self._clean_output(chain.invoke(query))` |
| 20 | Markdown fences stripped | `playwright_rag/generator.py` | `_clean_output()`, line 103 | `fenced = re.search(r"\`\`\`(?:typescript\|ts)?\\s*\\n(.*?)\`\`\`", text, re.DOTALL)` |
| 21 | Test file written to disk | `playwright_rag/cli.py` | `cmd_generate()`, line 68 | `f.write(result["tests"])` |

### Call chain summary

```
npm run generate -- "amazon login flow"
  └── generate.js : line 24        execSync(cmd)
        └── cli.py : main()        line 78   parse_args()
              └── cli.py : cmd_generate()
                    line 22   get_store() → VectorStore.__init__()
                    │           vector_store.py line 20  HuggingFaceEmbeddings()
                    │           vector_store.py line 21  self._db = None
                    │
                    line 42   ingestor.ingest_folder("docs/")
                    │           ingestor.py line 47  ingest_file() per file
                    │           ingestor.py line 35  _load_md() / TextLoader
                    │           ingestor.py line 38  splitter.split_documents()
                    │           vector_store.py line 31  FAISS.from_documents()
                    │
                    line 50   TestGenerator(store, ...)
                    │           generator.py line 55  ChatGroq(api_key, model)
                    │
                    line 53   gen.generate_with_context(query)
                                vector_store.py line 44  similarity_search_with_score()
                                generator.py line 74  _build_chain()
                                generator.py line 96  chain.invoke(query)
                                generator.py line 103 _clean_output()
                                cli.py line 68        f.write(result["tests"])
```

```
playwright-test/
│
├── docs/                              # Your application documentation
│   ├── amazon_login_spec.md           # Login page — selectors, URLs, error messages
│   ├── amazon_search_spec.md          # Search bar and results page
│   ├── amazon_product_spec.md         # Product detail page
│   ├── amazon_cart_spec.md            # Shopping cart
│   ├── amazon_checkout_spec.md        # Full checkout flow
│   ├── amazon_orders_spec.md          # Order history and account
│   ├── login_spec.md                  # Generic login spec (example)
│   └── checkout_spec.md               # Generic checkout spec (example)
│
├── playwright_rag/                    # RAG pipeline (Python)
│   ├── __init__.py
│   ├── vector_store.py                # FAISS vector store via LangChain
│   ├── ingestor.py                    # Document loader + chunker via LangChain
│   ├── generator.py                   # LangChain LCEL chain → Playwright tests
│   └── cli.py                         # Command-line interface
│
├── ragas_simple/                      # RAG quality evaluation framework
│   ├── __init__.py
│   ├── llm.py                         # Multi-provider LLM wrapper (Groq/Gemini/OpenAI/Ollama)
│   ├── evaluate.py                    # Evaluation runner
│   ├── dataset.py                     # EvalDataset class
│   ├── sample.py                      # EvalSample class
│   └── metrics/
│       ├── faithfulness.py            # Is the answer grounded in context?
│       ├── context_precision.py       # Are retrieved chunks relevant?
│       ├── context_recall.py          # Does context cover the reference answer?
│       └── answer_relevancy.py        # Does the answer address the question?
│
├── generated_tests/                   # Generated .spec.ts files (output)
│   ├── amazon_login_flow.spec.ts
│   ├── checkout_process.spec.ts
│   └── ...
│
├── generate.js                        # npm generate wrapper (derives filename from query)
├── run_playwright_rag.py              # Batch generation script
├── run_groq_eval.py                   # RAG evaluation script
├── playwright.config.ts               # Playwright configuration
├── package.json                       # npm scripts
├── tsconfig.json                      # TypeScript configuration
├── requirements.txt                   # Python dependencies
├── .env                               # API keys (gitignored — never committed)
└── .gitignore
```

---

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm 9 or higher
- A free Groq API key (https://console.groq.com)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/preethymhn-design/playwright-test.git
cd playwright-test
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
pip install langchain langchain-community langchain-groq langchain-huggingface faiss-cpu sentence-transformers python-dotenv openai
```

For PDF document support:
```bash
pip install pypdf
```

### 3. Install Node dependencies

```bash
npm install
```

### 4. Install Playwright browsers

```bash
npx playwright install chromium
```

---

## Configuration

### API Keys

Create a `.env` file in the project root. This file is gitignored and never committed.

```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free Groq key at https://console.groq.com (no credit card required).

### Playwright Base URL

Before running tests, set your application's base URL in `playwright.config.ts`:

```typescript
use: {
  baseURL: 'https://www.amazon.in',  // change to your app URL
  headless: true,
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
}
```

### LLM Provider

The default provider is Groq (`llama-3.1-8b-instant`). To change it, pass `--provider` to the CLI:

```bash
python -m playwright_rag.cli generate "login flow" --provider gemini
python -m playwright_rag.cli generate "login flow" --provider openai
python -m playwright_rag.cli generate "login flow" --provider ollama
```

---

## Writing Good Documentation

The quality of generated tests depends entirely on the quality of your documentation. The more precise your docs, the more accurate the tests.

### What to include in your docs

| Element | Example |
|---------|---------|
| Page URL | `Login page: https://www.amazon.in/ap/signin` |
| Input selectors | `Email input: input#ap_email` |
| Button selectors | `Sign-In button: input#signInSubmit` |
| Error messages | `Wrong password: "Your password is incorrect"` |
| Expected redirects | `Successful login redirects to https://www.amazon.in` |
| Conditional behaviour | `"Track package" is only visible for shipped orders` |

### Example of a well-structured doc

```markdown
# Login Page

## URL
https://www.amazon.in/ap/signin

## UI Elements
- Email input: `input#ap_email`
- Continue button: `input#continue`
- Password input: `input#ap_password`
- Sign-In button: `input#signInSubmit`
- Error message container: `div.a-alert-content`

## Behaviour
- Login is two-step: email first, then password
- Successful login redirects to https://www.amazon.in
- Wrong password shows: "Your password is incorrect"
- Empty email shows: "Enter your email or mobile phone number"
```

### Supported file formats

| Format | Notes |
|--------|-------|
| `.md` | Recommended — Markdown with headers and bullet points |
| `.txt` | Plain text |
| `.pdf` | Requires `pip install pypdf` |

---

## Generating Tests

### Using npm (recommended)

```bash
npm run generate -- "<your query>"
```

The query describes what you want to test. The filename is automatically derived from the query.

**Examples:**

```bash
# Amazon login tests → generated_tests/amazon_login_flow.spec.ts
npm run generate -- "amazon login flow"

# Checkout tests → generated_tests/checkout_process.spec.ts
npm run generate -- "checkout process"

# Search tests → generated_tests/product_search.spec.ts
npm run generate -- "product search"

# Cart tests → generated_tests/add_to_cart.spec.ts
npm run generate -- "add to cart"

# Order history tests → generated_tests/order_history.spec.ts
npm run generate -- "order history"
```

### What happens when you run the command

```
npm run generate -- "amazon login flow"
```

1. `generate.js` receives the query `"amazon login flow"`
2. Derives the output filename: `amazon_login_flow.spec.ts`
3. Calls: `python -m playwright_rag.cli generate "amazon login flow" --docs docs/ --out generated_tests/amazon_login_flow.spec.ts`
4. Python loads the embedding model (all-MiniLM-L6-v2, local)
5. Ingests all files from `docs/` into the FAISS vector store
6. Embeds the query and retrieves the top-5 most relevant chunks
7. Sends the chunks + query to the Groq LLM via LangChain
8. Saves the generated TypeScript to `generated_tests/amazon_login_flow.spec.ts`

### Filename derivation rules

| Query | Output file |
|-------|-------------|
| `"amazon login flow"` | `amazon_login_flow.spec.ts` |
| `"checkout process"` | `checkout_process.spec.ts` |
| `"add to cart"` | `add_to_cart.spec.ts` |
| `"order history & tracking"` | `order_history__tracking.spec.ts` |

Spaces → underscores, special characters stripped, all lowercase.

---

## Running Tests

### Run all generated tests

```bash
npm test
```

Runs all `.spec.ts` files in `generated_tests/` using Playwright with Chromium.

### Run a specific test file

```bash
npx playwright test generated_tests/amazon_login_flow.spec.ts
```

### Run tests and open the HTML report

```bash
npm run test:report
```

### Run tests in headed mode (see the browser)

```bash
npx playwright test --headed
```

### Run tests in debug mode

```bash
npx playwright test --debug
```

---

## npm Scripts Reference

| Script | Command | Description |
|--------|---------|-------------|
| `npm run generate -- "<query>"` | `node generate.js` | Ingest docs + generate `.spec.ts` from query |
| `npm test` | `npx playwright test` | Run all tests in `generated_tests/` |
| `npm run test:report` | `npx playwright test --reporter=html` | Run tests and open HTML report |

---

## Python CLI Reference

The CLI can also be used directly for more control.

### generate

```bash
python -m playwright_rag.cli generate "<query>" [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--docs` | `docs` | Folder or file to ingest (auto-ingested if store is empty) |
| `--out` | None (prints to terminal) | Output `.spec.ts` file path |
| `--provider` | `groq` | LLM provider: `groq`, `gemini`, `openai`, `ollama` |
| `--top-k` | `5` | Number of context chunks to retrieve |

**Examples:**

```bash
# Print to terminal
python -m playwright_rag.cli generate "login flow"

# Save to file
python -m playwright_rag.cli generate "login flow" --out generated_tests/login.spec.ts

# Custom docs folder
python -m playwright_rag.cli generate "login flow" --docs my_docs/ --out generated_tests/login.spec.ts

# Use Gemini instead of Groq
python -m playwright_rag.cli generate "login flow" --provider gemini

# Retrieve more context chunks for complex flows
python -m playwright_rag.cli generate "full checkout flow" --top-k 10
```

### ingest (optional — generate auto-ingests)

```bash
python -m playwright_rag.cli ingest <source> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--chunk-size` | `500` | Characters per chunk |
| `--overlap` | `50` | Overlap between chunks |

```bash
# Ingest a folder
python -m playwright_rag.cli ingest docs/

# Ingest a single file
python -m playwright_rag.cli ingest docs/amazon_login_spec.md

# Custom chunk size
python -m playwright_rag.cli ingest docs/ --chunk-size 300 --overlap 30
```

---

## RAG Evaluation

The `ragas_simple` module measures how well the RAG pipeline performs across four metrics.

| Metric | What it measures | Score |
|--------|-----------------|-------|
| Faithfulness | Are generated answers grounded in the retrieved context? | 0–1 |
| Context Precision | Are retrieved chunks actually relevant to the query? | 0–1 |
| Context Recall | Does the context cover the reference answer? | 0–1 |
| Answer Relevancy | Does the answer address the question asked? | 0–1 |

### Run the evaluation

```bash
python run_groq_eval.py
```

Results are printed to the terminal and saved to `eval_results.csv`.

### Sample output

```
Running metric: faithfulness
Running metric: context_precision
Running metric: context_recall
Running metric: answer_relevancy

Evaluation complete.
{'faithfulness': 0.8333, 'context_precision': 0.6667, 'context_recall': 0.6667, 'answer_relevancy': 0.8097}

PER-SAMPLE SCORES
=======================================================
Sample 1: What is photosynthesis?
  faithfulness              1.000
  context_precision         1.000
  context_recall            1.000
  answer_relevancy          0.751
```

---

## Supported LLM Providers

| Provider | Free | API Key Variable | Default Model |
|----------|------|-----------------|---------------|
| Groq | Yes | `GROQ_API_KEY` | `llama-3.1-8b-instant` |
| Google Gemini | Yes (free tier) | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| OpenAI | No | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Ollama | Yes (local) | None needed | `llama3.2` |

### Groq (default — recommended)

```bash
# Get free key at https://console.groq.com
echo "GROQ_API_KEY=your_key" >> .env
```

### Google Gemini

```bash
# Get free key at https://aistudio.google.com/apikey
pip install google-genai
echo "GEMINI_API_KEY=your_key" >> .env
python -m playwright_rag.cli generate "login flow" --provider gemini
```

### Ollama (fully local, no internet)

```bash
# Install from https://ollama.com
ollama pull llama3.2
python -m playwright_rag.cli generate "login flow" --provider ollama
```

---

## Troubleshooting

**`Vector store is empty` error**

The `generate` command auto-ingests from `docs/` by default. Make sure your `docs/` folder exists and contains `.md`, `.txt`, or `.pdf` files.

```bash
ls docs/
```

**`No API key found for provider 'groq'` error**

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_key_here
```

**`ModuleNotFoundError: No module named 'langchain_groq'`**

```bash
pip install langchain langchain-community langchain-groq langchain-huggingface faiss-cpu sentence-transformers
```

**`browserType.launch: Executable doesn't exist`**

```bash
npx playwright install chromium
```

**Generated tests contain selectors not in my docs**

This means the retrieved chunks didn't contain the right information. Try:
- Adding more detail to your docs (explicit selectors, exact error messages)
- Increasing `--top-k` to retrieve more context: `--top-k 8`
- Making your query more specific

**Tests fail because the app URL is wrong**

Update `baseURL` in `playwright.config.ts`:

```typescript
use: {
  baseURL: 'https://www.amazon.in',
}
```
