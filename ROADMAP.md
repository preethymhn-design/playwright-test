# RAG Roadmap — From POC to Production & Agentic RAG

---

## Part 1 — What Needs to Change to Use This for a Real Application

The current system is a POC (Proof of Concept). It works, but it makes several assumptions that break down in a real project. Here is what needs to be addressed before using it on any specific application.

---

### 1.1 Persistent Vector Store

**Current state:** The FAISS index is built in memory every run and thrown away when the process ends. Every `npm run generate` re-reads and re-embeds all your docs from scratch.

**What to change:** Save the FAISS index to disk after the first build. Load it on subsequent runs. Only rebuild when docs change.

```python
# Save after ingestion
store._db.save_local("faiss_index/")

# Load on next run (skip re-ingestion)
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.load_local("faiss_index/", embeddings, allow_dangerous_deserialization=True)
```

**Why it matters:** For a real app with 50+ doc files, re-embedding on every run wastes 10–30 seconds. With persistence, subsequent runs start in under 1 second.

---

### 1.2 Real Application Selectors and URLs

**Current state:** The docs in `docs/` are manually written and may not match the actual application's DOM.

**What to change:** For a specific application, the docs must be written by someone who has inspected the actual HTML. Every selector (`input#ap_email`, `button.checkout-btn`) must be verified against the live app using browser DevTools.

**Practical approach:**
- Open the app in Chrome
- Right-click each element → Inspect
- Copy the selector and paste it into your `.md` doc
- Run `npm run generate` and verify the generated test uses that exact selector

**Why it matters:** A test with a wrong selector will always fail, even if the logic is correct.

---

### 1.3 Authentication Handling

**Current state:** The generator has no concept of login state. Tests that require authentication will fail because there is no session.

**What to change:** Add a `storageState` setup in `playwright.config.ts` that logs in once and reuses the session for all tests.

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    storageState: 'auth/session.json',  // reuse logged-in session
  },
  globalSetup: './auth/global-setup.ts',
});
```

```typescript
// auth/global-setup.ts
import { chromium } from '@playwright/test';

export default async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://www.amazon.in/ap/signin');
  await page.fill('input#ap_email', process.env.TEST_EMAIL!);
  await page.click('input#continue');
  await page.fill('input#ap_password', process.env.TEST_PASSWORD!);
  await page.click('input#signInSubmit');
  await page.context().storageState({ path: 'auth/session.json' });
  await browser.close();
}
```

**Why it matters:** Without this, every test that needs a logged-in user will fail at the first step.

---

### 1.4 Test Data Management

**Current state:** The generator hardcodes placeholder values like `test@example.com` and `password123`.

**What to change:** Use environment variables or a test data file for credentials, product IDs, and other dynamic values.

```typescript
// Use env vars in tests
await page.fill('input#ap_email', process.env.TEST_EMAIL!);
```

```env
# .env.test
TEST_EMAIL=your_test_account@gmail.com
TEST_PASSWORD=your_test_password
TEST_PRODUCT_ASIN=B08N5WRWNW
```

**Why it matters:** Hardcoded test data breaks when accounts change, products go out of stock, or tests run in different environments.

---

### 1.5 baseURL Configuration Per Environment

**Current state:** `playwright.config.ts` has a single hardcoded `baseURL`.

**What to change:** Support multiple environments (dev, staging, production) via environment variables.

```typescript
// playwright.config.ts
use: {
  baseURL: process.env.BASE_URL || 'https://www.amazon.in',
}
```

```bash
# Run against staging
BASE_URL=https://staging.amazon.in npm test

# Run against production
BASE_URL=https://www.amazon.in npm test
```

---

### 1.6 CI/CD Integration

**Current state:** Tests are run manually from the terminal.

**What to change:** Add a GitHub Actions workflow that generates and runs tests automatically on every pull request.

```yaml
# .github/workflows/test.yml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - uses: actions/setup-node@v3
        with: { node-version: '18' }
      - run: pip install -r requirements.txt
      - run: npm install
      - run: npx playwright install chromium
      - run: npm run generate -- "amazon login flow"
      - run: npm test
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
```

---

### 1.7 Smarter Chunking for Structured Docs

**Current state:** `RecursiveCharacterTextSplitter` splits by character count, which can cut a selector list in half.

**What to change:** Use a header-aware splitter that keeps each section of a markdown doc together as one chunk.

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "page"),
    ("##", "section"),
    ("###", "subsection"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
```

**Why it matters:** A chunk that contains `input#ap_email` alongside its section heading "Email / Phone Step" gives the LLM much better context than a chunk that starts mid-sentence.

---

### 1.8 Summary of POC → Production Changes

