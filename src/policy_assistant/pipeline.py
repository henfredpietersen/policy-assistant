"""Wires the intent classifier, retriever and generator into one RAG pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from .documents import load_chunks
from .generator import ExtractiveGenerator, make_generator
from .intent import IntentClassifier
from .retriever import TfidfRetriever

log = logging.getLogger(__name__)


@dataclass
class Answer:
    question: str
    answer: str
    intent: str | None
    intent_confidence: float | None
    sources: list[dict] = field(default_factory=list)
    generator: str = "extractive"


class RAGPipeline:
    def __init__(self, retriever, generator, classifier: IntentClassifier | None = None) -> None:
        self.retriever, self.generator, self.classifier = retriever, generator, classifier

    @classmethod
    def from_paths(cls, docs_dir: str | Path, model_path: str | Path | None = None) -> RAGPipeline:
        retriever = TfidfRetriever().fit(load_chunks(docs_dir))
        classifier = None
        if model_path and Path(model_path).exists():
            classifier = IntentClassifier.load(model_path)
        return cls(retriever, make_generator(), classifier)

    def ask(self, question: str, top_k: int = 3) -> Answer:
        question = question.strip()
        if not question:
            raise ValueError("Question must not be empty")

        intent, confidence = (None, None)
        if self.classifier:
            intent, confidence = self.classifier.predict(question)

        results = self.retriever.search(question, top_k=top_k)
        try:
            text = self.generator.generate(question, results)
            gen_name = self.generator.name
        except Exception:  # LLM outage should not take the service down
            log.exception("Generator failed, falling back to extractive answer")
            text = ExtractiveGenerator().generate(question, results)
            gen_name = "extractive-fallback"

        return Answer(
            question=question,
            answer=text,
            intent=intent,
            intent_confidence=round(confidence, 3) if confidence is not None else None,
            sources=[
                {"id": r.chunk.id, "title": r.chunk.title, "score": round(r.score, 3)}
                for r in results
            ],
            generator=gen_name,
        )
