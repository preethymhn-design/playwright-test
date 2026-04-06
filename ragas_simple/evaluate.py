# evaluate.py
#
# The main entry point. Call evaluate() with your dataset and metrics.
#
# Usage
# -----
#   from ragas_simple import evaluate
#   result = evaluate(dataset, metrics=[faithfulness, context_precision])
#   print(result)
#   # {'faithfulness': 0.92, 'context_precision': 0.87}


import math
from ragas_simple.llm import SimpleLLM


class EvaluationResult:
    """
    Holds the output of an evaluate() call.

    Attributes
    ----------
    scores   : dict  — { metric_name: [score_0, score_1, ...] }
    averages : dict  — { metric_name: mean_score }
    dataset  : EvalDataset

    Usage
    -----
        result.scores["faithfulness"]    # list of per-sample scores
        result.averages["faithfulness"]  # mean score
        result.to_list()                 # list of dicts (inputs + scores)
        result.to_csv("results.csv")     # save to file
        print(result)                    # shows averages
    """

    def __init__(self, scores, dataset):
        self.scores = scores
        self.dataset = dataset

        # Compute mean for each metric, ignoring NaN
        self.averages = {}
        for name, metric_scores in scores.items():
            valid = [s for s in metric_scores if not math.isnan(s)]
            self.averages[name] = sum(valid) / len(valid) if valid else float("nan")

    def to_list(self):
        """Return results as a list of dicts — one dict per sample with scores attached."""
        rows = []
        for i, sample in enumerate(self.dataset):
            row = sample.to_dict()
            for metric_name, metric_scores in self.scores.items():
                row[metric_name] = metric_scores[i]
            rows.append(row)
        return rows

    def to_csv(self, path):
        """Save the full results (inputs + scores) to a CSV file."""
        import csv, json
        rows = self.to_list()
        if not rows:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            for row in rows:
                if isinstance(row.get("retrieved_contexts"), list):
                    row["retrieved_contexts"] = json.dumps(row["retrieved_contexts"])
                writer.writerow(row)
        print(f"Results saved to {path}")

    def __repr__(self):
        parts = []
        for name, avg in self.averages.items():
            parts.append(f"'{name}': {avg:.4f}" if not math.isnan(avg) else f"'{name}': nan")
        return "{" + ", ".join(parts) + "}"


def evaluate(dataset, metrics=None, llm=None, provider="gemini", model=None, show_progress=True):
    """
    Evaluate a dataset using the given metrics.

    Parameters
    ----------
    dataset       : EvalDataset
    metrics       : list of BaseMetric — defaults to all four core metrics
    llm           : SimpleLLM — created automatically if not provided
    provider      : str — "gemini" (free), "groq" (free), "ollama" (local), "openai"
    model         : str — model name override (uses provider default if None)
    show_progress : bool — print progress while scoring

    Returns
    -------
    EvaluationResult

    Example
    -------
        # Free — uses Gemini by default (set GEMINI_API_KEY)
        result = evaluate(dataset)

        # Free — use Groq (set GROQ_API_KEY)
        result = evaluate(dataset, provider="groq")

        # Free — fully local Ollama (no API key)
        result = evaluate(dataset, provider="ollama")
    """
    if metrics is None:
        from ragas_simple.metrics import ALL_METRICS
        metrics = ALL_METRICS

    # Create LLM if not provided
    if llm is None:
        kwargs = {"provider": provider}
        if model:
            kwargs["model"] = model
        llm = SimpleLLM(**kwargs)

    # Inject the LLM into every metric
    for metric in metrics:
        metric.llm = llm

    # Run each metric over the whole dataset
    all_scores = {}
    for metric in metrics:
        if show_progress:
            print(f"\nRunning metric: {metric.name}")
        all_scores[metric.name] = metric.score_dataset(dataset, show_progress=show_progress)

    result = EvaluationResult(scores=all_scores, dataset=dataset)

    if show_progress:
        print("\nEvaluation complete.")
        print(result)

    return result
