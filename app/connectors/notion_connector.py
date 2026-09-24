"""Notion connector."""

from datetime import datetime
from typing import Iterator, Optional

import requests

from app.config import settings
from app.connectors.base_connector import BaseConnector, RawDocument

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionConnector(BaseConnector):
    source_name = "notion"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.NOTION_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def list_documents(self) -> Iterator[RawDocument]:
        cursor = None
        while True:
            payload = {"start_cursor": cursor} if cursor else {}
            resp = requests.post(f"{NOTION_API_BASE}/search", headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            for page in data.get("results", []):
                doc = self._to_raw_document(page)
                if doc:
                    yield doc
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")

    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        resp = requests.get(f"{NOTION_API_BASE}/pages/{doc_id}", headers=self.headers)
        if resp.status_code != 200:
            return None
        return self._to_raw_document(resp.json())

    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        for doc in self.list_documents():
            if doc.last_updated and doc.last_updated > timestamp:
                yield doc

    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        return iter([])

    def _to_raw_document(self, page: dict) -> Optional[RawDocument]:
        if page.get("object") != "page":
            return None
        title = self._extract_title(page)
        return RawDocument(
            id=page["id"],
            source=self.source_name,
            title=title,
            content=self._fetch_page_content(page["id"]),
            content_type="text",
            last_updated=datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00")),
            url=page.get("url"),
        )

    def _extract_title(self, page: dict) -> str:
        props = page.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title" and prop.get("title"):
                return "".join(t.get("plain_text", "") for t in prop["title"])
        return "Untitled"

    def _fetch_page_content(self, page_id: str) -> str:
        resp = requests.get(f"{NOTION_API_BASE}/blocks/{page_id}/children", headers=self.headers)
        if resp.status_code != 200:
            return ""
        blocks = resp.json().get("results", [])
        texts = []
        for block in blocks:
            block_type = block.get("type")
            rich_text = block.get(block_type, {}).get("rich_text", [])
            texts.append("".join(t.get("plain_text", "") for t in rich_text))
        return "\n".join(texts)