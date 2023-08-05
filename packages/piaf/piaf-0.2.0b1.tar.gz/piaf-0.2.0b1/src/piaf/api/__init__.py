# coding: utf-8
"""
The base module for the Web API part of piaf.

It contains the `FastAPI` application and it imports routes from the :mod:`piaf.api.routes` module.
The application server can be launched using `uvicorn` (or any other production server).
"""
from __future__ import annotations

from fastapi import FastAPI

from piaf.api.managers import ptf_manager
from piaf.api.routes import app_v1

# Main application, empty
app = FastAPI()

# API version 1
app.include_router(app_v1, prefix="/v1")


@app.on_event("startup")
async def initialize_connection() -> None:
    """Initialize the Redis connection used by the WebAPI."""
    await ptf_manager.initialize()


@app.on_event("shutdown")
async def close_connection() -> None:
    """Close the Redis connection before stopping the server."""
    await ptf_manager.db.close()
