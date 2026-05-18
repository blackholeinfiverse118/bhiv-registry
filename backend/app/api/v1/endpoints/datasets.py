"""
BHIV Registry — Dataset API Endpoints
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.base import get_db
from app.services.dataset_service import DatasetService
from app.schemas.registry import (
    DatasetRegisterRequest, DatasetUpdateRequest,
    DatasetResponse, DatasetListResponse,
    DatasetSearchFilters, TrustUpdateRequest,
    ProvenanceCreateRequest, ProvenanceResponse,
    TrustLevel, ReplayCompatibility,
    SimulationCompatibility, DatasetStatus
)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/", response_model=DatasetResponse, status_code=201)
async def register_dataset(
    payload: DatasetRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        dataset = await DatasetService.register_dataset(db, payload)
        return dataset
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=DatasetListResponse)
async def search_datasets(
    domain_primary: Optional[str] = Query(None),
    domain_tags: Optional[List[str]] = Query(None),
    trust_level: Optional[TrustLevel] = Query(None),
    replay_compatibility: Optional[ReplayCompatibility] = Query(None),
    simulation_compatibility: Optional[SimulationCompatibility] = Query(None),
    owner_team: Optional[str] = Query(None),
    status: Optional[DatasetStatus] = Query(DatasetStatus.ACTIVE),
    search_text: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    filters = DatasetSearchFilters(
        domain_primary=domain_primary,
        domain_tags=domain_tags,
        trust_level=trust_level,
        replay_compatibility=replay_compatibility,
        simulation_compatibility=simulation_compatibility,
        owner_team=owner_team,
        status=status,
        search_text=search_text,
        page=page,
        page_size=page_size,
    )
    results, total = await DatasetService.search_datasets(db, filters)
    return DatasetListResponse(total=total, page=page, page_size=page_size, results=results)


@router.get("/canonical/{canonical_id}", response_model=DatasetResponse)
async def get_by_canonical_id(
    canonical_id: str,
    db: AsyncSession = Depends(get_db)
):
    dataset = await DatasetService.get_by_canonical_id(db, canonical_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{canonical_id}' not found.")
    return dataset


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    dataset = await DatasetService.get_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: UUID,
    payload: DatasetUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    dataset = await DatasetService.update_dataset(db, dataset_id, payload)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.post("/{dataset_id}/trust", response_model=DatasetResponse)
async def update_trust(
    dataset_id: UUID,
    payload: TrustUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    dataset = await DatasetService.update_trust(db, dataset_id, payload)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.get("/{dataset_id}/provenance", response_model=List[ProvenanceResponse])
async def get_provenance(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    records = await DatasetService.get_provenance(db, dataset_id)
    return records


@router.post("/{dataset_id}/provenance", response_model=ProvenanceResponse, status_code=201)
async def add_provenance(
    dataset_id: UUID,
    payload: ProvenanceCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    record = await DatasetService.add_provenance(db, dataset_id, payload)
    if not record:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return record


@router.post("/{dataset_id}/trust/transition", response_model=DatasetResponse)
async def transition_trust(
    dataset_id: UUID,
    payload: TrustUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Formally transition trust level with validation.
    Enforces valid transitions — not all trust changes are allowed.
    Requires governance note when moving to QUARANTINE or UNVERIFIED.
    """
    from app.services.trust_service import TrustService
    try:
        dataset = await TrustService.transition_trust(db, dataset_id, payload)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found.")
        return dataset
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{dataset_id}/trust/history", response_model=List[ProvenanceResponse])
async def get_trust_history(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the full trust change history for a dataset."""
    from app.services.trust_service import TrustService
    records = await TrustService.get_trust_history(db, dataset_id)
    return records