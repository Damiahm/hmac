"""Module with HMAC sign functions."""

from __future__ import annotations

import hmac
import hashlib
from typing import Annotated

from fastapi import Depends

from src.config import AppConfig, get_config


class HMACSigner:
    """Class for HMAC sign and verify signature."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if self.config.hmac_alg != "SHA256":
            raise ValueError("Unsupported HMAC algorithm")
        self._key = self.config.secret

    def sign(self, msg: str) -> bytes:
        """
        Sign message with HMAC algorithm.

        :param msg: Message for sign.
        :return: Signature bytes.
        """
        if not isinstance(msg, str):
            raise TypeError("Message must be a string")
        msg_bytes = msg.encode("utf-8")
        return hmac.new(self._key, msg_bytes, hashlib.sha256).digest()

    def verify(self, msg: str, signature: bytes) -> bool:
        """
        Verify message signature with HMAC algorithm.

        :param msg: Message for verify.
        :param signature: Signature for verify.
        :return: True if signature for message valid, else False.
        """
        if not isinstance(signature, (bytes, bytearray)):
            return False
        expected = self.sign(msg)
        return hmac.compare_digest(expected, signature)


def hmac_service(
    config: Annotated[AppConfig, Depends(get_config)],
) -> HMACSigner:
    """
    Fabric for signer.

    :return: Initialized HMACSigner object.
    """
    return HMACSigner(config)
