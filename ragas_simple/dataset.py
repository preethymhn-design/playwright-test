# dataset.py
#
# A dataset is a list of EvalSample objects with helpers to:
#   - iterate, index, and measure length
#   - save to / load from CSV or JSON Lines files


import csv
import json

from ragas_simple.sample import EvalSample


class EvalDataset:
    """
    A collection of EvalSample objects.

    Usage
    -----
        dataset = EvalDataset(samples=[sample1, sample2])
        len(dataset)          # number of samples
        dataset[0]            # first sample
        for s in dataset: ... # iterate

        dataset.to_csv("out.csv")
        dataset.to_jsonl("out.jsonl")
        EvalDataset.from_csv("data.csv")
        EvalDataset.from_jsonl("data.jsonl")
        EvalDataset.from_list([{"user_input": ..., ...}])
    """

    def __init__(self, samples):
        self.samples = samples

    # Python built-ins so the dataset behaves like a list
    def __len__(self):
        return len(self.samples)

    def __iter__(self):
        return iter(self.samples)

    def __getitem__(self, index):
        return self.samples[index]

    def __repr__(self):
        return f"EvalDataset(samples={len(self.samples)})"

    # ------------------------------------------------------------------ #
    # Save helpers                                                         #
    # ------------------------------------------------------------------ #

    def to_csv(self, path):
        """Save the dataset to a CSV file."""
        fieldnames = ["user_input", "retrieved_contexts", "response", "reference"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for sample in self.samples:
                row = sample.to_dict()
                # Serialize the list to JSON string so CSV can store it
                row["retrieved_contexts"] = json.dumps(row["retrieved_contexts"])
                writer.writerow(row)

    def to_jsonl(self, path):
        """Save the dataset to a JSON Lines file (one JSON object per line)."""
        with open(path, "w", encoding="utf-8") as f:
            for sample in self.samples:
                f.write(json.dumps(sample.to_dict(), ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------ #
    # Load helpers                                                         #
    # ------------------------------------------------------------------ #

    @classmethod
    def from_csv(cls, path):
        """Load a dataset from a CSV file previously saved with to_csv()."""
        samples = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contexts = json.loads(row["retrieved_contexts"])
                samples.append(EvalSample(
                    user_input=row["user_input"],
                    retrieved_contexts=contexts,
                    response=row["response"],
                    reference=row.get("reference"),
                ))
        return cls(samples=samples)

    @classmethod
    def from_jsonl(cls, path):
        """Load a dataset from a JSON Lines file."""
        samples = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                samples.append(EvalSample(
                    user_input=data["user_input"],
                    retrieved_contexts=data["retrieved_contexts"],
                    response=data["response"],
                    reference=data.get("reference"),
                ))
        return cls(samples=samples)

    @classmethod
    def from_list(cls, records):
        """Build a dataset from a plain list of dicts."""
        samples = [
            EvalSample(
                user_input=r["user_input"],
                retrieved_contexts=r["retrieved_contexts"],
                response=r["response"],
                reference=r.get("reference"),
            )
            for r in records
        ]
        return cls(samples=samples)
