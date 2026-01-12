"""Module with config utils."""

from __future__ import annotations

import base64
import binascii
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from constants import B64URL_LEN_K

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
CONFIG_ENV_VAR = "CONFIG_PATH"

_PORT_RANGE = (1, 65535)


class ConfigError(RuntimeError):
    """Raised when configuration is missing or invalid."""


@dataclass(frozen=True)
class AppConfig:
    """Validated application config."""

    hmac_alg: str
    secret: bytes
    log_level: str
    listen: str
    listen_host: str
    listen_port: int
    max_msg_size_bytes: int


def _ensure_exists(path: Path) -> None:
    if not path.exists():
        raise ConfigError(f"Config file not found at {path}")
    if not path.is_file():
        raise ConfigError(f"Config path is not a file: {path}")


def _decode_secret(secret_raw: str) -> bytes:
    if not isinstance(secret_raw, str) or not secret_raw:
        raise ConfigError("Secret must be a non-empty string")
    padding = "=" * (-len(secret_raw) % B64URL_LEN_K)
    try:
        secret = base64.urlsafe_b64decode(secret_raw + padding)
    except (binascii.Error, ValueError) as exc:
        raise ConfigError("Secret must be base64url encoded") from exc
    if not secret:
        raise ConfigError("Secret decoded to empty bytes")
    return secret


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config file is not valid JSON: {exc}") from exc


def _parse_listen(listen: str) -> tuple[str, int]:
    if not isinstance(listen, str) or ":" not in listen:
        raise ConfigError("listen must be in format host:port")
    host, port_str = listen.rsplit(":", 1)
    try:
        port = int(port_str)
    except ValueError as exc:
        raise ConfigError("listen port must be integer") from exc
    if port < _PORT_RANGE[0] or port > _PORT_RANGE[1]:
        raise ConfigError(f"listen port must be in {_PORT_RANGE[0]}-{_PORT_RANGE[1]} range")
    return host, port


def load_config(path: Path | str | None = None) -> AppConfig:
    """
    Load and validate config from file.

    :param path: Optional explicit config path.
    :raises ConfigError: If config missing or invalid.
    """
    config_path = (
        Path(path)
        if path
        else Path(os.environ.get(CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH))
    )
    _ensure_exists(config_path)
    raw = _read_json(config_path)
    try:
        hmac_alg = raw["hmac_alg"]
        secret_raw = raw["secret"]
        log_level = raw["log_level"]
        listen = raw["listen"]
        max_msg_size_bytes = raw["max_msg_size_bytes"]
    except KeyError as exc:
        raise ConfigError(f"Missing required config key: {exc.args[0]}") from exc

    if not isinstance(hmac_alg, str) or hmac_alg.upper() != "SHA256":
        raise ConfigError("Only HMAC-SHA256 is supported")
    secret = _decode_secret(secret_raw)
    if not isinstance(log_level, str):
        raise ConfigError("log_level must be string")
    if not isinstance(listen, str) or ":" not in listen:
        raise ConfigError("listen must be in format host:port")
    if not isinstance(max_msg_size_bytes, int) or max_msg_size_bytes <= 0:
        raise ConfigError("max_msg_size_bytes must be positive integer")

    listen_host, listen_port = _parse_listen(listen)

    return AppConfig(
        hmac_alg=hmac_alg.upper(),
        secret=secret,
        log_level=log_level.lower(),
        listen=listen,
        listen_host=listen_host,
        listen_port=listen_port,
        max_msg_size_bytes=max_msg_size_bytes,
    )


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Singleton accessor for config."""
    return load_config()


def reset_config_cache() -> None:
    """Reset cached config (useful for tests)."""
    get_config.cache_clear()
