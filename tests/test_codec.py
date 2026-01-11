import pytest

from src.codec import CodecError, decode_signature, encode_signature


def test_encode_decode_roundtrip() -> None:
    raw = b"\x01\x02test-bytes"
    encoded = encode_signature(raw)
    assert "=" not in encoded  # no padding
    decoded = decode_signature(encoded)
    assert decoded == raw


@pytest.mark.parametrize("value", ["", "@@@", "abc=", "abc/+", 123])
def test_decode_invalid_raises(value: str) -> None:
    with pytest.raises(CodecError):
        decode_signature(value)
