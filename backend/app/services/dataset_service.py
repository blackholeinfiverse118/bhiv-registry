"""
BHIV Registry — Dataset Service Layer
"""

from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.models.registry import (
    Dataset, ProvenanceRecord, DatasetSchema,
    TrustLevel, DatasetStatus
)
from app.schemas.registry import (
    DatasetRegisterRequest, DatasetUpdateRequest,
    DatasetSearchFilters, TrustUpdateRequest,
    ProvenanceCreateRequest
)


class DatasetService:

    @staticmethod
    async def register_dataset(
        db: AsyncSession,
        payload: DatasetRegisterRequest,
        registered_by: str = "system"
    ) -> Dataset:
        existing = await db.execute(
            select(Dataset).where(Dataset.canonical_id == payload.canonical_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Dataset with canonical_id '{payload.canonical_id}' already exists.")

        ingestion_ref = None
        if payload.ingestion_reference:
            ingestion_ref = payload.ingestion_reference.model_dump()

        dataset = Dataset(
            canonical_id=payload.canonical_id,
            dataset_name=payload.dataset_name,
            description=payload.description,
            version=payload.version,
            source_system=payload.source_system,
            source_location=payload.source_location,
            owner_name=payload.owner_name,
            owner_team=payload.owner_team,
            owner_contact=payload.owner_contact,
            domain_primary=payload.domain_primary,
            domain_tags=payload.domain_tags,
            trust_level=payload.trust_level,
            replay_compatibility=payload.replay_compatibility,
            replay_notes=payload.replay_notes,
            simulation_compatibility=payload.simulation_compatibility,
            simulation_notes=payload.simulation_notes,
            ingestion_reference=ingestion_ref,
            extended_metadata=payload.extended_metadata,
        )
        db.add(dataset)
        await db.flush()

        provenance = ProvenanceRecord(
            dataset_id=dataset.id,
            event_type="ORIGIN",
            source_system=payload.source_system,
            source_reference=payload.source_location,
            trust_at_event=payload.trust_level,
            recorded_by=registered_by,
            notes=f"Initial registration of dataset '{payload.canonical_id}'",
            is_replay_safe=(payload.replay_compatibility.value != "NONE"),
        )
        db.add(provenance)
        await db.flush()
        return dataset

    @staticmethod
    async def get_by_id(db: AsyncSession, dataset_id: UUID) -> Optional[Dataset]:
        result = await db.execute(
            select(Dataset)
            .options(selectinload(Dataset.provenance_records))
            .where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_canonical_id(db: AsyncSession, canonical_id: str) -> Optional[Dataset]:
        result = await db.execute(
            select(Dataset).where(Dataset.canonical_id == canonical_id.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def search_datasets(
        db: AsyncSession,
        filters: DatasetSearchFilters
    ) -> tuple[List[Dataset], int]:
        query = select(Dataset)
        conditions = []

        if filters.status:
            conditions.append(Dataset.status == filters.status)
        if filters.domain_primary:
            conditions.append(Dataset.domain_primary.ilike(f"%{filters.domain_primary}%"))
        if filters.trust_level:
            conditions.append(Dataset.trust_level == filters.trust_level)
        if filters.replay_compatibility:
            conditions.append(Dataset.replay_compatibility == filters.replay_compatibility)
        if filters.simulation_compatibility:
            conditions.append(Dataset.simulation_compatibility == filters.simulation_compatibility)
        if filters.owner_team:
            conditions.append(Dataset.owner_team.ilike(f"%{filters.owner_team}%"))
        if filters.search_text:
            search = f"%{filters.search_text}%"
            conditions.append(
                or_(
                    Dataset.dataset_name.ilike(search),
                    Dataset.description.ilike(search),
                    Dataset.canonical_id.ilike(search),
                )
            )
        if filters.domain_tags:
            for tag in filters.domain_tags:
                conditions.append(Dataset.domain_tags.any(tag))

        if conditions:
            query = query.where(and_(*conditions))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size).order_by(Dataset.registered_at.desc())

        result = await db.execute(query)
        return result.scalars().all(), total

    @staticmethod
    async def update_dataset(
        db: AsyncSession,
        dataset_id: UUID,
        payload: DatasetUpdateRequest
    ) -> Optional[Dataset]:
        dataset = await DatasetService.get_by_id(db, dataset_id)
        if not dataset:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        if "ingestion_reference" in update_data and update_data["ingestion_reference"]:
            update_data["ingestion_reference"] = payload.ingestion_reference.model_dump()

        for field, value in update_data.items():
            setattr(dataset, field, value)

        await db.flush()
        return dataset

    @staticmethod
    async def update_trust(
        db: AsyncSession,
        dataset_id: UUID,
        payload: TrustUpdateRequest
    ) -> Optional[Dataset]:
        from datetime import datetime, timezone
        dataset = await DatasetService.get_by_id(db, dataset_id)
        if not dataset:
            return None

        old_trust = dataset.trust_level
        dataset.trust_level = payload.trust_level
        dataset.trust_verified_by = payload.verified_by
        dataset.trust_verified_at = datetime.now(timezone.utc)
        if payload.governance_notes:
            dataset.governance_notes = payload.governance_notes

        provenance = ProvenanceRecord(
            dataset_id=dataset_id,
            event_type="TRUST_CHANGE",
            trust_at_event=payload.trust_level,
            recorded_by=payload.verified_by,
            notes=f"Trust changed from {old_trust} to {payload.trust_level}. {payload.governance_notes or ''}",
            is_replay_safe=False,
        )
        db.add(provenance)
        await db.flush()
        return dataset

    @staticmethod
    async def add_provenance(
        db: AsyncSession,
        dataset_id: UUID,
        payload: ProvenanceCreateRequest
    ) -> Optional[ProvenanceRecord]:
        dataset = await DatasetService.get_by_id(db, dataset_id)
        if not dataset:
            return None

        record = ProvenanceRecord(
            dataset_id=dataset_id,
            event_type=payload.event_type,
            source_system=payload.source_system,
            source_reference=payload.source_reference,
            ingestion_pipeline=payload.ingestion_pipeline,
            transformation_reference=payload.transformation_reference,
            trust_at_event=payload.trust_at_event,
            recorded_by=payload.recorded_by,
            notes=payload.notes,
            is_replay_safe=payload.is_replay_safe,
            replay_context=payload.replay_context,
        )
        db.add(record)
        await db.flush()
        return record

    @staticmethod
    async def get_provenance(
        db: AsyncSession, dataset_id: UUID
    ) -> List[ProvenanceRecord]:
        result = await db.execute(
            select(ProvenanceRecord)
            .where(ProvenanceRecord.dataset_id == dataset_id)
            .order_by(ProvenanceRecord.recorded_at.asc())
        )
        return result.scalars().all()
    