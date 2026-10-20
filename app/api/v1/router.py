"""Aggregates all v1 endpoints."""
from fastapi import APIRouter
from app.api.v1.endpoints import audio, query, dataset

api_router = APIRouter()
api_router.include_router(dataset.router, prefix="/dataset", tags=["Dataset"])
api_router.include_router(audio.router, prefix="/audio", tags=["Audio"])
api_router.include_router(query.router, prefix="/query", tags=["Query"])