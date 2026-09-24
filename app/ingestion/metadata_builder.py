"""Attach source, author, permissions, and timestamps to each chunk."""

from app.connectors.base_connector import RawDocument
from app.ingestion.chunker import Chunk


def build_metadata(doc: RawDocument, chunk: Chunk) -> dict:
    return {
        "doc_id": doc.id,
        "chunk_id": chunk.id,
        "chunk_index": chunk.index,
        "source": doc.source,
        "title": doc.title,
        "author": doc.author,
        "last_updated": doc.last_updated.isoformat() if doc.last_updated else None,
        "url": doc.url,
        "content_type": doc.content_type,
        "permissions": doc.permissions,
        **doc.extra_metadata,
    }