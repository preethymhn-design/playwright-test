# metrics/context_precision.py
#
# CONTEXT PRECISION
# -----------------
# Measures whether the retrieved context chunks are actually useful.
#
# Score = Average Precision (AP) over the ranked list of context chunks.
# Relevant chunks ranked higher → higher score.
#
# One LLM call per context chunk per sample.


from ragas_simple.metrics.base import BaseMetric


class ContextPrecision(BaseMetric):
    """
    Checks whether retrieved context chunks are relevant to the question.

    Requires: sample.user_input, sample.retrieved_contexts, sample.reference
    """

    name = "context_precision"

    def _is_context_useful(self, question, context_chunk, reference_answer):
        """
        Ask the LLM: was this context chunk useful for arriving at the answer?
        Returns 1 (useful) or 0 (not useful).
        """
        prompt = f"""Given the question, a context chunk, and the correct answer,
decide whether the context chunk was useful in arriving at the correct answer.

Question: {question}
Context chunk: {context_chunk}
Correct answer: {reference_answer}

Return JSON: {{"verdict": 1, "reason": "..."}}
verdict = 1 if useful, 0 if not."""

        result = self.llm.ask_json(prompt)
        try:
            return int(result.get("verdict", 0))
        except (TypeError, ValueError):
            return 0

    def _average_precision(self, verdicts):
        """
        Compute Average Precision from a list of binary verdicts (1/0).
        Rewards finding relevant chunks early in the list.

        Example: verdicts = [1, 0, 1]
          k=1: precision=1/1=1.0  (relevant)
          k=3: precision=2/3=0.67 (relevant)
          AP = (1.0 + 0.67) / 2 = 0.83
        """
        total_relevant = sum(verdicts)
        if total_relevant == 0:
            return 0.0

        cumulative_relevant = 0
        precision_sum = 0.0

        for k, verdict in enumerate(verdicts, start=1):
            if verdict == 1:
                cumulative_relevant += 1
                precision_sum += cumulative_relevant / k

        return precision_sum / total_relevant

    def score_sample(self, sample):
        if not sample.retrieved_contexts:
            return float("nan")
        if not sample.reference:
            raise ValueError(
                f"context_precision requires sample.reference. "
                f"Got None for: {sample.user_input!r}"
            )

        # Ask the LLM about each context chunk
        verdicts = [
            self._is_context_useful(sample.user_input, chunk, sample.reference)
            for chunk in sample.retrieved_contexts
        ]

        return self._average_precision(verdicts)


context_precision = ContextPrecision()
