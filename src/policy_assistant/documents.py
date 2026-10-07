"""Load markdown documents and split them into retrievable chunks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    """One retrievable piece of a document: a single '## ' section."""

    doc: str
    title: str
    text: str

    @property
    def id(self) -> str:
        return f"{self.doc}#{self.title}"


def split_markdown(doc_name: str, markdown: str) -> list[Chunk]:
    """Split a markdown document into one chunk per level-2 heading."""
    chunks: list[Chunk] = []
    title: str | None = None
    lines: list[str] = []

    def flush() -> None:
        body = " ".join(line.strip() for line in lines if line.strip())
        if title and body:
            chunks.append(Chunk(doc=doc_name, title=title, text=body))

    for line in markdown.splitlines():
        if line.startswith("## "):
            flush()
            title, lines = line[3:].strip(), []
        elif not line.startswith("# "):
            lines.append(line)
    flush()
    return chunks


def load_chunks(docs_dir: str | Path) -> list[Chunk]:
    """Load every .md file in a folder and return all chunks."""
    docs_dir = Path(docs_dir)
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.glob("*.md")):
        chunks.extend(split_markdown(path.stem, path.read_text(encoding="utf-8")))
    if not chunks:
        raise ValueError(f"No chunks found in {docs_dir}")
    return chunks
