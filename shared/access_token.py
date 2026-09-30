"""Signed per-character inventory links.

The bot issues a token only to the Mastodon account that owns a character, and
the API accepts write/read requests for that character only when the token is
valid. Tokens are ``<payload>.<signature>`` where the payload is base64url JSON
``{"n": character_name, "exp": unix_seconds}`` and the signature is
HMAC-SHA256(secret, payload). Rotating the secret revokes every issued link.
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Optional

MIN_SECRET_LENGTH = 32


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(payload: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest()
    return _b64encode(digest)


def is_valid_secret(secret: Optional[str]) -> bool:
    """A usable secret must be long enough to resist brute force."""
    return bool(secret) and len(secret) >= MIN_SECRET_LENGTH


def issue_token(character_name: str, secret: str, ttl_seconds: int, now: Optional[float] = None) -> str:
    """Create a signed token that grants access to one character until it expires."""
    if not is_valid_secret(secret):
        raise ValueError(f"secret must be at least {MIN_SECRET_LENGTH} characters")
    if not character_name:
        raise ValueError("character_name is required")
    issued_at = time.time() if now is None else now
    body = json.dumps({"n": character_name, "exp": int(issued_at + ttl_seconds)}, ensure_ascii=False)
    payload = _b64encode(body.encode("utf-8"))
    return f"{payload}.{_sign(payload, secret)}"


def verify_token(token: Optional[str], secret: Optional[str], now: Optional[float] = None) -> Optional[str]:
    """Return the character name if the token is authentic and unexpired, else None."""
    if not token or not is_valid_secret(secret):
        return None
    payload, sep, signature = token.partition(".")
    if not sep or not payload or not signature:
        return None
    if not hmac.compare_digest(_sign(payload, secret), signature):
        return None
    try:
        data = json.loads(_b64decode(payload).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    name, expires_at = data.get("n"), data.get("exp")
    if not isinstance(name, str) or not name or not isinstance(expires_at, int):
        return None
    current = time.time() if now is None else now
    if current >= expires_at:
        return None
    return name
