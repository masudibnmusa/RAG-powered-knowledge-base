from datetime import datetime

from app.connectors.local_files_connector import LocalFilesConnector


def test_local_files_connector_reads_files(tmp_path):
    file = tmp_path / "note.md"
    file.write_text("# Hello\nThis is a test note.")

    connector = LocalFilesConnector(root_dir=str(tmp_path))
    docs = list(connector.list_documents())

    assert len(docs) == 1
    assert docs[0].title == "note.md"
    assert "Hello" in docs[0].content


def test_local_files_connector_change_detection(tmp_path):
    file = tmp_path / "note.md"
    file.write_text("original content")

    connector = LocalFilesConnector(root_dir=str(tmp_path))
    old_time = datetime(1970, 1, 1)
    changed = list(connector.list_changed_since(old_time))

    assert len(changed) == 1