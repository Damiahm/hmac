"""Module with codec functions."""

from __future__ import annotations

import base64
import binascii
import re
from typing import Final

from .constants import B64URL_LEN_K

_B64URL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]+$")

class CodecError(ValueError):
    """Raised when signature encoding/decoding fails."""


def encode_signature(raw: bytes) -> str:
    """Encode signature bytes into base64url string without padding."""
    if not isinstance(raw, (bytes, bytearray)):
        raise CodecError("Signature must be bytes")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_signature(signature: str) -> bytes:
    """Decode base64url signature string into bytes with validation."""
    if not isinstance(signature, str) or not signature:
        raise CodecError("Signature must be a non-empty string")
    if not _B64URL_RE.fullmatch(signature):
        raise CodecError("Signature must contain only base64url characters")

    padding = "=" * (-len(signature) % B64URL_LEN_K)
    try:
        decoded = base64.urlsafe_b64decode(signature + padding)
    except (binascii.Error, ValueError) as exc:
        raise CodecError("Signature is not valid base64url") from exc

    if not decoded:
        raise CodecError("Decoded signature is empty")
    return decoded
