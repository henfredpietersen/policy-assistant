"""Score the retriever against a labelled set of questions.

Usage: python scripts/evaluate_retrieval.py
"""

from pathlib import Path

import pandas as pd

from policy_assistant.documents import load_chunks
from policy_assistant.evaluation import evaluate_retriever
from policy_assistant.retriever import TfidfRetriever

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    retriever = TfidfRetriever().fit(load_chunks(ROOT / "data" / "docs"))
    m = evaluate_retriever(retriever, pd.read_csv(ROOT / "data" / "retrieval_eval.csv"))
    print(f"Questions: {m.n}")
    print(f"Hit@1:     {m.hit_at_1:.2f}")
    print(f"Hit@3:     {m.hit_at_3:.2f}")
    print(f"MRR:       {m.mrr:.2f}")
    for q in m.misses:
        print(f"  missed: {q}")
