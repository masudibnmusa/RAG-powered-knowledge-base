"""Filters retrieved chunks by the querying user's permissions."""

from app.utils.auth import get_user_groups


class AccessFilter:
    def filter(self, user_id: str, results: list[dict]) -> list[dict]:
        user_groups = set(get_user_groups(user_id))
        allowed = []
        for result in results:
            permissions = result.get("metadata", {}).get("permissions", [])
            if not permissions or user_id in permissions or user_groups.intersection(permissions):
                allowed.append(result)
        return allowed

    def build_where_clause(self, user_id: str) -> dict:
        """Optional: push permission filtering down into the vector DB query itself."""
        user_groups = list(get_user_groups(user_id))
        return {"permissions": {"$in": [user_id] + user_groups}}