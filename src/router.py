"""Module with routes"""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.hmac_service import HMACSigner, hmac_service
from src.models import SignRequest, VerifyRequest, VerifyResponse

router = APIRouter()


# TODO: напишите логику для ручки подписи
@router.post('/sign')
async def sign(request: SignRequest, hmac_service: Annotated[HMACSigner, Depends(hmac_service)]) -> str:
    """
    Sign handler.

    :param request: Request model.
    :param hmac_service: HMAC service dependency.
    :return: URL safe signature for message.
    :raises HTTPException: If message invalid (empty or very big).
    """
    pass


# TODO: напишите логику для ручки проверки подписи
@router.post('/verify')
async def verify(request: VerifyRequest, hmac_service: Annotated[HMACSigner, Depends(hmac_service)]) -> VerifyResponse:
    """
    Verify message with signature handler.

    :param request: Request model.
    :param hmac_service: HMAC service dependency.
    :return: VerifyResponse model.
    :raises HTTPException: If invalid message or signature.
    """
    pass
