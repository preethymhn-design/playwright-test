# sample.py
#
# Defines what a single "evaluation sample" looks like.
# One sample = one question, its retrieved context chunks,
# the LLM's answer, and optionally a reference (ground truth).


class EvalSample:
    """
    Represents one evaluation example.

    Fields
    ------
    user_input        : The question the user asked.
    retrieved_contexts: A list of text chunks your RAG pipeline retrieved.
    response          : The answer your LLM generated.
    reference         : (optional) The correct / expected answer.
                        Needed by context_precision and context_recall.

    Example
    -------
        sample = EvalSample(
            user_input="What is photosynthesis?",
            retrieved_contexts=["Photosynthesis is the process by which plants..."],
            response="Photosynthesis is how plants make food from sunlight.",
            reference="Photosynthesis converts light energy into chemical energy.",
        )
    """

    def __init__(self, user_input, retrieved_contexts, response, reference=None):
        self.user_input = user_input
        self.retrieved_contexts = retrieved_contexts or []
        self.response = response
        self.reference = reference  # ground-truth answer (optional)

    def to_dict(self):
        """Return the sample as a plain dictionary."""
        return {
            "user_input": self.user_input,
            "retrieved_contexts": self.retrieved_contexts,
            "response": self.response,
            "reference": self.reference,
        }

    def __repr__(self):
        return f"EvalSample(user_input={self.user_input!r}, response={self.response!r})"
