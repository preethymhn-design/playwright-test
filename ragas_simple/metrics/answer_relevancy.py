# metrics/answer_relevancy.py
#
# ANSWER RELEVANCY
# ----------------
# Measures whether the answer actually addresses the question.
#
# Score = mean cosine similarity between the original question and
#         questions reverse-engineered from the answer.
#
# If you can reconstruct the original question just by reading the answer,
# the answer is highly relevant.
#
# Two API calls per sample:
#   1. LLM call  — generate N questions from the answer
#   2. Embed call — compute cosine similarity with the original question
#
# NOTE: For Gemini/Groq/Ollama providers, embeddings use a separate
#       sentence-transformers model locally (no extra API key needed).
#       For OpenAI, it uses text-embedding-3-small.


import math
from ragas_simple.metrics.base import BaseMetric


class AnswerRelevancy(BaseMetric):
    """
    Checks whether the answer is relevant to the question.

    Requires: sample.user_input, sample.response

    Parameters
    ----------
    n_questions : int
        How many reverse questions to generate per answer. Default is 3.
    """

    name = "answer_relevancy"

    def __init__(self, n_questions=3):
        super().__init__()
        self.n_questions = n_questions
        self._embed_fn = None  # lazily initialised on first use

    def _get_embed_fn(self):
        """
        Return an embedding function appropriate for the current provider.

        - openai   → OpenAI text-embedding-3-small (API call)
        - others   → sentence-transformers all-MiniLM-L6-v2 (local, free)
        """
        if self._embed_fn is not None:
            return self._embed_fn

        if self.llm.provider == "openai":
            # Use OpenAI embeddings — reuse the same client
            def openai_embed(texts):
                resp = self.llm.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts,
                )
                return [item.embedding for item in resp.data]
            self._embed_fn = openai_embed

        else:
            # Use local sentence-transformers (free, works with any provider)
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "Install sentence-transformers for answer_relevancy with non-OpenAI providers:\n"
                    "  pip install sentence-transformers"
                )
            # Load a small, fast model (~90 MB download on first use)
            _model = SentenceTransformer("all-MiniLM-L6-v2")

            def local_embed(texts):
                # Returns a list of lists (one vector per text)
                return _model.encode(texts, convert_to_numpy=True).tolist()

            self._embed_fn = local_embed

        return self._embed_fn

    def _generate_questions(self, answer):
        """Ask the LLM to generate questions that the answer could be answering."""
        prompt = f"""Given the answer below, generate {self.n_questions} different
questions that this answer could be responding to.

Answer: {answer}

Return JSON: {{"questions": ["question 1", "question 2", ...]}}"""

        result = self.llm.ask_json(prompt)
        questions = result.get("questions", [])
        if not isinstance(questions, list):
            return []
        return [str(q) for q in questions if q][: self.n_questions]

    def _cosine_similarity(self, vec_a, vec_b):
        """Cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def score_sample(self, sample):
        # Step 1: generate reverse questions from the answer
        generated_questions = self._generate_questions(sample.response)
        if not generated_questions:
            return float("nan")

        # Step 2: embed original + generated questions
        embed = self._get_embed_fn()
        all_texts = [sample.user_input] + generated_questions
        embeddings = embed(all_texts)

        original_emb = embeddings[0]
        generated_embs = embeddings[1:]

        # Step 3: mean cosine similarity
        similarities = [
            self._cosine_similarity(original_emb, gen_emb)
            for gen_emb in generated_embs
        ]
        return sum(similarities) / len(similarities)


answer_relevancy = AnswerRelevancy()
