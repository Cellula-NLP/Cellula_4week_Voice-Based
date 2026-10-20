"""FastAPI Application Entry Point."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
setup_logger()

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    description="Voice-Based Data Analysis System using FastAPI, Whisper, and LLMs."
)

# Set up CORS (Allows a frontend React/Vue app to talk to this API later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix=settings.api_v1_str)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Voice Data Analyst API is running!"}

if __name__ == "__main__":
    import uvicorn
    # Run: python app/main.py
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)