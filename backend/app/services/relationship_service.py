"""
BHIV Registry — Dataset Relationship Service Layer
"""

from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.registry import DatasetRelationship, Dataset
from app.schemas.registry import RelationshipCreateRequest


VALID_RELATIONSHIP_TYPES = {
    "DERIVED_FROM",
    "DEPENDS_ON",
    "MERGED_FROM",
    "FILTERED_FROM"
}


class RelationshipService:

    @staticmethod
    async def create_relationship(
        db: AsyncSession,
        payload: RelationshipCreateRequest
    ) -> DatasetRelationship:
        """
        Create a parent-child relationship between two datasets.
        Prevents duplicate relationships of the same type.
        Prevents self-referencing relationships.
        """
        # Prevent self-reference
        if payload.parent_dataset_id == payload.child_dataset_id:
            raise ValueError("A dataset cannot have a relationship with itself.")

        # Validate relationship type
        if payload.relationship_type.upper() not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"Invalid relationship type. Must be one of: {VALID_RELATIONSHIP_TYPES}"
            )

        # Check both datasets exist
        parent = await db.get(Dataset, payload.parent_dataset_id)
        if not parent:
            raise ValueError(f"Parent dataset '{payload.parent_dataset_id}' not found.")

        child = await db.get(Dataset, payload.child_dataset_id)
        if not child:
            raise ValueError(f"Child dataset '{payload.child_dataset_id}' not found.")

        # Check duplicate
        existing = await db.execute(
            select(DatasetRelationship).where(
                DatasetRelationship.parent_dataset_id == payload.parent_dataset_id,
                DatasetRelationship.child_dataset_id == payload.child_dataset_id,
                DatasetRelationship.relationship_type == payload.relationship_type.upper()
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("This relationship already exists.")

        relationship = DatasetRelationship(
            parent_dataset_id=payload.parent_dataset_id,
            child_dataset_id=payload.child_dataset_id,
            relationship_type=payload.relationship_type.upper(),
            description=payload.description,
            transformation_notes=payload.transformation_notes,
            chain_replay_safe=payload.chain_replay_safe,
            created_by=payload.created_by,
        )
        db.add(relationship)
        await db.flush()
        return relationship

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        relationship_id: UUID
    ) -> Optional[DatasetRelationship]:
        result = await db.execute(
            select(DatasetRelationship).where(
                DatasetRelationship.id == relationship_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_for_dataset(
        db: AsyncSession,
        dataset_id: UUID
    ) -> List[DatasetRelationship]:
        """Get all relationships where dataset is either parent or child."""
        result = await db.execute(
            select(DatasetRelationship).where(
                or_(
                    DatasetRelationship.parent_dataset_id == dataset_id,
                    DatasetRelationship.child_dataset_id == dataset_id
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def delete_relationship(
        db: AsyncSession,
        relationship_id: UUID
    ) -> bool:
        relationship = await RelationshipService.get_by_id(db, relationship_id)
        if not relationship:
            return False
        await db.delete(relationship)
        await db.flush()
        return True