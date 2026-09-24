"""Orchestrates pulling from all connectors and feeding the ingestion pipeline."""

from datetime import datetime

from app.connectors.base_connector import BaseConnector
from app.ingestion.change_detector import ChangeDetector
from app.ingestion.chunker import chunk_document
from app.ingestion.metadata_builder import build_metadata
from app.embeddings.embedder import Embedder
from app.vectorstore.store import VectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SyncManager:
    def __init__(self, connectors: list[BaseConnector], vector_store: VectorStore = None, embedder: Embedder = None):
        self.connectors = connectors
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or Embedder()
        self.change_detector = ChangeDetector()

    def full_sync(self):
        """Pull everything from every connector and index it from scratch."""
        for connector in self.connectors:
            logger.info(f"Full sync starting for source={connector.source_name}")
            for raw_doc in connector.list_documents():
                self._index_document(raw_doc)
            self.change_detector.mark_synced(connector.source_name, datetime.utcnow())
            logger.info(f"Full sync complete for source={connector.source_name}")

    def incremental_sync(self):
        """Pull only changed/deleted documents since the last sync per source."""
        for connector in self.connectors:
            last_sync = self.change_detector.get_last_sync(connector.source_name)
            logger.info(f"Incremental sync for source={connector.source_name} since={last_sync}")

            for raw_doc in connector.list_changed_since(last_sync):
                self._index_document(raw_doc)

            for deleted_id in connector.list_deleted_since(last_sync):
                self.vector_store.delete_by_doc_id(deleted_id)

            self.change_detector.mark_synced(connector.source_name, datetime.utcnow())

    def _index_document(self, raw_doc):
        if not self.change_detector.has_changed(raw_doc):
            logger.debug(f"Skipping unchanged doc: {raw_doc.id}")
            return

        chunks = chunk_document(raw_doc)
        metadata_list = [build_metadata(raw_doc, chunk) for chunk in chunks]
        embeddings = self.embedder.embed_batch([c.text for c in chunks])

        self.vector_store.upsert(
            doc_id=raw_doc.id,
            chunks=chunks,
            embeddings=embeddings,
            metadata_list=metadata_list,
        )
        self.change_detector.record_hash(raw_doc)