"""FastAPI service exposing the pipeline over HTTP."""

from __future__ import annotations

import os
from dataclasses import asdict
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import __version__
from .pipeline import RAGPipeline

DOCS_DIR = os.getenv("DOCS_DIR", "data/docs")
MODEL_PATH = os.getenv("MODEL_PATH", "models/intent.joblib")

app = FastAPI(title="Policy Assistant", version=__version__)


class Question(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(3, ge=1, le=10)


@lru_cache(maxsize=1)
def get_pipeline() -> RAGPipeline:
    return RAGPipeline.from_paths(DOCS_DIR, MODEL_PATH)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/ask")
def ask(q: Question) -> dict:
    try:
        return asdict(get_pipeline().ask(q.question, top_k=q.top_k))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
