"""Offline evaluation of the retriever: hit rate @k and mean reciprocal rank."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .retriever import TfidfRetriever


@dataclass
class RetrievalMetrics:
    n: int
    hit_at_1: float
    hit_at_3: float
    mrr: float
    misses: list[str]


def evaluate_retriever(
    retriever: TfidfRetriever, eval_df: pd.DataFrame, k: int = 3
) -> RetrievalMetrics:
    hits1 = hits_k = 0
    rr_total = 0.0
    misses: list[str] = []
    for question, expected in zip(eval_df["question"], eval_df["expected_id"], strict=True):
        ids = [r.chunk.id for r in retriever.search(question, top_k=k)]
        if ids[:1] == [expected]:
            hits1 += 1
        if expected in ids:
            hits_k += 1
            rr_total += 1 / (ids.index(expected) + 1)
        else:
            misses.append(question)
    n = len(eval_df)
    return RetrievalMetrics(n, hits1 / n, hits_k / n, rr_total / n, misses)
