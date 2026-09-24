"""User authentication and permission lookups."""

from app.config import settings


def get_user_groups(user_id: str) -> list[str]:
    """Return the list of group/team ids a user belongs to.

    Wire this up to your identity provider (Okta, Google Workspace, internal DB, etc.).
    """
    # Example stub — replace with a real IdP lookup
    return [f"user:{user_id}", "group:all_employees"]


def verify_token(token: str) -> str | None:
    """Validate an auth token and return the associated user_id, or None if invalid."""
    # Example stub — replace with real JWT/session validation
    if not token:
        return None
    return token.split(":")[-1] if ":" in token else None