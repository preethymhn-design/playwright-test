# generator.py
# LangChain RAG chain: retrieves context from FAISS and generates Playwright tests via Groq.

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from ragas_simple.llm import SimpleLLM

SYSTEM_PROMPT = """You are an expert Playwright test automation engineer.
Output ONLY raw TypeScript code. No markdown fences, no prose, no explanations, no backticks.
The output must be a valid, directly executable .spec.ts file.
Use @playwright/test imports. Write clean Page Object Model style tests with descriptive names, assertions, and inline comments.
Base your tests ONLY on the provided context."""

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """Generate Playwright TypeScript test cases for the following query using the provided context.

QUERY: {query}

CONTEXT:
{context}

Rules:
- Output ONLY valid TypeScript. No markdown, no backticks, no explanation text.
- Start directly with: import {{ test, expect }} from '@playwright/test';
- Include a test.describe block with multiple test cases
- Cover happy path and all edge cases mentioned in the context
- Use proper locators from the context (selectors, URLs, error messages)
- Add short inline comments per step
"""),
])


class TestGenerator:
    """
    Generates Playwright test cases using a LangChain RAG chain.

    Usage:
        gen = TestGenerator(vector_store)
        tests = gen.generate("login with invalid credentials")
        print(tests)
    """

    def __init__(self, vector_store, llm=None, top_k=5, provider="groq"):
        self.store = vector_store
        self.top_k = top_k

        # Build LangChain LLM — use ChatGroq if provider is groq, else fall back to SimpleLLM
        if llm is None:
            simple = SimpleLLM(provider=provider)
            if provider == "groq":
                self.lc_llm = ChatGroq(
                    api_key=simple.api_key,
                    model=simple.model,
                    temperature=0,
                )
                self._use_chain = True
            else:
                # Non-groq providers: use SimpleLLM directly (no LangChain wrapper needed)
                self.simple_llm = simple
                self._use_chain = False
        else:
            # Caller passed a SimpleLLM directly
            self.simple_llm = llm
            self._use_chain = False

    def _build_chain(self):
        """Build the LangChain LCEL retrieval chain."""
        retriever = self.store.as_retriever(top_k=self.top_k)

        def format_docs(docs):
            return "\n\n---\n\n".join(
                f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}"
                for d in docs
            )

        chain = (
            {"context": retriever | format_docs, "query": RunnablePassthrough()}
            | PROMPT_TEMPLATE
            | self.lc_llm
            | StrOutputParser()
        )
        return chain

    def _clean_output(self, text: str) -> str:
        """Strip markdown code fences and any prose before/after the TypeScript block."""
        import re
        # If there's a ```typescript or ``` block, extract just its contents
        fenced = re.search(r"```(?:typescript|ts)?\s*\n(.*?)```", text, re.DOTALL)
        if fenced:
            return fenced.group(1).strip()
        # Strip any leading prose lines before the first import/test statement
        lines = text.splitlines()
        start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("test") or stripped.startswith("//"):
                start = i
                break
        return "\n".join(lines[start:]).strip()

    def generate(self, query, top_k=None):
        """
        Retrieve relevant context and generate Playwright tests for the given query.

        Returns str — generated Playwright TypeScript test code.
        """
        if self._use_chain:
            chain = self._build_chain()
            return self._clean_output(chain.invoke(query))
        else:
            # Fallback: manual retrieval + SimpleLLM
            results = self.store.search(query, top_k=top_k or self.top_k)
            if not results:
                return "// No relevant context found. Please ingest documents first."
            context = "\n\n---\n\n".join(
                f"[Source: {r['metadata'].get('source','unknown')}]\n{r['text']}"
                for r in results
            )
            prompt = PROMPT_TEMPLATE.format_messages(query=query, context=context)
            full_prompt = "\n".join(m.content for m in prompt)
            return self._clean_output(self.simple_llm.ask(full_prompt, system_prompt=SYSTEM_PROMPT))

    def generate_with_context(self, query, top_k=None):
        """
        Same as generate() but also returns the retrieved context chunks.

        Returns dict: { "tests": str, "context": list[dict] }
        """
        k = top_k or self.top_k
        context_chunks = self.store.search(query, top_k=k)
        tests = self.generate(query, top_k=k)
        return {"tests": tests, "context": context_chunks}
