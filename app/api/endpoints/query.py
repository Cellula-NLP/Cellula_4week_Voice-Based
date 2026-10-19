# app/api/v1/endpoints/query.py
"""Endpoints for SQL Analysis."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_sql_service
from app.domain.models import AnalyzeRequest, AnalyzeResponse
from app.services.sql_service import SQLService

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    sql_service: SQLService = Depends(get_sql_service),
):
    """
    Takes transcribed text and a table name, generates SQL, executes it,
    and returns the data along with an explanation.
    """
    try:
        # SQLService is async because it uses the async OpenRouterClient
        result = await sql_service.analyze(
            user_text=request.user_text,
            table_name=request.dataset_name
        )
        return AnalyzeResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))