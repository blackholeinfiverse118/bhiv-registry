"""
BHIV Registry — Audit and Consumption Visibility Endpoints

GET /audit/logs              -> Recent API call logs
GET /audit/consumption        -> Consumption summary by consumer
GET /audit/api-keys           -> List registered API keys (no secrets)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.base import get_db
from app.services.audit_service import AuditService
from app.schemas.registry import AuditLogResponse, ApiKeyResponse

router = APIRouter(prefix="/audit", tags=["Audit and Consumption"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    owner: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get recent API call logs. Filter by api_key_owner if provided."""
    return await AuditService.get_recent_logs(db, limit, owner)


@router.get("/consumption")
async def get_consumption_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Summary of registry consumption by consumer and endpoint.
    This is the primary evidence source for ecosystem integration.
    """
    return await AuditService.get_consumption_summary(db)


@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db)
):
    """List all registered API keys (without exposing key values)."""
    return await AuditService.list_api_keys(db)