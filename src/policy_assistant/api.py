"""FastAPI service exposing the pipeline over HTTP."""

from __future__ import annotations

import os
from dataclasses import asdict
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .pipeline import RAGPipeline
from .ratelimit import RateLimiter

DOCS_DIR = os.getenv("DOCS_DIR", "data/docs")
MODEL_PATH = os.getenv("MODEL_PATH", "models/intent.joblib")

# Comma-separated list of web origins allowed to call the API from a browser,
# e.g. "https://outview.co.za,https://www.outview.co.za". Empty = no browser access.
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

limiter = RateLimiter(
    per_ip=int(os.getenv("RATE_LIMIT_PER_IP", "20")),
    window_s=int(os.getenv("RATE_LIMIT_WINDOW_S", "600")),
    daily=int(os.getenv("RATE_LIMIT_DAILY", "500")),
)

app = FastAPI(title="Policy Assistant", version=__version__)

if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )


class Question(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(3, ge=1, le=10)


@lru_cache(maxsize=1)
def get_pipeline() -> RAGPipeline:
    return RAGPipeline.from_paths(DOCS_DIR, MODEL_PATH)


def client_ip(request: Request) -> str:
    # Behind a proxy (Render) the visitor's address is the first X-Forwarded-For entry.
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limited(request: Request) -> None:
    allowed, retry_after = limiter.check(client_ip(request))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many questions for now. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/ask", dependencies=[Depends(rate_limited)])
def ask(q: Question) -> dict:
    try:
        return asdict(get_pipeline().ask(q.question, top_k=q.top_k))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
