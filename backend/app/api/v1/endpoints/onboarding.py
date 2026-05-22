"""
BHIV Registry — Dataset Onboarding API Endpoints

POST   /onboarding/submit              → Submit new dataset onboarding request
GET    /onboarding/pending             → Get all pending requests
GET    /onboarding/all                 → Get all requests
GET    /onboarding/{request_id}        → Get specific request
POST   /onboarding/{request_id}/review → Approve or reject request
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.services.onboarding_service import OnboardingService
from app.schemas.registry import (
    OnboardingSubmitRequest,
    OnboardingReviewRequest,
    OnboardingResponse
)

router = APIRouter(prefix="/onboarding", tags=["Dataset Onboarding"])


@router.post("/submit", response_model=OnboardingResponse, status_code=201)
async def submit_onboarding_request(
    payload: OnboardingSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new dataset for onboarding review.
    Creates a PENDING_REVIEW request that must be
    approved before the dataset enters the registry.
    """
    try:
        request = await OnboardingService.submit_request(db, payload)
        return request
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/pending", response_model=List[OnboardingResponse])
async def get_pending_requests(
    db: AsyncSession = Depends(get_db)
):
    """Get all pending onboarding requests awaiting review."""
    return await OnboardingService.get_pending_requests(db)


@router.get("/all", response_model=List[OnboardingResponse])
async def get_all_requests(
    db: AsyncSession = Depends(get_db)
):
    """Get all onboarding requests regardless of status."""
    return await OnboardingService.get_all_requests(db)


@router.get("/{request_id}", response_model=OnboardingResponse)
async def get_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific onboarding request by ID."""
    request = await OnboardingService.get_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Onboarding request not found.")
    return request


@router.post("/{request_id}/review", response_model=OnboardingResponse)
async def review_request(
    request_id: UUID,
    payload: OnboardingReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve or reject an onboarding request.
    If APPROVED — dataset is automatically registered in the canonical registry.
    If REJECTED — request is closed with review notes.
    """
    try:
        request = await OnboardingService.review_request(db, request_id, payload)
        if not request:
            raise HTTPException(status_code=404, detail="Onboarding request not found.")
        return request
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))