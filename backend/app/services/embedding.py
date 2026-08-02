from sentence_transformers import SentenceTransformer

from app.core.logging_config import get_logger

logger = get_logger(__name__)

_model: SentenceTransformer | None = None

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def get_model() -> SentenceTransformer:
    """Lazily loads the embedding model once, reused across all requests."""
    global _model
    if _model is None:
        logger.info("embedding_model_loading model=BAAI/bge-small-en-v1.5")
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        logger.info("embedding_model_loaded")
    return _model


def embed_chunks(texts: list[str]) -> list[list[float]]:
    """Embeds document chunks (no prefix needed for the passage side)."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """Embeds a user's search question. BGE recommends a prefix for queries specifically."""
    model = get_model()
    embedding = model.encode(QUERY_PREFIX + text, normalize_embeddings=True)
    return embedding.tolist()

