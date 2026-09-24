"""Orchestrates: query -> retrieve -> rerank -> generate."""

from app.embeddings.embedder import Embedder
from app.generation.citation_builder import build_citations
from app.generation.llm import LLMClient
from app.vectorstore.access_filter import AccessFilter
from app.vectorstore.hybrid_search import HybridSearch
from app.vectorstore.reranker import Reranker
from app.vectorstore.store import VectorStore
from app.feedback.feedback_logger import FeedbackLogger
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RetrievalPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedder = Embedder()
        self.hybrid_search = HybridSearch(self.vector_store, self.embedder)
        self.reranker = Reranker()
        self.access_filter = AccessFilter()
        self.llm = LLMClient()
        self.feedback_logger = FeedbackLogger()

    def run(self, query: str, user_id: str, top_k: int = 5) -> dict:
        where = self.access_filter.build_where_clause(user_id)

        candidates = self.hybrid_search.search(query, top_k=top_k * 3, where=where)
        candidates = self.access_filter.filter(user_id, candidates)

        top_chunks = self.reranker.rerank(query, candidates, top_k=top_k)

        answer = self.llm.generate_answer(query, top_chunks)
        citations = build_citations(answer, top_chunks)

        self.feedback_logger.log_query(query=query, user_id=user_id, answer=answer, chunk_ids=[c.get("chunk_id") for c in top_chunks])

        return {"answer": answer, "citations": citations, "chunks_used": top_chunks}