| Area | POC (current) | Production (needed) |
|------|--------------|---------------------|
| Vector store | In-memory, rebuilt every run | Persisted to disk, rebuilt only on doc changes |
| Selectors | Manually written, may be wrong | Verified against live app DOM |
| Authentication | Not handled | `storageState` global setup |
| Test data | Hardcoded placeholders | Environment variables |
| Environments | Single hardcoded URL | `BASE_URL` env var per environment |
| CI/CD | Manual terminal runs | GitHub Actions on every PR |
| Chunking | Character-based | Header-aware markdown splitting |

---

## Part 2 — From Traditional RAG to Agentic RAG

### What is the difference?

**Traditional RAG** (what this project currently does):

```
User query → Retrieve chunks → Send to LLM → Get answer
```

It is a single, linear, one-shot pipeline. The LLM gets the context once and produces one output. It cannot ask follow-up questions, check its own work, use tools, or decide to look for more information.

**Agentic RAG:**

```
User query → Agent thinks → Decides what to do → Uses tools → Checks result
           → Decides to do more → Uses more tools → Checks again
           → Decides it is done → Returns final answer
```

The LLM becomes an agent — it has a loop, it has tools, and it decides what to do next at each step. It can retrieve information multiple times, validate its own output, browse the web, run code, and more.

---

### Step 1 — Give the Agent Tools

In traditional RAG, retrieval is hardwired. The system always retrieves exactly 5 chunks and sends them to the LLM. The LLM has no say in this.

In agentic RAG, retrieval becomes a **tool** that the agent can choose to call — or not call, or call multiple times with different queries.

**Current (traditional):**
```python
# generator.py — hardwired retrieval
results = self.store.search(query, top_k=5)
# always retrieves 5 chunks, always from the same store
```

**Agentic version — retrieval as a tool:**
```python
from langchain.tools import tool
from langchain_community.vectorstores import FAISS

@tool
def search_docs(query: str) -> str:
    """Search the documentation for information about a specific UI element or flow."""
    results = vector_store.search(query, top_k=3)
    return "\n\n".join(r["text"] for r in results)

@tool
def search_by_selector(selector: str) -> str:
    """Find documentation that mentions a specific CSS selector."""
    results = vector_store.search(f"selector {selector}", top_k=3)
    return "\n\n".join(r["text"] for r in results)
```

Now the agent can call `search_docs("login error messages")` and then separately call `search_docs("login page URL")` — two targeted searches instead of one broad one.

---

### Step 2 — Add a ReAct Loop (Reason + Act)

The ReAct pattern gives the agent a think-act-observe loop. At each step the agent:
1. **Thinks** — reasons about what it knows and what it needs
2. **Acts** — calls a tool
3. **Observes** — reads the tool's output
4. Repeats until it has enough information to answer

**Example of what the agent's internal monologue looks like:**

```
User: "Generate tests for the Amazon login page"

Agent thinks: I need to find the login page URL and its selectors.
Agent acts:   search_docs("amazon login page URL")
Agent observes: "Login page: https://www.amazon.in/ap/signin"

Agent thinks: Good. Now I need the input selectors.
Agent acts:   search_docs("login page input selectors email password")
Agent observes: "Email input: input#ap_email, Password: input#ap_password"

Agent thinks: I also need the error messages for negative test cases.
Agent acts:   search_docs("login error messages wrong password")
Agent observes: "Wrong password: 'Your password is incorrect'"

Agent thinks: I have enough. I can now write the tests.
Agent acts:   generate_playwright_test(url, selectors, error_messages)
Agent observes: [TypeScript code]

Agent thinks: Done.
```

**Implementation using LangChain:**

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_groq import ChatGroq
from langchain import hub

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
tools = [search_docs, search_by_selector, generate_playwright_test]

# Pull the standard ReAct prompt from LangChain hub
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "Generate tests for the Amazon login page"})
```

---

### Step 3 — Add a Test Validation Tool

Traditional RAG generates the test and stops. It has no idea if the generated TypeScript is valid.

An agent can validate its own output by running a tool that checks the TypeScript syntax.

```python
import subprocess

@tool
def validate_typescript(code: str) -> str:
    """
    Validate that the generated TypeScript compiles without errors.
    Returns 'VALID' or the compiler error message.
    """
    with open("_temp_check.ts", "w") as f:
        f.write(code)
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--strict", "_temp_check.ts"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return "VALID"
    return f"ERRORS:\n{result.stderr}"
```

Now the agent's loop becomes:

```
Agent generates test code
Agent calls validate_typescript(code)
Agent observes: "ERRORS: Property 'toHaveText' does not exist..."
Agent thinks: I used the wrong assertion. Let me fix it.
Agent generates corrected code
Agent calls validate_typescript(corrected_code)
Agent observes: "VALID"
Agent thinks: Done.
```

This is self-healing — the agent fixes its own mistakes before saving the file.

---

### Step 4 — Add a Live Page Inspection Tool

Traditional RAG relies entirely on your manually written docs. If a selector is wrong in the docs, the test will be wrong.

An agent can use a Playwright tool to inspect the live page and verify selectors exist before writing the test.

```python
from playwright.sync_api import sync_playwright

