import uuid

from qdrant_client.models import Distance, PointStruct, VectorParams

from app.db.qdrant_client import qdrant
from app.core.logging_config import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "document_chunks"
VECTOR_SIZE = 384  # bge-small-en-v1.5 output dimension


def ensure_collection_exists() -> None:
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        logger.info(f"qdrant_collection_created name={COLLECTION_NAME}")


def store_chunks(document_id: str, tenant_id: str, chunks: list[str], embeddings: list[list[float]]) -> int:
    ensure_collection_exists()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "document_id": document_id,
                "tenant_id": tenant_id,
                "chunk_index": i,
                "text": chunk,
            },
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)


def search_chunks(query_embedding: list[float], tenant_id: str, top_k: int = 5, document_id: str | None = None):
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        return []

    from qdrant_client.models import Filter, FieldCondition, MatchValue
    must_conditions = [FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
    if document_id:
        must_conditions.append(FieldCondition(key="document_id", match=MatchValue(value=document_id)))

    query_filter = Filter(must=must_conditions)

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    )

    return [
        {
            "text": point.payload["text"],
            "document_id": point.payload["document_id"],
            "chunk_index": point.payload["chunk_index"],
            "score": point.score,
        }
        for point in results.points
    ]
