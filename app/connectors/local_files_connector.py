"""Local filesystem connector."""

import os
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from app.connectors.base_connector import BaseConnector, RawDocument

SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml"}


class LocalFilesConnector(BaseConnector):
    source_name = "local_files"

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def list_documents(self) -> Iterator[RawDocument]:
        for path in self._walk_files():
            doc = self._to_raw_document(path)
            if doc:
                yield doc

    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        path = Path(doc_id)
        return self._to_raw_document(path) if path.exists() else None

    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        cutoff = timestamp.timestamp()
        for path in self._walk_files():
            if path.stat().st_mtime > cutoff:
                doc = self._to_raw_document(path)
                if doc:
                    yield doc

    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        # Compare against sync_state records of previously seen files; omitted here.
        return iter([])

    def _walk_files(self):
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix in SUPPORTED_EXTENSIONS:
                    yield path

    def _to_raw_document(self, path: Path) -> Optional[RawDocument]:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
        stat = path.stat()
        return RawDocument(
            id=str(path.resolve()),
            source=self.source_name,
            title=path.name,
            content=content,
            content_type="code" if path.suffix in {".py", ".js", ".ts"} else "text",
            last_updated=datetime.fromtimestamp(stat.st_mtime),
            url=f"file://{path.resolve()}",
        )