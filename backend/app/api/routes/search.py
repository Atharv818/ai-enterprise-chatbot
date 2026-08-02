from fastapi import APIRouter

from app.core.logging_config import get_logger
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedding import embed_query
from app.services.vector_store import search_chunks

router = APIRouter(prefix="/search", tags=["search"])
logger = get_logger(__name__)


@router.post("/documents", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    query_embedding = embed_query(request.question)
    results = search_chunks(
        query_embedding=query_embedding,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    logger.info(f"search_performed question={request.question!r} results={len(results)}")

    return SearchResponse(question=request.question, results=results)

    