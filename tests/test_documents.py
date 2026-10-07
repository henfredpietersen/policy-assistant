import pytest

from policy_assistant.documents import load_chunks, split_markdown


def test_split_markdown_one_chunk_per_section():
    md = "# Title\n\n## First\nHello world.\n\n## Second\nMore text\nacross lines."
    chunks = split_markdown("doc", md)
    assert [c.title for c in chunks] == ["First", "Second"]
    assert chunks[1].text == "More text across lines."
    assert chunks[0].id == "doc#First"


def test_load_chunks_reads_all_docs(docs_dir):
    chunks = load_chunks(docs_dir)
    assert len(chunks) >= 10
    assert {c.doc for c in chunks} == {"beneficiaries", "cancellations", "claims", "premiums"}


def test_load_chunks_empty_dir_raises(tmp_path):
    with pytest.raises(ValueError):
        load_chunks(tmp_path)
