"""Detects new/updated/deleted documents via content hashing."""

import hashlib
import json
import os
from datetime import datetime, timezone

from app.config import settings
from app.connectors.base_connector import RawDocument


class ChangeDetector:
    def __init__(self, state_dir: str = None):
        self.state_dir = state_dir or settings.SYNC_STATE_DIR
        os.makedirs(self.state_dir, exist_ok=True)
        self.hashes_path = os.path.join(self.state_dir, "doc_hashes.json")
        self.sync_times_path = os.path.join(self.state_dir, "last_sync.json")
        self._hashes = self._load_json(self.hashes_path)
        self._sync_times = self._load_json(self.sync_times_path)

    def has_changed(self, doc: RawDocument) -> bool:
        new_hash = self._hash_content(doc.content)
        return self._hashes.get(doc.id) != new_hash

    def record_hash(self, doc: RawDocument):
        self._hashes[doc.id] = self._hash_content(doc.content)
        self._save_json(self.hashes_path, self._hashes)

    def get_last_sync(self, source: str) -> datetime:
        ts = self._sync_times.get(source)
        return datetime.fromisoformat(ts) if ts else datetime(1970, 1, 1, tzinfo=timezone.utc)

    def mark_synced(self, source: str, timestamp: datetime):
        self._sync_times[source] = timestamp.isoformat()
        self._save_json(self.sync_times_path, self._sync_times)

    @staticmethod
    def _hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _load_json(path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save_json(path: str, data: dict):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)