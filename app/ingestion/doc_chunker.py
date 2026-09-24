"""Chunk prose documents by heading/section."""

import re

from app.connectors.base_connector import RawDocument

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+.*$", re.MULTILINE)


def chunk_doc(doc: RawDocument, max_chunk_chars: int = 1500, overlap_chars: int = 150):
    from app.ingestion.chunker import Chunk

    sections = _split_by_headings(doc.content)
    chunks = []
    idx = 0
    for section in sections:
        for piece in _split_with_overlap(section, max_chunk_chars, overlap_chars):
            if piece.strip():
                chunks.append(Chunk(id=f"{doc.id}#{idx}", text=piece.strip(), index=idx))
                idx += 1
    return chunks


def _split_by_headings(content: str) -> list[str]:
    matches = list(HEADING_PATTERN.finditer(content))
    if not matches:
        return [content]

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append(content[start:end])
    return sections


def _split_with_overlap(text: str, max_chars: int, overlap: int):
    if len(text) <= max_chars:
        yield text
        return
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        yield text[start:end]
        start = end - overlap if end < len(text) else end