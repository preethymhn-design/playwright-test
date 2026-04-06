# metrics/context_recall.py
#
# CONTEXT RECALL
# --------------
# Measures whether the retrieved context covers the reference answer.
#
# Score = attributed_sentences / total_sentences_in_reference
#
# 1.0 = context fully covers the reference answer
# 0.0 = context is missing all the needed information
#
# One LLM call per sample.


from ragas_simple.metrics.base import BaseMetric


class ContextRecall(BaseMetric):
    """
    Checks whether the retrieved context covers the reference answer.

    Requires: sample.user_input, sample.retrieved_contexts, sample.reference
    """

    name = "context_recall"

    def _classify_sentences(self, question, context, reference_answer):
        """
        Ask the LLM to classify each sentence in the reference answer:
        can it be attributed to the context, or not?

        Returns a list of dicts:
            [{"sentence": "...", "attributed": 1, "reason": "..."}, ...]
        attributed = 1 → context supports this sentence
        attributed = 0 → context does NOT support this sentence
        """
        prompt = f"""You are given a question, a context, and a reference answer.
For each sentence in the reference answer, decide whether it can be attributed
to (supported by) the given context.

Question: {question}

Context:
{context}

Reference answer: {reference_answer}

Return JSON:
{{
  "classifications": [
    {{"sentence": "...", "attributed": 1, "reason": "..."}},
    {{"sentence": "...", "attributed": 0, "reason": "..."}}
  ]
}}
attributed = 1 if the sentence is supported by the context, 0 if not."""

        result = self.llm.ask_json(prompt)
        classifications = result.get("classifications", [])
        if not isinstance(classifications, list):
            return []
        return classifications

    def score_sample(self, sample):
        if not sample.reference:
            raise ValueError(
                f"context_recall requires sample.reference. "
                f"Got None for: {sample.user_input!r}"
            )
        if not sample.retrieved_contexts:
            return float("nan")

        context = "\n".join(sample.retrieved_contexts)
        classifications = self._classify_sentences(
            sample.user_input, context, sample.reference
        )

        if not classifications:
            return float("nan")

        total = len(classifications)
        attributed = sum(
            1 for c in classifications
            if isinstance(c, dict) and c.get("attributed") == 1
        )
        return attributed / total if total > 0 else float("nan")


context_recall = ContextRecall()
