"""Chunk source code by function/class using simple heuristics (or an AST parser)."""

import ast
import re

from app.connectors.base_connector import RawDocument


def chunk_code(doc: RawDocument, max_chunk_chars: int = 2000):
    from app.ingestion.chunker import Chunk

    if doc.title.endswith(".py"):
        return _chunk_python(doc, max_chunk_chars)
    return _chunk_generic_code(doc, max_chunk_chars)


def _chunk_python(doc: RawDocument, max_chunk_chars: int):
    from app.ingestion.chunker import Chunk

    try:
        tree = ast.parse(doc.content)
    except SyntaxError:
        return _chunk_generic_code(doc, max_chunk_chars)

    lines = doc.content.splitlines()
    chunks = []
    idx = 0
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", start + 1)
            snippet = "\n".join(lines[start:end])
            chunks.append(Chunk(id=f"{doc.id}#{idx}", text=snippet, index=idx, start_offset=start, end_offset=end))
            idx += 1

    if not chunks:
        return _chunk_generic_code(doc, max_chunk_chars)
    return chunks


def _chunk_generic_code(doc: RawDocument, max_chunk_chars: int):
    """Fallback: split by blank-line-delimited blocks, respecting a max size."""
    from app.ingestion.chunker import Chunk

    blocks = re.split(r"\n\s*\n", doc.content)
    chunks, buffer, idx = [], "", 0
    for block in blocks:
        if len(buffer) + len(block) > max_chunk_chars and buffer:
            chunks.append(Chunk(id=f"{doc.id}#{idx}", text=buffer.strip(), index=idx))
            idx += 1
            buffer = ""
        buffer += block + "\n\n"
    if buffer.strip():
        chunks.append(Chunk(id=f"{doc.id}#{idx}", text=buffer.strip(), index=idx))
    return chunks