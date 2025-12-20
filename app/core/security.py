import bcrypt
import hashlib
import base64

def _pre_hash(password: str) -> bytes:
    """
    Bcrypt has a strict 72-byte limit on input.
    We hash the raw password with SHA-256 first (32 bytes)
    and base64 encode it (~44 bytes).
    This allows passwords of ANY length to be secure.
    """
    # 1. SHA-256 Hash (Returns 32 bytes)
    digest = hashlib.sha256(password.encode('utf-8')).digest()
    # 2. Base64 Encode (Returns bytes like b'TXkg...')
    return base64.b64encode(digest)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if the typed password matches the stored hash."""
    # Convert DB string back to bytes for bcrypt
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password

    # Pre-hash the input so it matches the format used during creation
    safe_password = _pre_hash(plain_password)
    
    # Check
    return bcrypt.checkpw(safe_password, hashed_bytes)

def get_password_hash(password: str) -> str:
    """Converts a plain password into a secure bcrypt hash."""
    # 1. Compress length
    safe_password = _pre_hash(password)
    # 2. Generate Salt and Hash
    hashed = bcrypt.hashpw(safe_password, bcrypt.gensalt())
    # 3. Return as string for database storage
    return hashed.decode('utf-8')
