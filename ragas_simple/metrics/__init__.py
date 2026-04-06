# metrics/__init__.py
# Exports all metric instances for clean imports:
#   from ragas_simple.metrics import faithfulness, context_precision

from ragas_simple.metrics.faithfulness import faithfulness, Faithfulness
from ragas_simple.metrics.context_precision import context_precision, ContextPrecision
from ragas_simple.metrics.context_recall import context_recall, ContextRecall
from ragas_simple.metrics.answer_relevancy import answer_relevancy, AnswerRelevancy

# Pass this to evaluate() to run all four metrics at once
ALL_METRICS = [faithfulness, context_precision, context_recall, answer_relevancy]

__all__ = [
    "faithfulness", "Faithfulness",
    "context_precision", "ContextPrecision",
    "context_recall", "ContextRecall",
    "answer_relevancy", "AnswerRelevancy",
    "ALL_METRICS",
]
