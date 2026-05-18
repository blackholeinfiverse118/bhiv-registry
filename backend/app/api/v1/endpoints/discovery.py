"""
BHIV Registry — Discovery API Endpoints

GET /discovery/summary                  → Registry summary dashboard
GET /discovery/replay-safe              → All replay-safe datasets
GET /discovery/simulation-ready         → All simulation-ready datasets
GET /discovery/trusted                  → All trusted/verified datasets
GET /discovery/quarantined              → All quarantined datasets
GET /discovery/by-team/{team}           → Datasets by owner team
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from app.db.base import get_db
from app.services.discovery_service import DiscoveryService
from app.schemas.registry import DatasetResponse

from app.services.provenance_service import ProvenanceService
from uuid import UUID


router = APIRouter(prefix="/discovery", tags=["Discovery"])


@router.get("/summary")
async def get_registry_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a high-level summary of the entire registry.
    Shows counts by trust level, replay compatibility,
    simulation compatibility, domain and status.
    Perfect for dashboards.
    """
    return await DiscoveryService.get_registry_summary(db)


@router.get("/replay-safe", response_model=List[DatasetResponse])
async def get_replay_safe_datasets(
    domain: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all datasets safe for replay workflows."""
    return await DiscoveryService.find_replay_safe_datasets(db, domain)


@router.get("/simulation-ready", response_model=List[DatasetResponse])
async def get_simulation_ready_datasets(
    domain: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all datasets suitable for simulation use cases."""
    return await DiscoveryService.find_simulation_ready_datasets(db, domain)


@router.get("/trusted", response_model=List[DatasetResponse])
async def get_trusted_datasets(
    domain: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all datasets at TRUSTED or VERIFIED trust level."""
    return await DiscoveryService.find_trusted_datasets(db, domain)


@router.get("/quarantined", response_model=List[DatasetResponse])
async def get_quarantined_datasets(
    db: AsyncSession = Depends(get_db)
):
    """Get all quarantined datasets — these need immediate attention."""
    return await DiscoveryService.get_quarantined_datasets(db)


@router.get("/by-team/{owner_team}", response_model=List[DatasetResponse])
async def get_datasets_by_team(
    owner_team: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all datasets owned by a specific team."""
    return await DiscoveryService.find_datasets_by_owner_team(db, owner_team)


@router.get("/provenance/validate/{dataset_id}")
async def validate_provenance_chain(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate the provenance chain for a single dataset.
    Checks completeness, trust consistency and TANTRA readiness.
    """
    return await ProvenanceService.validate_chain(db, dataset_id)


@router.get("/provenance/validate-all")
async def validate_all_provenance(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Validate provenance chains for all datasets.
    Returns a full registry-wide validation report.
    """
    return await ProvenanceService.validate_all(db)