# examples/custom_llm_and_load_data.py
#
# Shows how to:
#   - Load a dataset from a JSONL file
#   - Use a specific provider / model
#   - Run only selected metrics
#
# Run:
#   python examples/custom_llm_and_load_data.py


import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ragas_simple import evaluate, EvalDataset, SimpleLLM
from ragas_simple.metrics import faithfulness, answer_relevancy

# ---------------------------------------------------------------------------
# 1. Write sample data to a JSONL file
# ---------------------------------------------------------------------------

data = [
    {
        "user_input": "What is the speed of light?",
        "retrieved_contexts": [
            "The speed of light in a vacuum is approximately 299,792,458 m/s."
        ],
        "response": "The speed of light is approximately 300,000 km/s.",
        "reference": "The speed of light in a vacuum is 299,792,458 m/s.",
    },
    {
        "user_input": "What is the boiling point of water?",
        "retrieved_contexts": [
            "Water boils at 100°C (212°F) at standard atmospheric pressure."
        ],
        "response": "Water boils at 100°C or 212°F at sea level.",
        "reference": "The boiling point of water is 100°C at 1 atm pressure.",
    },
]

data_path = "sample_data.jsonl"
with open(data_path, "w") as f:
    for record in data:
        f.write(json.dumps(record) + "\n")
print(f"Data written to {data_path}")

# ---------------------------------------------------------------------------
# 2. Load from JSONL
# ---------------------------------------------------------------------------

dataset = EvalDataset.from_jsonl(data_path)
print(f"Loaded {len(dataset)} samples")

# ---------------------------------------------------------------------------
# 3. Create a custom LLM (Groq example — free)
#    Switch provider= to "gemini", "ollama", or "openai" as needed
# ---------------------------------------------------------------------------

llm = SimpleLLM(provider="gemini")   # or "groq", "ollama", "openai"
print(f"Using provider: {llm.provider}, model: {llm.model}")

# ---------------------------------------------------------------------------
# 4. Run only selected metrics
# ---------------------------------------------------------------------------

result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy],
    llm=llm,
)

# ---------------------------------------------------------------------------
# 5. Access scores programmatically
# ---------------------------------------------------------------------------

print("\nFaithfulness scores:", result.scores["faithfulness"])
print("Answer relevancy scores:", result.scores["answer_relevancy"])
print("\nAverages:", result.averages)
