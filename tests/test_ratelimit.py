import importlib

import pytest
from fastapi.testclient import TestClient

from policy_assistant import api
from policy_assistant.ratelimit import RateLimiter


class FakeClock:
    def __init__(self, t: float = 1_000_000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t


def test_per_ip_limit_blocks_then_recovers():
    clock = FakeClock()
    rl = RateLimiter(per_ip=2, window_s=60, daily=100, clock=clock)
    assert rl.check("1.1.1.1")[0]
    assert rl.check("1.1.1.1")[0]
    allowed, retry = rl.check("1.1.1.1")
    assert not allowed and 0 < retry <= 61
    assert rl.check("2.2.2.2")[0]  # other visitors unaffected
    clock.t += 61
    assert rl.check("1.1.1.1")[0]


def test_daily_cap_applies_to_everyone_and_resets_next_day():
    clock = FakeClock(86400 * 20 + 10)
    rl = RateLimiter(per_ip=100, window_s=60, daily=2, clock=clock)
    assert rl.check("a")[0]
    assert rl.check("b")[0]
    assert not rl.check("c")[0]
    clock.t += 86400
    assert rl.check("c")[0]


def test_ask_returns_429_with_retry_after(monkeypatch, docs_dir):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    api.get_pipeline.cache_clear()
    monkeypatch.setattr(api, "DOCS_DIR", str(docs_dir))
    monkeypatch.setattr(api, "limiter", RateLimiter(per_ip=1, window_s=600, daily=100))
    client = TestClient(api.app)
    headers = {"X-Forwarded-For": "9.9.9.9"}
    body = {"question": "How long does a claim take?"}
    assert client.post("/ask", json=body, headers=headers).status_code == 200
    resp = client.post("/ask", json=body, headers=headers)
    assert resp.status_code == 429
    assert int(resp.headers["Retry-After"]) > 0


@pytest.fixture
def cors_api(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://outview.co.za")
    yield importlib.reload(api)
    monkeypatch.delenv("ALLOWED_ORIGINS")
    importlib.reload(api)


def test_cors_allows_only_listed_origin(cors_api):
    client = TestClient(cors_api.app)
    ok = client.get("/health", headers={"Origin": "https://outview.co.za"})
    assert ok.headers.get("access-control-allow-origin") == "https://outview.co.za"
    other = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in other.headers
