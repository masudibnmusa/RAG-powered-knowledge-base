from unittest.mock import MagicMock

from app.vectorstore.hybrid_search import HybridSearch


def test_build_bm25_index_and_keyword_search():
    search = HybridSearch(vector_store=MagicMock(), embedder=MagicMock())
    corpus = [("c1", "python code for retrieval"), ("c2", "javascript frontend code")]
    search.build_bm25_index(corpus)

    results = search._keyword_search("python retrieval", top_k=2)

    assert results[0][0] == "c1"


def test_merge_results_combines_scores():
    search = HybridSearch(vector_store=MagicMock(), embedder=MagicMock(), alpha=0.5)
    semantic = {"ids": [["c1", "c2"]], "distances": [[0.1, 0.4]]}
    keyword = [("c1", 5.0), ("c2", 1.0)]

    merged = search._merge_results(semantic, keyword, top_k=2)

    assert merged[0]["chunk_id"] == "c1"