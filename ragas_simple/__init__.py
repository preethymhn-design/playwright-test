# ragas_simple/__init__.py
# Public API — everything a user needs is importable from here.

from ragas_simple.sample import EvalSample
from ragas_simple.dataset import EvalDataset
from ragas_simple.llm import SimpleLLM
from ragas_simple.evaluate import evaluate, EvaluationResult

__all__ = ["evaluate", "EvaluationResult", "EvalSample", "EvalDataset", "SimpleLLM"]
