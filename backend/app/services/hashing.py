import hashlib
 
 
def compute_file_hash(content: bytes) -> str:
    """SHA-256 hex digest of raw file bytes — used to detect duplicate uploads
    within a tenant regardless of filename."""
    return hashlib.sha256(content).hexdigest()
