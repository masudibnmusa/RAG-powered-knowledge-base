"""Maps LLM answer citations like [1], [2] back to real source document links."""

import re

CITATION_PATTERN = re.compile(r"\[(\d+)\]")


def build_citations(answer: str, chunks: list[dict]) -> list[dict]:
    cited_indices = {int(n) for n in CITATION_PATTERN.findall(answer)}
    citations = []
    for i, chunk in enumerate(chunks, start=1):
        if i in cited_indices:
            metadata = chunk.get("metadata", {})
            citations.append(
                {
                    "index": i,
                    "title": metadata.get("title"),
                    "source": metadata.get("source"),
                    "url": metadata.get("url"),
                    "author": metadata.get("author"),
                }
            )
    return citations