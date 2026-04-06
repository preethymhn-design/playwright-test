# metrics/base.py
#
# Every metric inherits from BaseMetric.
# Subclasses only need to implement score_sample() —
# the loop over the full dataset is handled here.


import math


class BaseMetric:
    """
    Base class for all evaluation metrics.

    To create a new metric, subclass this and implement score_sample().

    Attributes
    ----------
    name : str       — shown in results, e.g. "faithfulness"
    llm  : SimpleLLM — injected by evaluate() before scoring starts
    """

    name = "base_metric"

    def __init__(self):
        # The LLM is set by evaluate() — metrics don't create it themselves
        self.llm = None

    def score_sample(self, sample):
        """
        Score a single EvalSample. Must be overridden by subclasses.

        Returns
        -------
        float  — 0.0 to 1.0, or float('nan') if the sample can't be scored
        """
        raise NotImplementedError(
            f"Metric '{self.name}' must implement score_sample(sample)."
        )

    def score_dataset(self, dataset, show_progress=True):
        """
        Score every sample in the dataset.

        Returns
        -------
        list of float  — one score per sample
        """
        scores = []
        total = len(dataset)

        for i, sample in enumerate(dataset):
            if show_progress:
                print(f"  {self.name}  [{i + 1}/{total}]", end="\r")
            try:
                score = self.score_sample(sample)
            except Exception as exc:
                print(f"\n  Warning: {self.name} failed on sample {i}: {exc}")
                score = float("nan")
            scores.append(score)

        if show_progress:
            print()  # newline after progress counter

        return scores

    def mean_score(self, scores):
        """Average of a list of scores, ignoring NaN values."""
        valid = [s for s in scores if not math.isnan(s)]
        if not valid:
            return float("nan")
        return sum(valid) / len(valid)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"
