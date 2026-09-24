"""Cross-encoder or Cohere-based reranking of retrieved chunks."""

from app.config import settings


class Reranker:
    def __init__(self, provider: str = "cross_encoder"):
        self.provider = provider
        self._model = self._load_model()

    def _load_model(self):
        if self.provider == "cross_encoder":
            from sentence_transformers import CrossEncoder

            return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        return None  # Cohere client would be built here

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        if not settings.RERANK_ENABLED or not candidates:
            return candidates[:top_k]

        if self.provider == "cross_encoder":
            pairs = [(query, c["text"]) for c in candidates]
            scores = self._model.predict(pairs)
            for c, score in zip(candidates, scores):
                c["rerank_score"] = float(score)
            candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
            return candidates[:top_k]

        return candidates[:top_k]