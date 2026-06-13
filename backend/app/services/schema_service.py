"""
BHIV Registry — Schema Service Layer

All business logic for schema creation, versioning,
freezing, and retrieval lives here.
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.registry import DatasetSchema, Dataset, SchemaStatus
from app.schemas.registry import SchemaCreateRequest


class SchemaService:

    @staticmethod
    async def create_schema(
        db: AsyncSession,
        payload: SchemaCreateRequest
    ) -> DatasetSchema:
        """
        Create a new schema version for a dataset.
        Each dataset can have multiple schema versions.
        Versions must be unique per dataset.
        """
        # Check dataset exists
        dataset = await db.get(Dataset, payload.dataset_id)
        if not dataset:
            raise ValueError(f"Dataset '{payload.dataset_id}' not found.")

        # Check version uniqueness for this dataset
        existing = await db.execute(
            select(DatasetSchema).where(
                DatasetSchema.dataset_id == payload.dataset_id,
                DatasetSchema.schema_version == payload.schema_version
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                f"Schema version '{payload.schema_version}' already exists "
                f"for this dataset."
            )

        # Build field definitions as list of dicts
        field_defs = [f.model_dump() for f in payload.field_definitions]

        # Build compatibility rules
        compat_rules = None
        if payload.compatibility_rules:
            compat_rules = payload.compatibility_rules.model_dump()

        schema = DatasetSchema(
            dataset_id=payload.dataset_id,
            schema_version=payload.schema_version,
            status=SchemaStatus.DRAFT,
            field_definitions=field_defs,
            compatibility_rules=compat_rules,
            previous_schema_id=payload.previous_schema_id,
            schema_notes=payload.schema_notes,
            created_by=payload.created_by,
        )
        db.add(schema)
        await db.flush()
        return schema

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        schema_id: UUID
    ) -> Optional[DatasetSchema]:
        result = await db.execute(
            select(DatasetSchema).where(DatasetSchema.id == schema_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_schemas_for_dataset(
        db: AsyncSession,
        dataset_id: UUID
    ) -> List[DatasetSchema]:
        result = await db.execute(
            select(DatasetSchema)
            .where(DatasetSchema.dataset_id == dataset_id)
            .order_by(DatasetSchema.created_at.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def freeze_schema(
        db: AsyncSession,
        schema_id: UUID
    ) -> Optional[DatasetSchema]:
        """
        Freeze a schema version.
        Once frozen:
        - Field definitions become immutable
        - Status changes to FROZEN
        - frozen_at timestamp is recorded
        - Safe to use in production and replay workflows
        """
        schema = await SchemaService.get_by_id(db, schema_id)
        if not schema:
            return None

        if schema.status == SchemaStatus.FROZEN:
            raise ValueError("Schema is already frozen.")

        schema.status = SchemaStatus.FROZEN
        schema.frozen_at = datetime.now(timezone.utc)
        
        # Updated parent dataset to point to this frozen schema
        from app.models.registry import Dataset
        dataset = await db.get(Dataset, schema.dataset_id)
        if dataset:
            dataset.current_schema_id = schema.id
            dataset.schema_version = schema.schema_version
        
        await db.flush()
        return schema

    @staticmethod
    async def activate_schema(
        db: AsyncSession,
        schema_id: UUID
    ) -> Optional[DatasetSchema]:
        """Activate a draft schema — marks it ready for use."""
        schema = await SchemaService.get_by_id(db, schema_id)
        if not schema:
            return None

        if schema.status == SchemaStatus.FROZEN:
            raise ValueError("Cannot activate a frozen schema.")

        schema.status = SchemaStatus.ACTIVE
        await db.flush()
        return schema