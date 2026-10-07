import pytest
from fastapi.testclient import TestClient

from policy_assistant import api
from policy_assistant.generator import ExtractiveGenerator
from policy_assistant.pipeline import RAGPipeline


class BrokenGenerator:
    name = "broken"

    def generate(self, question, results):
        raise ConnectionError("LLM is down")


def test_pipeline_falls_back_when_llm_fails(docs_dir):
    pipe = RAGPipeline.from_paths(docs_dir)
    pipe.generator = BrokenGenerator()
    ans = pipe.ask("How long does a claim take?")
    assert ans.generator == "extractive-fallback"
    assert "5 working days" in ans.answer


def test_pipeline_rejects_empty_question(docs_dir):
    pipe = RAGPipeline.from_paths(docs_dir)
    pipe.generator = ExtractiveGenerator()
    with pytest.raises(ValueError):
        pipe.ask("   ")


@pytest.fixture
def client(monkeypatch, docs_dir):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    api.get_pipeline.cache_clear()
    monkeypatch.setattr(api, "DOCS_DIR", str(docs_dir))
    return TestClient(api.app)


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_ask_returns_answer_and_sources(client):
    resp = client.post("/ask", json={"question": "Can my child be a beneficiary?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["sources"][0]["title"] == "Minors as beneficiaries"
    assert body["answer"]


def test_ask_validates_input(client):
    assert client.post("/ask", json={"question": "x"}).status_code == 422
