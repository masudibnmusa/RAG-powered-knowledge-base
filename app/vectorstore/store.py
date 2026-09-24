"""Vector DB client wrapper — supports Pinecone, Chroma, or Weaviate."""

from app.config import settings
from app.ingestion.chunker import Chunk


class VectorStore:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.VECTOR_DB_PROVIDER
        self._client = self._build_client()

    def _build_client(self):
        if self.provider == "pinecone":
            return self._build_pinecone()
        if self.provider == "weaviate":
            return self._build_weaviate()
        return self._build_chroma()

    def _build_chroma(self):
        import chromadb

        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        return client.get_or_create_collection(name="knowledge_base")

    def _build_pinecone(self):
        # from pinecone import Pinecone
        # pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        # return pc.Index("knowledge-base")
        raise NotImplementedError("Wire up Pinecone client here")

    def _build_weaviate(self):
        # import weaviate
        # return weaviate.connect_to_custom(http_host=settings.WEAVIATE_URL)
        raise NotImplementedError("Wire up Weaviate client here")

    def upsert(self, doc_id: str, chunks: list[Chunk], embeddings: list[list[float]], metadata_list: list[dict]):
        ids = [c.id for c in chunks]
        texts = [c.text for c in chunks]
        if self.provider == "chroma":
            self._client.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadata_list)
        else:
            raise NotImplementedError(f"upsert not implemented for provider={self.provider}")

    def delete_by_doc_id(self, doc_id: str):
        if self.provider == "chroma":
            self._client.delete(where={"doc_id": doc_id})
        else:
            raise NotImplementedError(f"delete not implemented for provider={self.provider}")

    def query(self, embedding: list[float], top_k: int = 10, where: dict = None):
        if self.provider == "chroma":
            return self._client.query(query_embeddings=[embedding], n_results=top_k, where=where)
        raise NotImplementedError(f"query not implemented for provider={self.provider}")