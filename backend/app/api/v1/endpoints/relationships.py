"""
BHIV Registry — Dataset Relationship API Endpoints

POST   /relationships/                          → Create relationship between datasets
GET    /relationships/dataset/{dataset_id}      → Get all relationships for a dataset
GET    /relationships/{relationship_id}         → Get specific relationship
DELETE /relationships/{relationship_id}         → Remove a relationship
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.services.relationship_service import RelationshipService
from app.schemas.registry import (
    RelationshipCreateRequest,
    RelationshipResponse
)

router = APIRouter(prefix="/relationships", tags=["Dataset Relationships"])


@router.post("/", response_model=RelationshipResponse, status_code=201)
async def create_relationship(
    payload: RelationshipCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a relationship between two datasets.
    Relationship types: DERIVED_FROM, DEPENDS_ON, MERGED_FROM, FILTERED_FROM
    """
    try:
        relationship = await RelationshipService.create_relationship(db, payload)
        return relationship
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/dataset/{dataset_id}", response_model=List[RelationshipResponse])
async def get_relationships_for_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all relationships for a dataset — both as parent and as child."""
    relationships = await RelationshipService.get_for_dataset(db, dataset_id)
    return relationships


@router.get("/{relationship_id}", response_model=RelationshipResponse)
async def get_relationship(
    relationship_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific relationship by ID."""
    relationship = await RelationshipService.get_by_id(db, relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found.")
    return relationship


@router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    relationship_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove a dataset relationship."""
    deleted = await RelationshipService.delete_relationship(db, relationship_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relationship not found.")