"""Google Drive connector."""

from datetime import datetime
from typing import Iterator, Optional

from app.config import settings
from app.connectors.base_connector import BaseConnector, RawDocument


class GoogleDriveConnector(BaseConnector):
    source_name = "google_drive"

    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or settings.GOOGLE_DRIVE_CREDENTIALS
        self._client = self._build_client()

    def _build_client(self):
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build
        # creds = service_account.Credentials.from_service_account_file(self.credentials_path)
        # return build("drive", "v3", credentials=creds)
        raise NotImplementedError("Wire up Google Drive API client here")

    def list_documents(self) -> Iterator[RawDocument]:
        for file in self._list_all_files():
            yield self._to_raw_document(file)

    def get_document(self, doc_id: str) -> Optional[RawDocument]:
        file = self._client.files().get(fileId=doc_id).execute()
        return self._to_raw_document(file) if file else None

    def list_changed_since(self, timestamp: datetime) -> Iterator[RawDocument]:
        query = f"modifiedTime > '{timestamp.isoformat()}'"
        for file in self._list_all_files(query=query):
            yield self._to_raw_document(file)

    def list_deleted_since(self, timestamp: datetime) -> Iterator[str]:
        # Google Drive Changes API tracks deletions explicitly
        return iter([])

    def _list_all_files(self, query: str = None):
        # results = self._client.files().list(q=query, fields="files(id,name,mimeType,modifiedTime,owners,permissions)").execute()
        # return results.get("files", [])
        return []

    def _to_raw_document(self, file: dict) -> RawDocument:
        return RawDocument(
            id=file["id"],
            source=self.source_name,
            title=file.get("name", ""),
            content=self._extract_text(file),
            content_type="text",
            author=(file.get("owners") or [{}])[0].get("displayName"),
            last_updated=datetime.fromisoformat(file["modifiedTime"]) if file.get("modifiedTime") else None,
            url=f"https://drive.google.com/file/d/{file['id']}/view",
            permissions=[p.get("id") for p in file.get("permissions", [])],
        )

    def _extract_text(self, file: dict) -> str:
        # Export Google Docs as plain text, or download raw bytes for other types
        return ""