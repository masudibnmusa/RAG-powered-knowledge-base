"""Analyzes feedback logs to identify recurring retrieval failures."""

import json
from collections import Counter

from app.config import settings
import os


class GapAnalyzer:
    def __init__(self, log_path: str = None):
        self.log_path = log_path or os.path.join(settings.SYNC_STATE_DIR, "feedback_log.jsonl")

    def load_entries(self) -> list[dict]:
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r") as f:
            return [json.loads(line) for line in f if line.strip()]

    def find_low_rated_queries(self, min_downvotes: int = 2) -> list[dict]:
        entries = self.load_entries()
        queries = {e["id"]: e for e in entries if e.get("type") == "query"}
        ratings = [e for e in entries if e.get("type") == "rating"]

        downvote_counts = Counter(r["query_id"] for r in ratings if r.get("rating") == "down")

        gaps = []
        for query_id, count in downvote_counts.items():
            if count >= min_downvotes and query_id in queries:
                gaps.append({"query": queries[query_id]["query"], "downvotes": count})
        return sorted(gaps, key=lambda g: g["downvotes"], reverse=True)

    def find_frequent_unanswered_topics(self, top_n: int = 10) -> list[tuple[str, int]]:
        entries = self.load_entries()
        queries = [e["query"] for e in entries if e.get("type") == "query"]
        words = Counter()
        for q in queries:
            words.update(w.lower() for w in q.split() if len(w) > 3)
        return words.most_common(top_n)