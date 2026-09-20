CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
 
 
def chunk_params_label() -> str:
    """Stamp stored on a Document to record which params it was chunked with.
    Compared against this at upload time to decide whether reprocessing
    would actually change anything."""
    return f"{CHUNK_SIZE}/{CHUNK_OVERLAP}"
 
 
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Splits text into overlapping chunks of roughly chunk_size characters.
    Overlap ensures we don't lose meaning at chunk boundaries.
    """
    text = text.strip()
    if not text:
        return []
 
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
 
    return chunks

