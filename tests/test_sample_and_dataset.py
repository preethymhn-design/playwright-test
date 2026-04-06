# tests/test_sample_and_dataset.py
# Tests for EvalSample and EvalDataset — no API key needed.
# Run: python tests/test_sample_and_dataset.py

import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ragas_simple.sample import EvalSample
from ragas_simple.dataset import EvalDataset


def make_samples(n=2):
    return [
        EvalSample(
            user_input=f"Question {i}",
            retrieved_contexts=[f"Context {i}a", f"Context {i}b"],
            response=f"Answer {i}",
            reference=f"Reference {i}",
        )
        for i in range(n)
    ]


# ---- EvalSample tests ----

def test_sample_stores_fields():
    s = EvalSample("Q", ["C"], "A", "R")
    assert s.user_input == "Q"
    assert s.retrieved_contexts == ["C"]
    assert s.response == "A"
    assert s.reference == "R"

def test_sample_reference_optional():
    s = EvalSample("Q", ["C"], "A")
    assert s.reference is None

def test_sample_to_dict():
    s = EvalSample("Q", ["C"], "A", "R")
    d = s.to_dict()
    assert d == {"user_input": "Q", "retrieved_contexts": ["C"], "response": "A", "reference": "R"}


# ---- EvalDataset tests ----

def test_dataset_len():
    assert len(EvalDataset(samples=make_samples(3))) == 3

def test_dataset_iter():
    items = list(EvalDataset(samples=make_samples(2)))
    assert len(items) == 2
    assert all(isinstance(s, EvalSample) for s in items)

def test_dataset_index():
    ds = EvalDataset(samples=make_samples(3))
    assert ds[0].user_input == "Question 0"
    assert ds[2].user_input == "Question 2"

def test_dataset_from_list():
    ds = EvalDataset.from_list([{"user_input": "Q", "retrieved_contexts": ["C"], "response": "A"}])
    assert len(ds) == 1
    assert ds[0].user_input == "Q"

def test_csv_roundtrip():
    original = EvalDataset(samples=make_samples(2))
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        path = f.name
    try:
        original.to_csv(path)
        loaded = EvalDataset.from_csv(path)
        assert len(loaded) == len(original)
        for o, l in zip(original, loaded):
            assert o.user_input == l.user_input
            assert o.retrieved_contexts == l.retrieved_contexts
    finally:
        os.unlink(path)

def test_jsonl_roundtrip():
    original = EvalDataset(samples=make_samples(2))
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        path = f.name
    try:
        original.to_jsonl(path)
        loaded = EvalDataset.from_jsonl(path)
        assert len(loaded) == len(original)
        for o, l in zip(original, loaded):
            assert o.user_input == l.user_input
    finally:
        os.unlink(path)


# ---- Runner ----

if __name__ == "__main__":
    tests = [
        test_sample_stores_fields, test_sample_reference_optional, test_sample_to_dict,
        test_dataset_len, test_dataset_iter, test_dataset_index,
        test_dataset_from_list, test_csv_roundtrip, test_jsonl_roundtrip,
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
