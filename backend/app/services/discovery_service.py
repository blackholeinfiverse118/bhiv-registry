"""
BHIV Registry — Discovery Service

Provides advanced dataset discovery capabilities for the TANTRA ecosystem.
This is the primary interface for external systems to find and validate datasets.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.registry import (
    Dataset, DatasetSchema, ProvenanceRecord,
    TrustLevel, ReplayCompatibility,
    SimulationCompatibility, DatasetStatus
)


class DiscoveryService:

    @staticmethod
    async def get_registry_summary(db: AsyncSession) -> Dict[str, Any]:
        """
        Returns a high-level summary of the entire registry.
        Useful for dashboards and health monitoring.
        """
        # Total datasets
        total = await db.scalar(select(func.count(Dataset.id)))

        # Count by trust level
        trust_counts = {}
        for level in TrustLevel:
            count = await db.scalar(
                select(func.count(Dataset.id))
                .where(Dataset.trust_level == level)
            )
            trust_counts[level.value] = count

        # Count by replay compatibility
        replay_counts = {}
        for level in ReplayCompatibility:
            count = await db.scalar(
                select(func.count(Dataset.id))
                .where(Dataset.replay_compatibility == level)
            )
            replay_counts[level.value] = count

        # Count by simulation compatibility
        simulation_counts = {}
        for level in SimulationCompatibility:
            count = await db.scalar(
                select(func.count(Dataset.id))
                .where(Dataset.simulation_compatibility == level)
            )
            simulation_counts[level.value] = count

        # Count by domain
        domain_result = await db.execute(
            select(Dataset.domain_primary, func.count(Dataset.id))
            .group_by(Dataset.domain_primary)
            .order_by(func.count(Dataset.id).desc())
        )
        domain_counts = {row[0]: row[1] for row in domain_result.fetchall()}

        # Count by status
        status_counts = {}
        for status in DatasetStatus:
            count = await db.scalar(
                select(func.count(Dataset.id))
                .where(Dataset.status == status)
            )
            status_counts[status.value] = count

        return {
            "total_datasets": total,
            "by_trust_level": trust_counts,
            "by_replay_compatibility": replay_counts,
            "by_simulation_compatibility": simulation_counts,
            "by_domain": domain_counts,
            "by_status": status_counts,
        }

    @staticmethod
    async def find_replay_safe_datasets(
        db: AsyncSession,
        domain: Optional[str] = None
    ) -> List[Dataset]:
        """
        Find all datasets that are safe for replay workflows.
        Optionally filter by domain.
        """
        conditions = [
            Dataset.replay_compatibility.in_([
                ReplayCompatibility.FULL,
                ReplayCompatibility.PARTIAL
            ]),
            Dataset.status == DatasetStatus.ACTIVE
        ]
        if domain:
            conditions.append(Dataset.domain_primary.ilike(f"%{domain}%"))

        result = await db.execute(
            select(Dataset)
            .where(and_(*conditions))
            .order_by(Dataset.registered_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def find_simulation_ready_datasets(
        db: AsyncSession,
        domain: Optional[str] = None
    ) -> List[Dataset]:
        """
        Find all datasets suitable for simulation use cases.
        """
        conditions = [
            Dataset.simulation_compatibility.in_([
                SimulationCompatibility.NATIVE,
                SimulationCompatibility.COMPATIBLE
            ]),
            Dataset.status == DatasetStatus.ACTIVE
        ]
        if domain:
            conditions.append(Dataset.domain_primary.ilike(f"%{domain}%"))

        result = await db.execute(
            select(Dataset)
            .where(and_(*conditions))
            .order_by(Dataset.registered_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def find_trusted_datasets(
        db: AsyncSession,
        domain: Optional[str] = None
    ) -> List[Dataset]:
        """
        Find all datasets at TRUSTED or VERIFIED trust level.
        These are safe for intelligence workflows.
        """
        conditions = [
            Dataset.trust_level.in_([
                TrustLevel.TRUSTED,
                TrustLevel.VERIFIED
            ]),
            Dataset.status == DatasetStatus.ACTIVE
        ]
        if domain:
            conditions.append(Dataset.domain_primary.ilike(f"%{domain}%"))

        result = await db.execute(
            select(Dataset)
            .where(and_(*conditions))
            .order_by(Dataset.trust_level.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def find_datasets_by_owner_team(
        db: AsyncSession,
        owner_team: str
    ) -> List[Dataset]:
        """Find all datasets owned by a specific team."""
        result = await db.execute(
            select(Dataset)
            .where(
                Dataset.owner_team.ilike(f"%{owner_team}%"),
                Dataset.status == DatasetStatus.ACTIVE
            )
            .order_by(Dataset.registered_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_quarantined_datasets(
        db: AsyncSession
    ) -> List[Dataset]:
        """
        Get all quarantined datasets.
        These need immediate attention — not safe for any workflow.
        """
        result = await db.execute(
            select(Dataset)
            .where(Dataset.trust_level == TrustLevel.QUARANTINE)
            .order_by(Dataset.updated_at.desc())
        )
        return result.scalars().all()