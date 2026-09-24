from unittest.mock import patch

from app.vectorstore.access_filter import AccessFilter


def test_filter_allows_public_chunks():
    access_filter = AccessFilter()
    results = [{"metadata": {"permissions": []}}]

    filtered = access_filter.filter(user_id="u1", results=results)

    assert len(filtered) == 1


def test_filter_blocks_unauthorized_chunks():
    with patch("app.vectorstore.access_filter.get_user_groups", return_value=["group:eng"]):
        access_filter = AccessFilter()
        results = [{"metadata": {"permissions": ["group:finance"]}}]

        filtered = access_filter.filter(user_id="u2", results=results)

        assert len(filtered) == 0


def test_filter_allows_matching_group():
    with patch("app.vectorstore.access_filter.get_user_groups", return_value=["group:finance"]):
        access_filter = AccessFilter()
        results = [{"metadata": {"permissions": ["group:finance"]}}]

        filtered = access_filter.filter(user_id="u3", results=results)

        assert len(filtered) == 1