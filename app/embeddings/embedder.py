"""Batch embedding generation."""

from app.config import settings


class Embedder:
    def __init__(self, model: str = None, batch_size: int = 64):
        self.model = model or settings.EMBEDDING_MODEL
        self.batch_size = batch_size
        self._client = self._build_client()

    def _build_client(self):
        # from openai import OpenAI
        # return OpenAI(api_key=settings.OPENAI_API_KEY)
        return None

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            embeddings.extend(self._embed_call(batch))
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self._embed_call([text])[0]

    def _embed_call(self, batch: list[str]) -> list[list[float]]:
        # resp = self._client.embeddings.create(model=self.model, input=batch)
        # return [d.embedding for d in resp.data]
        return [[0.0] * settings.EMBEDDING_DIM for _ in batch]