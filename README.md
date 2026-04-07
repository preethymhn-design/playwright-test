# Playwright RAG Test Generator

A RAG (Retrieval-Augmented Generation) pipeline that reads your documentation, understands your application's UI, and generates executable Playwright TypeScript test cases — grounded strictly in what your docs describe.

No hallucination. Every selector, URL, and assertion in the generated tests comes directly from your documentation.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Writing Good Documentation](#writing-good-documentation)
8. [Generating Tests](#generating-tests)
9. [Running Tests](#running-tests)
10. [npm Scripts Reference](#npm-scripts-reference)
11. [Python CLI Reference](#python-cli-reference)
12. [RAG Evaluation](#rag-evaluation)
13. [Supported LLM Providers](#supported-llm-providers)
14. [Troubleshooting](#troubleshooting)

---

## How It Works

The system follows an 8-step pipeline every time you run `npm run generate`:

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
         Each chunk is converted to a 384-dimensional vector
         Runs entirely on your local machine — no API key needed
         Model is downloaded once (~90MB) and cached

Step 5 — Vector Store (FAISS in-memory index)
         All chunk vectors are stored in a FAISS index
         Enables fast cosine similarity search across all your docs

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

## Project Structure

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
