import sys, os, math
sys.path.insert(0, '.')
from ragas_simple import evaluate, EvalSample, EvalDataset
from ragas_simple.metrics import faithfulness, context_precision, context_recall, answer_relevancy

samples = [
    EvalSample(
        user_input="What is photosynthesis?",
        retrieved_contexts=[
            "Photosynthesis is the process by which green plants convert light energy into chemical energy stored in glucose.",
            "During photosynthesis, plants absorb CO2 and water, producing glucose and oxygen.",
        ],
        response="Photosynthesis is the process plants use to convert sunlight into food, taking in CO2 and water and releasing oxygen.",
        reference="Photosynthesis is a biological process where plants convert light energy into chemical energy (glucose) using CO2 and water, releasing oxygen.",
    ),
    EvalSample(
        user_input="Who invented the telephone?",
        retrieved_contexts=[
            "Alexander Graham Bell is widely credited with inventing the telephone. He was awarded the first patent for the telephone in 1876.",
        ],
        response="The telephone was invented by Alexander Graham Bell, who received the first patent for it in 1876.",
        reference="Alexander Graham Bell invented the telephone and received the first patent in 1876.",
    ),
    EvalSample(
        user_input="What causes rainbows?",
        retrieved_contexts=[
            "The water cycle describes how water evaporates, rises, condenses into clouds, and falls as precipitation.",
        ],
        response="Rainbows are caused by refraction, dispersion, and reflection of sunlight inside water droplets.",
        reference="Rainbows form when sunlight enters water droplets, is refracted and dispersed into colors, and reflects back out at an angle.",
    ),
]

dataset = EvalDataset(samples=samples)
print(f"Dataset: {len(dataset)} samples\n")

result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, context_precision, context_recall, answer_relevancy],
    provider="groq",
)

print("\nPER-SAMPLE SCORES")
print("=" * 55)
for i, row in enumerate(result.to_list()):
    print(f"\nSample {i+1}: {row['user_input']}")
    for m in ["faithfulness", "context_precision", "context_recall", "answer_relevancy"]:
        score = row.get(m)
        if score is not None:
            s = f"{score:.3f}" if not math.isnan(score) else "nan"
            print(f"  {m:<25} {s}")

result.to_csv("eval_results.csv")
