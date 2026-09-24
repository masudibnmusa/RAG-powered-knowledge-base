"""Confluence connector."""

from datetime import datetime
from typing import Iterator, Optional

import requests

from app.config import settings
from app.connectors.base_connector import BaseConnector, RawDocument


class ConfluenceConnector(BaseConnector):
    source_name = "confluence"

    def __init__(self, base_url: str, email: str, api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_key = api_key or settings.CONFLUENCE_API_KEY
        self.auth = (self.email, self.api_key)

    def list_documents(self) -> Iterator[RawDocument]:
        start = 0
        limit = 50
        while True:
            resp = requests.get(
                f"{self.base_url}/wiki/rest/api/content",
                auth=self.auth,
                params={"start": start, "limit": limit, "expand": "body.storage,version,history"},
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            for page in results:
                yield self._to_raw_document(page)
            if len(results) < limit:
                break
            start += limit

    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        resp = requests.get(
            f"{self.base_url}/wiki/rest/api/content/{doc_id}",
            auth=self.auth,
            params={"expand": "body.storage,version,history"},
        )
        if resp.status_code != 200:
            return None
        return self._to_raw_document(resp.json())

    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        cql = f'lastmodified >= "{timestamp.strftime("%Y-%m-%d %H:%M")}"'
        resp = requests.get(
            f"{self.base_url}/wiki/rest/api/content/search",
            auth=self.auth,
            params={"cql": cql, "expand": "body.storage,version,history"},
        )
        resp.raise_for_status()
        for page in resp.json().get("results", []):
            yield self._to_raw_document(page)

    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        return iter([])

    def _to_raw_document(self, page: dict) -> RawDocument:
        body = page.get("body", {}).get("storage", {}).get("value", "")
        return RawDocument(
            id=page["id"],
            source=self.source_name,
            title=page.get("title", ""),
            content=body,
            content_type="text",
            author=page.get("history", {}).get("createdBy", {}).get("displayName"),
            last_updated=datetime.fromisoformat(page["version"]["when"]) if page.get("version") else None,
            url=f"{self.base_url}/wiki{page.get('_links', {}).get('webui', '')}",
        )