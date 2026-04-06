# metrics/faithfulness.py
#
# FAITHFULNESS
# ------------
# Measures whether the LLM's answer is grounded in the retrieved context.
#
# Score = supported_statements / total_statements
#
# 1.0 = every claim in the answer is backed by the context (no hallucinations)
# 0.0 = none of the claims are supported
#
# Two LLM calls per sample:
#   Step 1 — Break the answer into individual factual statements
#   Step 2 — For each statement ask: "Can this be inferred from the context?"


import math
from ragas_simple.metrics.base import BaseMetric


class Faithfulness(BaseMetric):
    """
    Checks whether the answer is faithful to the retrieved context.

    Requires: sample.user_input, sample.response, sample.retrieved_contexts
    """

    name = "faithfulness"

    def _extract_statements(self, question, answer):
        """
        Step 1: Ask the LLM to decompose the answer into atomic statements.
        Returns a list of statement strings.
        """
        prompt = f"""Given the question and answer below, break the answer into
simple, standalone factual statements. Each statement must be self-contained
(replace pronouns like "he/she/it" with the actual noun).

Question: {question}
Answer: {answer}

Return JSON: {{"statements": ["Statement one.", "Statement two."]}}"""

        result = self.llm.ask_json(prompt)
        statements = result.get("statements", [])
        if not isinstance(statements, list):
            return []
        return [str(s) for s in statements if s]

    def _verify_statements(self, context, statements):
        """
        Step 2: Ask the LLM whether each statement can be inferred from context.
        Returns a list of dicts: [{"statement": "...", "verdict": 1, "reason": "..."}]
        verdict 1 = supported, 0 = not supported
        """
        statements_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(statements))

        prompt = f"""You are given a context and a list of statements.
For each statement decide if it can be directly inferred from the context.

Context:
{context}

Statements:
{statements_text}

Return JSON:
{{
  "verdicts": [
    {{"statement": "...", "verdict": 1, "reason": "..."}},
    {{"statement": "...", "verdict": 0, "reason": "..."}}
  ]
}}
verdict = 1 if supported by context, 0 if not."""

        result = self.llm.ask_json(prompt)
        verdicts = result.get("verdicts", [])
        if not isinstance(verdicts, list):
            return []
        return verdicts

    def score_sample(self, sample):
        # Combine all context chunks into one block
        context = "\n".join(sample.retrieved_contexts)

        # Step 1: decompose answer into statements
        statements = self._extract_statements(sample.user_input, sample.response)
        if not statements:
            return float("nan")

        # Step 2: verify each statement against context
        verdicts = self._verify_statements(context, statements)
        if not verdicts:
            return float("nan")

        # Score = supported / total
        supported = sum(
            1 for v in verdicts
            if isinstance(v, dict) and v.get("verdict") == 1
        )
        return supported / len(statements)


# Pre-built instance — use directly:
#   from ragas_simple.metrics import faithfulness
faithfulness = Faithfulness()
