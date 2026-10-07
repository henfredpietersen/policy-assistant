from pathlib import Path

import pandas as pd
import pytest

from policy_assistant.documents import load_chunks
from policy_assistant.evaluation import evaluate_retriever
from policy_assistant.retriever import TfidfRetriever

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def retriever(docs_dir):
    return TfidfRetriever().fit(load_chunks(docs_dir))


@pytest.mark.parametrize(
    "question, expected_title",
    [
        ("How do I change my beneficiary?", "Changing beneficiaries"),
        ("What happens if I miss a premium?", "Missed premiums and the grace period"),
        ("Can I cancel and get a refund in the cooling-off period?", "Cooling-off period"),
        ("How long does a claim take?", "How long a claim takes"),
    ],
)
def test_top_result_is_relevant(retriever, question, expected_title):
    assert retriever.search(question)[0].chunk.title == expected_title


def test_retrieval_quality_does_not_regress(retriever):
    """Guard rail: fail CI if a change makes retrieval noticeably worse."""
    metrics = evaluate_retriever(retriever, pd.read_csv(ROOT / "data" / "retrieval_eval.csv"))
    assert metrics.hit_at_3 >= 0.8
    assert metrics.mrr >= 0.7


def test_scores_are_sorted(retriever):
    scores = [r.score for r in retriever.search("premium increase", top_k=5)]
    assert scores == sorted(scores, reverse=True)


def test_unrelated_query_returns_nothing(retriever):
    assert retriever.search("xylophone quantum banana") == []


def test_search_before_fit_raises():
    with pytest.raises(RuntimeError):
        TfidfRetriever().search("anything")
