"""GitHub connector — codebase ingestion."""

from datetime import datetime
from typing import Iterator, Optional

import requests

from app.config import settings
from app.connectors.base_connector import BaseConnector, RawDocument

GITHUB_API_BASE = "https://api.github.com"

CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go", ".rb", ".rs", ".cpp", ".c", ".md"}


class GithubConnector(BaseConnector):
    source_name = "github"

    def __init__(self, repo: str, token: str = None):
        self.repo = repo  # "owner/name"
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"}

    def list_documents(self) -> Iterator[RawDocument]:
        for path in self._list_repo_files():
            doc = self._fetch_file(path)
            if doc:
                yield doc

    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        return self._fetch_file(doc_id)

    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        since = timestamp.isoformat()
        resp = requests.get(
            f"{GITHUB_API_BASE}/repos/{self.repo}/commits",
            headers=self.headers,
            params={"since": since},
        )
        resp.raise_for_status()
        changed_paths = set()
        for commit in resp.json():
            commit_detail = requests.get(commit["url"], headers=self.headers).json()
            for f in commit_detail.get("files", []):
                if f["status"] != "removed":
                    changed_paths.add(f["filename"])
        for path in changed_paths:
            doc = self._fetch_file(path)
            if doc:
                yield doc

    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        since = timestamp.isoformat()
        resp = requests.get(
            f"{GITHUB_API_BASE}/repos/{self.repo}/commits",
            headers=self.headers,
            params={"since": since},
        )
        resp.raise_for_status()
        for commit in resp.json():
            commit_detail = requests.get(commit["url"], headers=self.headers).json()
            for f in commit_detail.get("files", []):
                if f["status"] == "removed":
                    yield f["filename"]

    def _list_repo_files(self) -> list[str]:
        resp = requests.get(
            f"{GITHUB_API_BASE}/repos/{self.repo}/git/trees/HEAD",
            headers=self.headers,
            params={"recursive": "1"},
        )
        resp.raise_for_status()
        return [
            item["path"]
            for item in resp.json().get("tree", [])
            if item["type"] == "blob" and self._is_code_or_doc(item["path"])
        ]

    def _is_code_or_doc(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in CODE_EXTENSIONS)

    def _fetch_file(self, path: str) -> Optional[RawDocument]:
        resp = requests.get(
            f"{GITHUB_API_BASE}/repos/{self.repo}/contents/{path}",
            headers=self.headers,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        import base64

        content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        return RawDocument(
            id=f"{self.repo}:{path}",
            source=self.source_name,
            title=path,
            content=content,
            content_type="code" if not path.endswith(".md") else "text",
            url=data.get("html_url"),
            extra_metadata={"repo": self.repo, "path": path, "sha": data.get("sha")},
        )