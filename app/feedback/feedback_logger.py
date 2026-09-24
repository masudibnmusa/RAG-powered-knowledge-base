"""Logs thumbs up/down ratings and the queries/answers they relate to."""

import json
import os
import uuid
from datetime import datetime

from app.config import settings


class FeedbackLogger:
    def __init__(self, log_path: str = None):
        self.log_path = log_path or os.path.join(settings.SYNC_STATE_DIR, "feedback_log.jsonl")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_query(self, query: str, user_id: str, answer: str, chunk_ids: list[str]) -> str:
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "type": "query",
            "query": query,
            "user_id": user_id,
            "answer": answer,
            "chunk_ids": chunk_ids,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._append(entry)
        return entry_id

    def log_rating(self, query_id: str, rating: str, comment: str = None):
        entry = {
            "type": "rating",
            "query_id": query_id,
            "rating": rating,  # "up" | "down"
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._append(entry)

    def _append(self, entry: dict):
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")