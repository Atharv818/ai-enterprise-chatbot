from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str
    document_id: str | None = None
    top_k: int = 5


class SearchResult(BaseModel):
    text: str
    document_id: str
    chunk_index: int
    score: float


class SearchResponse(BaseModel):
    question: str
    results: list[SearchResult]

    