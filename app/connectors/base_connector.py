"""Abstract interface that all source connectors must implement."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator, Optional


@dataclass
class RawDocument:
    """A single document/file pulled from a source, before chunking."""

    id: str                      # stable unique id (source-specific)
    source: str                  # e.g. "google_drive", "github", "notion"
    title: str
    content: str
    content_type: str            # "text", "code", "chat", etc.
    author: Optional[str] = None
    last_updated: Optional[datetime] = None
    url: Optional[str] = None
    permissions: list[str] = field(default_factory=list)  # user/group ids allowed to view
    extra_metadata: dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """All connectors (Google Drive, Notion, GitHub, etc.) implement this."""

    source_name: str = "base"

    @abstractmethod
    def list_documents(self) -> Iterator[RawDocument]:
        """Yield all documents currently available at the source."""
        raise NotImplementedError

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        """Fetch a single document by id."""
        raise NotImplementedError

    @abstractmethod
    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        """Yield documents changed/added since the given timestamp."""
        raise NotImplementedError

    @abstractmethod
    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        """Yield ids of documents deleted since the given timestamp."""
        raise NotImplementedError