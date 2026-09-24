"""Prompt templates for grounded answer generation."""

RAG_SYSTEM_PROMPT = """You are a knowledge base assistant. Answer the user's question using ONLY the provided context.
If the context does not contain enough information, say so explicitly instead of guessing.
Always cite the source of each claim using the [n] notation matching the numbered context blocks."""

RAG_USER_TEMPLATE = """Context:
{context}

Question: {question}

Answer the question using the context above. Cite sources as [n]."""


def build_context_block(chunks: list[dict]) -> str:
    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        title = chunk.get("metadata", {}).get("title", "Untitled")
        source = chunk.get("metadata", {}).get("source", "unknown")
        blocks.append(f"[{i}] ({source} — {title})\n{chunk.get('text', '')}")
    return "\n\n".join(blocks)


def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    context = build_context_block(chunks)
    return RAG_USER_TEMPLATE.format(context=context, question=question)