"""Entry point for the RAG Knowledge Base app (API server / UI)."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.config import settings
from app.retrieval_pipeline import RetrievalPipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)
app = FastAPI(title="RAG Knowledge Base")
pipeline = RetrievalPipeline()


class QueryRequest(BaseModel):
    query: str
    user_id: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    citations: list


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    logger.info(f"Query from user={request.user_id}: {request.query}")
    result = pipeline.run(
        query=request.query,
        user_id=request.user_id,
        top_k=request.top_k,
    )
    return QueryResponse(answer=result["answer"], citations=result["citations"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)