@tool
def verify_selector_exists(url: str, selector: str) -> str:
    """
    Open the given URL in a browser and check if the selector exists on the page.
    Returns 'EXISTS' or 'NOT FOUND'.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        element = page.query_selector(selector)
        browser.close()
        return "EXISTS" if element else "NOT FOUND"
```

Agent usage:

```
Agent thinks: The docs say the email input is input#ap_email. Let me verify.
Agent calls:  verify_selector_exists("https://www.amazon.in/ap/signin", "input#ap_email")
Agent observes: "EXISTS"
Agent thinks: Good. I can use this selector in the test.

Agent thinks: The docs say the submit button is input#signInSubmit. Let me verify.
Agent calls:  verify_selector_exists("https://www.amazon.in/ap/signin", "input#signInSubmit")
Agent observes: "NOT FOUND"
Agent thinks: That selector is wrong. Let me search for the correct one.
Agent calls:  search_docs("sign in button selector")
...
```

---

### Step 5 — Add Memory Across Sessions

Traditional RAG has no memory. Every run starts fresh. The agent does not know what tests it generated yesterday or what selectors it already verified.

Agentic RAG can use a memory store to remember:
- Which selectors have been verified as correct
- Which tests have already been generated
- Which flows have been tested and which have not

```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=2000,
    return_messages=True
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)

# First run
executor.invoke({"input": "Generate tests for the login page"})

# Second run — agent remembers the login tests were already done
executor.invoke({"input": "Generate tests for the checkout page"})
# Agent: "I already generated login tests. The checkout page needs shipping and payment tests."
```

---

### Step 6 — Multi-Agent Architecture

For a large application, a single agent trying to do everything becomes slow and unreliable. The solution is multiple specialised agents that work together.

```
Orchestrator Agent
├── Doc Analysis Agent     — reads docs, extracts all selectors and flows
├── Test Planning Agent    — decides which test cases are needed
├── Test Writing Agent     — writes the TypeScript for each test case
├── Validation Agent       — checks TypeScript syntax and selector existence
└── Coverage Agent         — checks which flows are not yet tested
```

**Example flow:**

```
User: "Generate a full test suite for Amazon checkout"

Orchestrator → Doc Analysis Agent:
  "Extract all selectors and flows from amazon_checkout_spec.md"
  Returns: {url: "/checkout/shipping", selectors: [...], flows: [...]}

Orchestrator → Test Planning Agent:
  "Given these flows, what test cases do we need?"
  Returns: ["happy path", "invalid card", "expired card", "empty cart", ...]

Orchestrator → Test Writing Agent (runs in parallel for each test case):
  "Write a test for: invalid card number"
  Returns: TypeScript for that one test

Orchestrator → Validation Agent:
  "Validate all generated tests"
  Returns: ["VALID", "VALID", "ERROR in test 3: ...", ...]

Orchestrator → Test Writing Agent:
  "Fix test 3: ..."
  Returns: corrected TypeScript

Orchestrator → Coverage Agent:
  "Which flows in the docs are not yet covered by tests?"
  Returns: ["order confirmation email", "address validation"]
```

---

### Summary — Traditional RAG vs Agentic RAG

| Capability | Traditional RAG (current) | Agentic RAG |
|-----------|--------------------------|-------------|
| Retrieval | Fixed — always 5 chunks, one query | Dynamic — agent decides when and what to search |
| Self-correction | None — output is final | Agent validates and fixes its own output |
| Selector verification | None — trusts docs blindly | Agent checks selectors against live page |
| Memory | None — starts fresh every run | Remembers previous runs and decisions |
| Multi-step reasoning | None — one prompt, one response | ReAct loop — thinks, acts, observes, repeats |
| Parallelism | Sequential | Multiple agents work in parallel |
| Error handling | Fails silently | Agent detects errors and retries with corrections |
| Coverage tracking | None | Coverage agent tracks what is and isn't tested |

---

### Recommended Migration Path

If you want to evolve this POC toward agentic RAG, do it in stages:

**Stage 1 (1–2 days):** Add TypeScript validation tool. The agent generates a test, validates it, and fixes syntax errors before saving. This alone eliminates most broken test files.

**Stage 2 (2–3 days):** Convert retrieval to a tool. Let the agent call `search_docs()` multiple times with different queries instead of one fixed retrieval. This improves context quality significantly.

**Stage 3 (3–5 days):** Add the ReAct loop using `create_react_agent`. The agent now reasons about what information it needs before writing tests.

**Stage 4 (1 week):** Add live selector verification. The agent checks that every selector it uses actually exists on the page before writing the test.

**Stage 5 (ongoing):** Add memory, coverage tracking, and multi-agent orchestration as the test suite grows.
