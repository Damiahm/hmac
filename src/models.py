"""Module with request/response models."""

from pydantic import BaseModel


class SignRequest(BaseModel):
    """Model for /sign request."""

    msg: str | None = None


class VerifyRequest(BaseModel):
    """Model for /verify request."""

    msg: str | None = None
    signature: str | None = None
