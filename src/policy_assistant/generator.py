"""Turn retrieved chunks into an answer: an LLM if configured, else extractive."""

from __future__ import annotations

import json
import os
import urllib.request

from .retriever import SearchResult

PROMPT_TEMPLATE = """You are a helpful life-insurance client care assistant.
Answer the question using ONLY the context below. If the context does not
contain the answer, say you don't know and suggest contacting client care.

Context:
{context}

Question: {question}
Answer:"""


def build_prompt(question: str, results: list[SearchResult]) -> str:
    context = "\n\n".join(f"[{r.chunk.title}] {r.chunk.text}" for r in results)
    return PROMPT_TEMPLATE.format(context=context, question=question)


class ExtractiveGenerator:
    """No-LLM fallback: return the best-matching section as the answer."""

    name = "extractive"

    def generate(self, question: str, results: list[SearchResult]) -> str:
        if not results:
            return "I couldn't find that in the policy information. Please contact client care."
        return results[0].chunk.text


class GeminiGenerator:
    """Calls the Google Gemini REST API with a grounded prompt."""

    name = "gemini"
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", timeout: int = 20) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def generate(self, question: str, results: list[SearchResult]) -> str:
        if not results:
            return ExtractiveGenerator().generate(question, results)
        body = json.dumps(
            {"contents": [{"parts": [{"text": build_prompt(question, results)}]}]}
        ).encode()
        req = urllib.request.Request(
            self.URL.format(model=self.model, key=self.api_key),
            data=body, headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.load(resp)
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def make_generator():
    """Use Gemini when GEMINI_API_KEY is set, otherwise the extractive fallback."""
    key = os.getenv("GEMINI_API_KEY")
    return GeminiGenerator(key) if key else ExtractiveGenerator()
