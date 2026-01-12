"""Module with routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.codec import CodecError, decode_signature, encode_signature
from src.config import AppConfig, get_config
from src.hmac_service import HMACSigner, hmac_service
from src.logger import get_logger
from src.models import SignRequest, VerifyRequest

router = APIRouter()
logger = get_logger(__name__)


def _validate_msg(msg: str, config: AppConfig) -> None:
    if not isinstance(msg, str) or msg == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="invalid_msg")
    if len(msg.encode("utf-8")) > config.max_msg_size_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="payload_too_large"
        )


@router.post("/sign")
async def sign(
    request: SignRequest,
    hmac_service: Annotated[HMACSigner, Depends(hmac_service)],
) -> dict[str, str]:
    """
    Sign handler.

    :param request: Request model.
    :param hmac_service: HMAC service dependency.
    :return: URL safe signature for message.
    :raises HTTPException: If message invalid (empty or very big).
    """
    config = get_config()
    _validate_msg(request.msg, config)
    msg_len = len(request.msg.encode("utf-8"))
    signature_bytes = hmac_service.sign(request.msg)
    signature = encode_signature(signature_bytes)
    logger.info(f"sign ok len={msg_len}")
    return {"signature": signature}


@router.post("/verify")
async def verify(
    request: VerifyRequest,
    hmac_service: Annotated[HMACSigner, Depends(hmac_service)],
) -> dict[str, bool]:
    """
    Verify message with signature handler.

    :param request: Request model.
    :param hmac_service: HMAC service dependency.
    :return: VerifyResponse model.
    :raises HTTPException: If invalid message or signature.
    """
    config = get_config()
    _validate_msg(request.msg, config)
    try:
        signature_bytes = decode_signature(request.signature)
    except CodecError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="invalid_signature_format"
        )
    if len(signature_bytes) > config.max_msg_size_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="payload_too_large"
        )

    ok = hmac_service.verify(request.msg, signature_bytes)
    logger.info(f"verify len={len(request.msg.encode('utf-8'))} ok={ok}")
    return {"ok": ok}
