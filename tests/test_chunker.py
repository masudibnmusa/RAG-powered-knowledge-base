from app.connectors.base_connector import RawDocument
from app.ingestion.chunker import chunk_document


def test_chunk_doc_by_heading():
    content = "# Title\nIntro text.\n## Section 1\nSection content here."
    doc = RawDocument(id="1", source="test", title="doc.md", content=content, content_type="text")

    chunks = chunk_document(doc)

    assert len(chunks) >= 1
    assert all(c.text for c in chunks)


def test_chunk_code_python():
    content = "def foo():\n    return 1\n\ndef bar():\n    return 2\n"
    doc = RawDocument(id="2", source="test", title="file.py", content=content, content_type="code")

    chunks = chunk_document(doc)

    assert len(chunks) == 2
    assert "def foo" in chunks[0].text
    assert "def bar" in chunks[1].text


def test_chunk_chat():
    content = "\n".join(f"user{i}: message {i}" for i in range(50))
    doc = RawDocument(id="3", source="test", title="thread", content=content, content_type="chat")

    chunks = chunk_document(doc)

    assert len(chunks) >= 2