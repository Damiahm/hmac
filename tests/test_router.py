import json

import pytest
from fastapi.testclient import TestClient

from src.config import CONFIG_ENV_VAR, reset_config_cache


def make_config_dict(secret: str = "c2VjcmV0LXRlc3Qtc2VjcmV0") -> dict:
    return {
        "hmac_alg": "SHA256",
        "secret": secret,
        "log_level": "info",
        "listen": "0.0.0.0:8080",
        "max_msg_size_bytes": 32,
    }


@pytest.fixture
def client(monkeypatch, tmp_path) -> TestClient:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(make_config_dict()), encoding="utf-8")
    monkeypatch.setenv(CONFIG_ENV_VAR, str(config_path))
    reset_config_cache()

    from src.app import app

    return TestClient(app)


def test_sign_and_verify_success(client: TestClient) -> None:
    resp = client.post("/sign", json={"msg": "hello"})
    assert resp.status_code == 200
    signature = resp.json()["signature"]

    verify_resp = client.post("/verify", json={
        "msg": "hello", 
        "signature": signature
    })
    assert verify_resp.status_code == 200
    assert verify_resp.json() == {"ok": True}


def test_verify_wrong_signature(client: TestClient) -> None:
    sig_resp = client.post("/sign", json={"msg": "hello"})
    signature = sig_resp.json()["signature"]

    bad_signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    verify_resp = client.post(
        "/verify", json={
            "msg": "hello", 
            "signature": bad_signature
        }
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json() == {"ok": False}


def test_verify_wrong_message(client: TestClient) -> None:
    sig_resp = client.post("/sign", json={"msg": "hello"})
    signature = sig_resp.json()["signature"]
    verify_resp = client.post("/verify", json={
        "msg": "hello!", 
        "signature": signature
    })
    assert verify_resp.status_code == 200
    assert verify_resp.json() == {"ok": False}


def test_invalid_signature_format(client: TestClient) -> None:
    verify_resp = client.post("/verify", json={
        "msg": "hello", 
        "signature": "@@@"
    })
    assert verify_resp.status_code == 400
    assert verify_resp.json()["detail"] == "invalid_signature_format"


def test_empty_message_rejected(client: TestClient) -> None:
    resp = client.post("/sign", json={"msg": ""})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "invalid_msg"


def test_payload_too_large(client: TestClient) -> None:
    long_msg = "a" * 64  # greater than max_msg_size_bytes=32
    resp = client.post("/sign", json={"msg": long_msg})
    assert resp.status_code == 413
    assert resp.json()["detail"] == "payload_too_large"
