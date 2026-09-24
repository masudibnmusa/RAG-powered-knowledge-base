from unittest.mock import MagicMock, patch

from app.retrieval_pipeline import RetrievalPipeline


@patch("app.retrieval_pipeline.LLMClient")
@patch("app.retrieval_pipeline.Reranker")
@patch("app.retrieval_pipeline.HybridSearch")
@patch("app.retrieval_pipeline.AccessFilter")
def test_pipeline_run_returns_answer_and_citations(mock_access, mock_hybrid, mock_reranker, mock_llm):
    mock_access.return_value.build_where_clause.return_value = {}
    mock_access.return_value.filter.return_value = [{"chunk_id": "c1", "text": "some text", "metadata": {"title": "Doc"}}]
    mock_hybrid.return_value.search.return_value = [{"chunk_id": "c1", "text": "some text"}]
    mock_reranker.return_value.rerank.return_value = [{"chunk_id": "c1", "text": "some text", "metadata": {"title": "Doc"}}]
    mock_llm.return_value.generate_answer.return_value = "This is the answer [1]."

    pipeline = RetrievalPipeline()
    pipeline.feedback_logger = MagicMock()

    result = pipeline.run(query="What is X?", user_id="u1", top_k=3)

    assert "answer" in result
    assert result["answer"] == "This is the answer [1]."
    assert len(result["citations"]) == 1