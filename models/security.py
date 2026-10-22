import hashlib


def hash_password(password):
    """Turn a password into a scrambled string (SHA-256 hash)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()