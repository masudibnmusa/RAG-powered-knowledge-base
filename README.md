# RAG-Powered Knowledge Base

A searchable knowledge base built over a large, heterogeneous corpus — company docs, codebases, wikis, and personal notes — using a vector database for retrieval and an LLM for grounded question answering.

This is a production-oriented version of a simple Document Q&A bot, adding multi-source ingestion, incremental updates, access control, and support for structured content like code.

## Overview

**Core idea:** Continuously ingest and index content from multiple sources into a vector DB → retrieve relevant chunks per query (with hybrid search/reranking for accuracy) → generate grounded answers with citations → keep the index fresh as source content changes.

## How It Works

1. **Multi-source ingestion** — pull from Google Drive, Notion, Confluence, GitHub repos, Slack exports, local files, etc.
2. **Source-aware chunking** — code gets chunked by function/class, docs by section/heading, chat logs by thread
3. **Embedding & indexing** — embed chunks and store with rich metadata (source, author, last updated, permissions)
4. **Incremental sync** — detect changed/deleted docs and update the index instead of rebuilding from scratch
5. **Hybrid retrieval** — combine semantic search + keyword search (BM25) + optional reranking for better precision
6. **Access control** — filter retrieved results based on user permissions (important for company data)
7. **Answer generation** — LLM answers with inline citations back to source documents/files
8. **Feedback loop** — track thumbs up/down on answers to identify retrieval gaps

## 📁 Project Structure

```text
rag-knowledge-base/
│
├── app/
│   ├── __init__.py
│   ├── main.py                         # Entry point (API server / UI)
│   ├── config.py                       # API keys, DB config, sync schedule
│   │
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base_connector.py           # Abstract interface for all connectors
│   │   ├── google_drive_connector.py
│   │   ├── notion_connector.py
│   │   ├── github_connector.py         # Codebase ingestion
│   │   ├── confluence_connector.py
│   │   ├── local_files_connector.py
│   │   └── slack_connector.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── sync_manager.py             # Orchestrates pulling from all connectors
│   │   ├── change_detector.py          # Detect new/updated/deleted docs
│   │   ├── chunker.py                  # Source-aware chunking strategies
│   │   ├── code_chunker.py             # Chunk by function/class
│   │   ├── doc_chunker.py              # Chunk by heading/section
│   │   ├── chat_chunker.py             # Chunk by thread/conversation
│   │   └── metadata_builder.py         # Attach source, author, permissions, timestamps
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedder.py                 # Batch embedding generation
│   │
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   ├── store.py                    # Pinecone/Chroma/Weaviate client wrapper
│   │   ├── hybrid_search.py            # Semantic + BM25 keyword search
│   │   ├── reranker.py                 # Cross-encoder/Cohere reranking
│   │   └── access_filter.py            # Permission-based result filtering
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── prompt_templates.py         # LLM prompt templates
│   │   ├── llm.py                      # Claude/GPT API wrapper
│   │   └── citation_builder.py         # Map answers back to source docs/links
│   │
│   ├── retrieval_pipeline.py           # Query → retrieve → rerank → generate
│   │
│   ├── feedback/
│   │   ├── __init__.py
│   │   ├── feedback_logger.py          # Log thumbs up/down + queries
│   │   └── gap_analyzer.py             # Identify recurring retrieval failures
│   │
│   └── utils/
│       ├── __init__.py
│       ├── auth.py                     # User authentication/permissions
│       └── logger.py                   # Application logging
│
├── data/
│   ├── raw_sources/                    # Cached raw pulls from connectors
│   ├── vector_db/                      # Local Chroma files
│   └── sync_state/                     # Track last sync timestamps per source
│
├── scheduler/
│   └── sync_job.py                     # Cron/Celery job for periodic re-sync
│
├── tests/
│   ├── test_connectors.py
│   ├── test_chunker.py
│   ├── test_hybrid_search.py
│   ├── test_access_filter.py
│   └── test_retrieval_pipeline.py
│
├── .env                                # Environment variables
├── .env.example                        # Environment variable template
├── .gitignore
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # Spin up vector DB + app together
├── README.md
└── run.sh                              # Application startup script


## Tech Stack

- **Vector DB:** Pinecone / Chroma / Weaviate
- **LLM:** Claude / GPT (configurable via `app/generation/llm.py`)
- **Keyword search:** BM25
- **Reranking:** Cross-encoder or Cohere Rerank
- **Scheduling:** Cron / Celery

## Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional, for local vector DB)
- API keys for your chosen vector DB and LLM provider

### Installation

```bash
git clone <repo-url>
cd rag-knowledge-base
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your API keys and config (vector DB credentials, LLM API key, connector OAuth tokens, sync schedule, etc.).

### Running Locally

```bash
# Spin up the vector DB (if using local Chroma or a containerized DB)
docker-compose up -d

# Run an initial sync
python scheduler/sync_job.py --initial

# Start the app
./run.sh
```

## Configuration

All source connectors, sync intervals, chunking strategies, and model settings are managed in `app/config.py` and `.env`. See `.env.example` for the full list of required environment variables.

## Testing

```bash
pytest tests/
```

## License

MIT