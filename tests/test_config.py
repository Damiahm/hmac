import json
from pathlib import Path

import pytest

from src.config import (
    CONFIG_ENV_VAR,
    ConfigError,
    AppConfig,
    load_config,
    reset_config_cache,
)


def make_config_dict(secret: str = "c2VjdXJlLXRlc3Qtc2VjcmV0") -> dict:
    return {
        "hmac_alg": "SHA256",
        "secret": secret,
        "log_level": "info",
        "listen": "0.0.0.0:8080",
        "max_msg_size_bytes": 1024,
    }


def write_config(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def config_path(tmp_path, monkeypatch) -> Path:
    path = tmp_path / "config.json"
    write_config(path, make_config_dict())
    monkeypatch.setenv(CONFIG_ENV_VAR, str(path))
    reset_config_cache()
    return path


def test_load_config_success(config_path: Path) -> None:
    cfg = load_config(config_path)
    assert isinstance(cfg, AppConfig)
    assert cfg.hmac_alg == "SHA256"
    assert cfg.secret
    assert cfg.listen_host == "0.0.0.0"
    assert cfg.listen_port == 8080


def test_invalid_secret(monkeypatch, tmp_path) -> None:
    path = tmp_path / "config.json"
    write_config(path, make_config_dict(secret="@@@"))
    monkeypatch.setenv(CONFIG_ENV_VAR, str(path))
    reset_config_cache()
    with pytest.raises(ConfigError):
        load_config()


def test_missing_key(monkeypatch, tmp_path) -> None:
    path = tmp_path / "config.json"
    data = make_config_dict()
    data.pop("secret")
    write_config(path, data)
    monkeypatch.setenv(CONFIG_ENV_VAR, str(path))
    reset_config_cache()
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_listen(monkeypatch, tmp_path) -> None:
    path = tmp_path / "config.json"
    bad_cfg = make_config_dict()
    bad_cfg["listen"] = "bad"
    write_config(path, bad_cfg)
    monkeypatch.setenv(CONFIG_ENV_VAR, str(path))
    reset_config_cache()
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_hmac_alg(monkeypatch, tmp_path) -> None:
    path = tmp_path / "config.json"
    bad_cfg = make_config_dict()
    bad_cfg["hmac_alg"] = "SHA1"
    write_config(path, bad_cfg)
    monkeypatch.setenv(CONFIG_ENV_VAR, str(path))
    reset_config_cache()
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_max_msg_size(monkeypatch, tmp_path) -> None:
    path = tmp_path / "config.json"
    bad_cfg = make_config_dict()
    bad_cfg["max_msg_size_bytes"] = -1
    write_config(path, bad_cfg)
    monkeypatch.setenv(CONFIG_ENV_VAR, str(path))
    reset_config_cache()
    with pytest.raises(ConfigError):
        load_config()


def test_missing_config_file(monkeypatch, tmp_path) -> None:
    missing_path = tmp_path / "no_config.json"
    monkeypatch.setenv(CONFIG_ENV_VAR, str(missing_path))
    reset_config_cache()
    with pytest.raises(ConfigError):
        load_config()
