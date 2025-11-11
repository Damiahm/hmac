"""Main module for run FastAPI application"""

import uvicorn

from src.app import app 


if __name__ == '__main__':
    host = '' # TODO: хост должен получаться из config.json
    port = 1  # TODO: порт должен получаться из config.json
    uvicorn.run(app, host=host, port=int(port))
