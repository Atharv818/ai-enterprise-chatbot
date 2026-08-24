import uuid

from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.qdrant_client import qdrant

logger = get_logger(__name__)

COLLECTION_NAME = "document_chunks"
VECTOR_SIZE = 384


def ensure_collection_exists() -> None:
    existing = [collection.name for collection in qdrant.get_collections().collections]

    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        logger.info("qdrant_collection_created name=%s", COLLECTION_NAME)


def store_chunks(
    document_id: str,
    tenant_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    ensure_collection_exists()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "document_id": document_id,
                "tenant_id": tenant_id,
                "chunk_index": index,
                "text": chunk,
            },
        )
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)


def search_chunks(
    query_embedding: list[float],
    tenant_id: str,
    top_k: int = 5,
    document_id: str | None = None,
    min_score: float | None = None,
) -> list[dict]:
    existing = [collection.name for collection in qdrant.get_collections().collections]

    if COLLECTION_NAME not in existing:
        return []

    from qdrant_client.models import FieldCondition, Filter, MatchValue

    must_conditions = [
        FieldCondition(
            key="tenant_id",
            match=MatchValue(value=tenant_id),
        )
    ]

    if document_id:
        must_conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchValue(value=document_id),
            )
        )

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        query_filter=Filter(must=must_conditions),
        with_payload=True,
    )

    relevance_floor = (
        settings.RAG_MIN_RELEVANCE_SCORE
        if min_score is None
        else min_score
    )

    chunks = [
        {
            "text": point.payload["text"],
            "document_id": point.payload["document_id"],
            "chunk_index": point.payload["chunk_index"],
            "score": point.score,
        }
        for point in results.points
    ]

    relevant_chunks = [
        chunk for chunk in chunks
        if chunk["score"] >= relevance_floor
    ]

    logger.info(
        "vector_search tenant_id=%s candidates=%d relevant=%d min_score=%.2f",
        tenant_id,
        len(chunks),
        len(relevant_chunks),
        relevance_floor,
    )

    return relevant_chunks