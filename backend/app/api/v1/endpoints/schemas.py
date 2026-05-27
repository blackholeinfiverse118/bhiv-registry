"""
BHIV Registry — Schema Registry API Endpoints

POST   /schemas/                    → Create new schema version
GET    /schemas/{schema_id}         → Get schema by ID
GET    /schemas/dataset/{dataset_id} → Get all schemas for a dataset
POST   /schemas/{schema_id}/freeze  → Freeze a schema version (makes it immutable)
PATCH  /schemas/{schema_id}/status  → Update schema status
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.services.schema_service import SchemaService
from app.schemas.registry import (
    SchemaCreateRequest,
    SchemaResponse,
    SuccessResponse
)

router = APIRouter(prefix="/schemas", tags=["Schemas"])


@router.post("/", response_model=SchemaResponse, status_code=201)
async def create_schema(
    payload: SchemaCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new schema version for a dataset."""
    try:
        schema = await SchemaService.create_schema(db, payload)
        return schema
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/dataset/{dataset_id}", response_model=List[SchemaResponse])
async def get_schemas_for_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all schema versions for a dataset."""
    schemas = await SchemaService.get_schemas_for_dataset(db, dataset_id)
    return schemas


@router.get("/{schema_id}", response_model=SchemaResponse)
async def get_schema(
    schema_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific schema version by ID."""
    schema = await SchemaService.get_by_id(db, schema_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found.")
    return schema


@router.post("/{schema_id}/freeze", response_model=SchemaResponse)
async def freeze_schema(
    schema_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Freeze a schema version — makes it immutable.
    Once frozen, field definitions cannot be changed.
    This is required before a schema can be used in production.
    """
    try:
        schema = await SchemaService.freeze_schema(db, schema_id)
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found.")
        return schema
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/{schema_id}/activate", response_model=SchemaResponse)
async def activate_schema(
    schema_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Activate a draft schema."""
    try:
        schema = await SchemaService.activate_schema(db, schema_id)
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found.")
        return schema
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))