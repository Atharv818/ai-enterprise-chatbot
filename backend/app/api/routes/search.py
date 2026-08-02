from fastapi import APIRouter

from app.core.logging_config import get_logger
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedding import embed_query
from app.services.vector_store import search_chunks
from app.schemas.search import SearchRequest, SearchResponse, AskDocumentsResponse
from app.services.rag_answer import generate_answer

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

@router.post("/ask", response_model=AskDocumentsResponse)
def ask_documents(request: SearchRequest):
    query_embedding = embed_query(request.question)
    results = search_chunks(
        query_embedding=query_embedding,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    answer = generate_answer(request.question, results)

    logger.info(f"rag_ask_completed question={request.question!r} sources={len(results)}")

    return AskDocumentsResponse(
        question=request.question,
        answer=answer,
        sources=results,
    )
