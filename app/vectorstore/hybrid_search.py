"""Combines semantic (vector) search with BM25 keyword search."""

from rank_bm25 import BM25Okapi

from app.config import settings
from app.embeddings.embedder import Embedder
from app.vectorstore.store import VectorStore


class HybridSearch:
    def __init__(self, vector_store: VectorStore = None, embedder: Embedder = None, alpha: float = None):
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or Embedder()
        self.alpha = alpha if alpha is not None else settings.HYBRID_SEARCH_ALPHA  # 1.0 = pure semantic
        self._bm25_index = None
        self._bm25_corpus_ids = []

    def build_bm25_index(self, corpus: list[tuple[str, str]]):
        """corpus: list of (chunk_id, text) pairs to index for keyword search."""
        self._bm25_corpus_ids = [c[0] for c in corpus]
        tokenized = [text.lower().split() for _, text in corpus]
        self._bm25_index = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10, where: dict = None) -> list[dict]:
        semantic_results = self._semantic_search(query, top_k * 2, where)
        keyword_results = self._keyword_search(query, top_k * 2)
        return self._merge_results(semantic_results, keyword_results, top_k)

    def _semantic_search(self, query: str, top_k: int, where: dict = None) -> dict:
        embedding = self.embedder.embed_query(query)
        return self.vector_store.query(embedding, top_k=top_k, where=where)

    def _keyword_search(self, query: str, top_k: int) -> list[tuple[str, float]]:
        if not self._bm25_index:
            return []
        scores = self._bm25_index.get_scores(query.lower().split())
        ranked = sorted(zip(self._bm25_corpus_ids, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def _merge_results(self, semantic: dict, keyword: list[tuple[str, float]], top_k: int) -> list[dict]:
        scores: dict[str, float] = {}

        sem_ids = semantic.get("ids", [[]])[0]
        sem_distances = semantic.get("distances", [[]])[0]
        for chunk_id, dist in zip(sem_ids, sem_distances):
            scores[chunk_id] = scores.get(chunk_id, 0) + self.alpha * (1 - dist)

        if keyword:
            max_kw_score = max((s for _, s in keyword), default=1) or 1
            for chunk_id, kw_score in keyword:
                scores[chunk_id] = scores.get(chunk_id, 0) + (1 - self.alpha) * (kw_score / max_kw_score)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{"chunk_id": cid, "score": score} for cid, score in ranked]