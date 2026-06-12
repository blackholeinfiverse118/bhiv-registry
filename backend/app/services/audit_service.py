"""
BHIV Registry — Audit Log Service

Provides visibility into API consumption for ecosystem
integration evidence. Read-only — logs are written by middleware.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.registry import AuditLog, ApiKey


class AuditService:

    @staticmethod
    async def get_recent_logs(
        db: AsyncSession,
        limit: int = 50,
        owner: Optional[str] = None
    ) -> List[AuditLog]:
        query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        if owner:
            query = query.where(AuditLog.api_key_owner == owner)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_consumption_summary(db: AsyncSession):
        """
        Summarize API consumption by owner — who has called
        the registry, how many times, what endpoints.
        """
        result = await db.execute(
            select(
                AuditLog.api_key_owner,
                AuditLog.path,
                func.count(AuditLog.id).label("call_count"),
                func.max(AuditLog.timestamp).label("last_called")
            )
            .where(AuditLog.api_key_owner.isnot(None))
            .group_by(AuditLog.api_key_owner, AuditLog.path)
            .order_by(func.max(AuditLog.timestamp).desc())
        )
        rows = result.all()
        return [
            {
                "owner": row[0],
                "endpoint": row[1],
                "call_count": row[2],
                "last_called": row[3].isoformat() if row[3] else None
            }
            for row in rows
        ]

    @staticmethod
    async def list_api_keys(db: AsyncSession) -> List[ApiKey]:
        result = await db.execute(select(ApiKey).order_by(ApiKey.created_at.asc()))
        return result.scalars().all()