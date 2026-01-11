"""Main module for running FastAPI application."""

import uvicorn

from src.app import app
from src.config import get_config


if __name__ == "__main__":
    config = get_config()
    uvicorn.run(app, host=config.listen_host, port=config.listen_port)
