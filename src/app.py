"""Module with FastAPI application."""

from fastapi import FastAPI

from src.router import router

app = FastAPI()
app.include_router(router)
