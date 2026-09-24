"""Dispatches to the right source-aware chunking strategy."""

from dataclasses import dataclass

from app.connectors.base_connector import RawDocument
from app.ingestion.code_chunker import chunk_code
from app.ingestion.doc_chunker import chunk_doc
from app.ingestion.chat_chunker import chunk_chat


@dataclass
class Chunk:
    id: str
    text: str
    index: int
    start_offset: int = 0
    end_offset: int = 0


def chunk_document(doc: RawDocument) -> list[Chunk]:
    if doc.content_type == "code":
        return chunk_code(doc)
    if doc.content_type == "chat":
        return chunk_chat(doc)
    return chunk_doc(doc)