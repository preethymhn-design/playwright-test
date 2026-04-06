# tests/test_metrics_logic.py
# Tests for pure metric math — no LLM or API key needed.
# Run: python tests/test_metrics_logic.py

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ragas_simple.metrics.base import BaseMetric
from ragas_simple.metrics.context_precision import ContextPrecision
from ragas_simple.metrics.answer_relevancy import AnswerRelevancy


# ---- BaseMetric ----

def test_mean_score_normal():
    m = BaseMetric()
    result = m.mean_score([1.0, 0.5, 0.0])
    assert abs(result - 0.5) < 1e-9

def test_mean_score_ignores_nan():
    m = BaseMetric()
    result = m.mean_score([1.0, float("nan"), 0.0])
    assert abs(result - 0.5) < 1e-9

def test_mean_score_all_nan():
    m = BaseMetric()
    assert math.isnan(m.mean_score([float("nan"), float("nan")]))

def test_score_sample_not_implemented():
    try:
        BaseMetric().score_sample(None)
        assert False, "Should raise NotImplementedError"
    except NotImplementedError:
        pass


# ---- Faithfulness scoring logic ----

def test_faithfulness_all_supported():
    verdicts = [{"verdict": 1}, {"verdict": 1}]
    supported = sum(1 for v in verdicts if v.get("verdict") == 1)
    assert supported / len(verdicts) == 1.0

def test_faithfulness_none_supported():
    verdicts = [{"verdict": 0}, {"verdict": 0}]
    supported = sum(1 for v in verdicts if v.get("verdict") == 1)
    assert supported / len(verdicts) == 0.0

def test_faithfulness_partial():
    verdicts = [{"verdict": 1}, {"verdict": 0}]
    supported = sum(1 for v in verdicts if v.get("verdict") == 1)
    assert abs(supported / len(verdicts) - 0.5) < 1e-9


# ---- ContextPrecision average precision ----

def test_ap_all_relevant():
    cp = ContextPrecision()
    assert cp._average_precision([1, 1, 1]) == 1.0

def test_ap_none_relevant():
    cp = ContextPrecision()
    assert cp._average_precision([0, 0, 0]) == 0.0

def test_ap_first_only():
    # Only first chunk relevant → AP = 1.0
    cp = ContextPrecision()
    assert cp._average_precision([1, 0, 0]) == 1.0

def test_ap_last_only():
    # Only last chunk relevant → AP = 1/3
    cp = ContextPrecision()
    assert abs(cp._average_precision([0, 0, 1]) - 1/3) < 1e-9

def test_ap_mixed():
    # verdicts=[1,0,1] → AP = (1.0 + 2/3) / 2
    cp = ContextPrecision()
    expected = (1.0 + 2/3) / 2
    assert abs(cp._average_precision([1, 0, 1]) - expected) < 1e-9


# ---- AnswerRelevancy cosine similarity ----

def test_cosine_identical():
    ar = AnswerRelevancy()
    vec = [1.0, 2.0, 3.0]
    assert abs(ar._cosine_similarity(vec, vec) - 1.0) < 1e-9

def test_cosine_orthogonal():
    ar = AnswerRelevancy()
    assert abs(ar._cosine_similarity([1.0, 0.0], [0.0, 1.0])) < 1e-9

def test_cosine_opposite():
    ar = AnswerRelevancy()
    assert abs(ar._cosine_similarity([1.0, 0.0], [-1.0, 0.0]) - (-1.0)) < 1e-9

def test_cosine_zero_vector():
    ar = AnswerRelevancy()
    assert ar._cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


# ---- Runner ----

if __name__ == "__main__":
    tests = [
        test_mean_score_normal, test_mean_score_ignores_nan,
        test_mean_score_all_nan, test_score_sample_not_implemented,
        test_faithfulness_all_supported, test_faithfulness_none_supported,
        test_faithfulness_partial,
        test_ap_all_relevant, test_ap_none_relevant, test_ap_first_only,
        test_ap_last_only, test_ap_mixed,
        test_cosine_identical, test_cosine_orthogonal,
        test_cosine_opposite, test_cosine_zero_vector,
    ]
    passed = 0
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed.")
