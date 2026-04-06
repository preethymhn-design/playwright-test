# ragas-simple

A beginner-friendly, simplified version of the Ragas LLM evaluation toolkit.

No complex type annotations, no abstract class maze — just clean, commented Python
that's easy to read and understand.

## What this does

Evaluates how good your RAG (Retrieval-Augmented Generation) pipeline is by
scoring it across four key metrics:

- **Faithfulness** — Is the answer grounded in the retrieved context?
- **Context Precision** — Are the retrieved contexts actually relevant?
- **Context Recall** — Did we retrieve all the context needed to answer?
- **Answer Relevancy** — Does the answer actually address the question?

## Free LLM providers (no paid key needed)

| Provider | Free tier | How to get a key |
|---|---|---|
| Google Gemini | 15 req/min, 1M tokens/day | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Groq | Generous free tier | [console.groq.com](https://console.groq.com) |
| Ollama | Unlimited (runs locally) | [ollama.com](https://ollama.com) — no key needed |

## Project layout

```
playwright-test/
├── ragas_simple/
│   ├── __init__.py          # Public API
│   ├── sample.py            # EvalSample — one question/answer pair
│   ├── dataset.py           # EvalDataset — list of samples + CSV/JSONL I/O
│   ├── llm.py               # SimpleLLM — wraps Gemini / Groq / Ollama / OpenAI
│   ├── evaluate.py          # evaluate() function + EvaluationResult
│   └── metrics/
│       ├── base.py               # BaseMetric (shared logic)
│       ├── faithfulness.py       # Faithfulness metric
│       ├── context_precision.py  # Context Precision metric
│       ├── context_recall.py     # Context Recall metric
│       └── answer_relevancy.py   # Answer Relevancy metric
├── examples/
│   ├── basic_rag_eval.py         # Full end-to-end example
│   └── custom_llm_and_load_data.py
├── tests/
│   ├── test_sample_and_dataset.py  # No API key needed
│   └── test_metrics_logic.py       # No API key needed
├── requirements.txt
├── Makefile
└── README.md
```

## Quick start

```bash
pip install -r requirements.txt

# Option A — Google Gemini (free, recommended)
export GEMINI_API_KEY="your-key"
python examples/basic_rag_eval.py

# Option B — Groq (free, fast)
export GROQ_API_KEY="your-key"
# edit basic_rag_eval.py: change provider="gemini" to provider="groq"

# Option C — Ollama (fully local, no key needed)
ollama pull llama3.2
# edit basic_rag_eval.py: change provider="gemini" to provider="ollama"
```

## Basic usage

```python
from ragas_simple import evaluate, EvalSample, EvalDataset
from ragas_simple.metrics import faithfulness, context_precision

samples = [
    EvalSample(
        user_input="What is the capital of France?",
        retrieved_contexts=["Paris is the capital and largest city of France."],
        response="The capital of France is Paris.",
        reference="Paris",
    )
]

dataset = EvalDataset(samples=samples)

# Uses Gemini by default (free) — change provider= for others
result = evaluate(dataset, metrics=[faithfulness, context_precision], provider="gemini")
print(result)
# {'faithfulness': 1.0, 'context_precision': 1.0}
```

## Run tests (no API key needed)

```bash
python tests/test_sample_and_dataset.py
python tests/test_metrics_logic.py

# or with pytest
python -m pytest tests/ -v
```
