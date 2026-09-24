"""Central configuration: API keys, DB config, sync schedule."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # App
    PORT: int = int(os.getenv("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

    # Vector DB
    VECTOR_DB_PROVIDER: str = os.getenv("VECTOR_DB_PROVIDER", "chroma")  # pinecone | chroma | weaviate
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "")
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "data/vector_db")

    # Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", 1536))

    # Connectors
    GOOGLE_DRIVE_CREDENTIALS: str = os.getenv("GOOGLE_DRIVE_CREDENTIALS", "")
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    CONFLUENCE_API_KEY: str = os.getenv("CONFLUENCE_API_KEY", "")
    SLACK_TOKEN: str = os.getenv("SLACK_TOKEN", "")

    # Sync
    SYNC_INTERVAL_MINUTES: int = int(os.getenv("SYNC_INTERVAL_MINUTES", 60))
    SYNC_STATE_DIR: str = os.getenv("SYNC_STATE_DIR", "data/sync_state")

    # Retrieval
    RERANK_ENABLED: bool = os.getenv("RERANK_ENABLED", "true").lower() == "true"
    HYBRID_SEARCH_ALPHA: float = float(os.getenv("HYBRID_SEARCH_ALPHA", 0.5))  # weight: semantic vs keyword


settings = Settings()