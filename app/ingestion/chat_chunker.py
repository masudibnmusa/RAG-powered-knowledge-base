"""Chunk chat logs by thread/conversation."""

from app.connectors.base_connector import RawDocument


def chunk_chat(doc: RawDocument, max_messages_per_chunk: int = 30):
    from app.ingestion.chunker import Chunk

    lines = doc.content.splitlines()
    chunks = []
    idx = 0
    for i in range(0, len(lines), max_messages_per_chunk):
        block = "\n".join(lines[i : i + max_messages_per_chunk])
        if block.strip():
            chunks.append(Chunk(id=f"{doc.id}#{idx}", text=block, index=idx))
            idx += 1
    return chunks or [Chunk(id=f"{doc.id}#0", text=doc.content, index=0)]