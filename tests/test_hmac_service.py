import pytest

from src.config import AppConfig
from src.hmac_service import HMACSigner


def make_config() -> AppConfig:
    return AppConfig(
        hmac_alg="SHA256",
        secret=b"static-test-secret",
        log_level="info",
        listen="0.0.0.0:8080",
        listen_host="0.0.0.0",
        listen_port=8080,
        max_msg_size_bytes=1024,
    )


def test_sign_deterministic() -> None:
    signer = HMACSigner(make_config())
    sig1 = signer.sign("hello")
    sig2 = signer.sign("hello")
    assert sig1 == sig2


def test_verify_success() -> None:
    signer = HMACSigner(make_config())
    msg = "hello"
    sig = signer.sign(msg)
    assert signer.verify(msg, sig) is True


def test_verify_failure_with_different_message() -> None:
    signer = HMACSigner(make_config())
    msg = "hello"
    sig = signer.sign(msg)
    assert signer.verify("different message", sig) is False


def test_verify_failure_with_invalid_signature() -> None:
    signer = HMACSigner(make_config())
    assert signer.verify("hello", b"bad") is False
    assert signer.verify("hello", "not-bytes") is False  # type: ignore[arg-type]


def test_sign_non_str_raises() -> None:
    signer = HMACSigner(make_config())
    with pytest.raises(TypeError):
        signer.sign(123)  # type: ignore[arg-type]
