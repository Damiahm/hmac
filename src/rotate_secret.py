"""Utility to rotate HMAC secret in config.json."""

from __future__ import annotations

import base64
import json
import secrets
from pathlib import Path
from typing import Any

from src.config import CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH, load_config
from src.logger import get_logger


_DEFAULT_SECRET_BYTES = 32


logger = get_logger(__name__)


def _generate_secret(bytes_len: int = _DEFAULT_SECRET_BYTES) -> str:
    """Generate base64url secret without padding."""
    raw = secrets.token_bytes(bytes_len)
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def rotate_secret(path: Path | str | None = None) -> str:
    """
    Rotate secret in config file.

    :param path: Optional explicit config path.
    :return: New base64url secret string.
    """
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    config = load_config(config_path)  # validate existing config

    new_secret = _generate_secret()
    config_dict: dict[str, Any] = {
        "hmac_alg": config.hmac_alg,
        "secret": new_secret,
        "log_level": config.log_level,
        "listen": config.listen,
        "max_msg_size_bytes": config.max_msg_size_bytes,
    }
    config_path.write_text(json.dumps(config_dict, indent=2), encoding="utf-8")
    logger.info(f"Secret rotated and written to {config_path}")
    return new_secret


if __name__ == "__main__":
    target_path = Path(
        __import__("os").environ.get(CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH)
    )
    new_secret = rotate_secret(target_path)
    print(f"New secret (base64url, no padding): {new_secret}")
