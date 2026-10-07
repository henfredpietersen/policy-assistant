"""Vector search over document chunks using TF-IDF and cosine similarity."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .documents import Chunk


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


class TfidfRetriever:
    """Embeds chunks as TF-IDF vectors and returns the closest ones to a query.

    Character n-grams (3-5 chars within word boundaries) are used instead of
    whole words so that "beneficiary" still matches "beneficiaries" and
    "cancel" matches "cancelling" without a stemmer. TF-IDF keeps the project
    free to run (no API key); the fit/search interface matches what a
    dense-embedding retriever would expose, so one can be swapped in later.
    """

    def __init__(self, min_score: float = 0.15) -> None:
        self.min_score = min_score
        self._vectorizer = TfidfVectorizer(
            analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True
        )
        self._chunks: list[Chunk] = []
        self._matrix = None

    def fit(self, chunks: list[Chunk]) -> TfidfRetriever:
        if not chunks:
            raise ValueError("Cannot fit a retriever on zero chunks")
        self._chunks = list(chunks)
        corpus = [f"{c.title}. {c.text}" for c in self._chunks]
        self._matrix = self._vectorizer.fit_transform(corpus)
        return self

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if self._matrix is None:
            raise RuntimeError("Call fit() before search()")
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [
            SearchResult(self._chunks[i], float(scores[i]))
            for i in ranked
            if scores[i] >= self.min_score
        ]
