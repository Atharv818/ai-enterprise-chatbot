import uuid

_query_cache: dict[str, str] = {}


def store_query(sql: str) -> str:
    query_id = str(uuid.uuid4())
    _query_cache[query_id] = sql
    return query_id


def get_query(query_id: str) -> str | None:
    return _query_cache.get(query_id)

