"""Cron/Celery job entry point for periodic re-sync."""

import argparse

from app.connectors.local_files_connector import LocalFilesConnector
from app.connectors.github_connector import GithubConnector
from app.ingestion.sync_manager import SyncManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_connectors() -> list:
    # Register the connectors you actually want to sync from here.
    return [
        LocalFilesConnector(root_dir="./docs"),
        # GithubConnector(repo="your-org/your-repo"),
        # NotionConnector(),
        # ConfluenceConnector(base_url="https://your-domain.atlassian.net", email="you@company.com"),
        # SlackConnector(channels=["C0123456"]),
    ]


def main():
    parser = argparse.ArgumentParser(description="Run a knowledge base sync job")
    parser.add_argument("--initial", action="store_true", help="Run a full sync instead of incremental")
    args = parser.parse_args()

    connectors = build_connectors()
    manager = SyncManager(connectors=connectors)

    if args.initial:
        logger.info("Starting full sync")
        manager.full_sync()
    else:
        logger.info("Starting incremental sync")
        manager.incremental_sync()


if __name__ == "__main__":
    main()