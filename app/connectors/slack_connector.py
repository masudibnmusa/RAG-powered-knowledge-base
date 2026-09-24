"""Slack connector — ingests exported channel history."""

from datetime import datetime
from typing import Iterator, Optional

import requests

from app.config import settings
from app.connectors.base_connector import BaseConnector, RawDocument

SLACK_API_BASE = "https://slack.com/api"


class SlackConnector(BaseConnector):
    source_name = "slack"

    def __init__(self, token: str = None, channels: list[str] = None):
        self.token = token or settings.SLACK_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.channels = channels or []

    def list_documents(self) -> Iterator[RawDocument]:
        for channel_id in self.channels:
            yield from self._list_threads(channel_id)

    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        channel_id, thread_ts = doc_id.split(":", 1)
        return self._fetch_thread(channel_id, thread_ts)

    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        oldest = str(timestamp.timestamp())
        for channel_id in self.channels:
            yield from self._list_threads(channel_id, oldest=oldest)

    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        return iter([])

    def _list_threads(self, channel_id: str, oldest: str = None) -> Iterator[RawDocument]:
        params = {"channel": channel_id}
        if oldest:
            params["oldest"] = oldest
        resp = requests.get(f"{SLACK_API_BASE}/conversations.history", headers=self.headers, params=params)
        resp.raise_for_status()
        for msg in resp.json().get("messages", []):
            if msg.get("thread_ts"):
                doc = self._fetch_thread(channel_id, msg["thread_ts"])
                if doc:
                    yield doc

    def _fetch_thread(self, channel_id: str, thread_ts: str) -> Optional[RawDocument]:
        resp = requests.get(
            f"{SLACK_API_BASE}/conversations.replies",
            headers=self.headers,
            params={"channel": channel_id, "ts": thread_ts},
        )
        if resp.status_code != 200:
            return None
        messages = resp.json().get("messages", [])
        content = "\n".join(f"{m.get('user', 'unknown')}: {m.get('text', '')}" for m in messages)
        return RawDocument(
            id=f"{channel_id}:{thread_ts}",
            source=self.source_name,
            title=f"Thread {thread_ts} in {channel_id}",
            content=content,
            content_type="chat",
            last_updated=datetime.fromtimestamp(float(thread_ts)),
            url=f"slack://channel/{channel_id}/{thread_ts}",
        )