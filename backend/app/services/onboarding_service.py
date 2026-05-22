"""
BHIV Registry — Dataset Onboarding Service

Manages the formal onboarding flow for new datasets.
Datasets must go through this process before being
registered in the canonical registry.

Flow: SUBMIT → PENDING_REVIEW → APPROVED → REGISTERED
                              → REJECTED
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.registry import (
    DatasetOnboardingRequest, Dataset,
    OnboardingStatus, TrustLevel
)
from app.schemas.registry import (
    OnboardingSubmitRequest,
    OnboardingReviewRequest
)


class OnboardingService:

    @staticmethod
    async def submit_request(
        db: AsyncSession,
        payload: OnboardingSubmitRequest
    ) -> DatasetOnboardingRequest:
        """
        Submit a new dataset onboarding request.
        Creates a PENDING_REVIEW request for governance review.
        """
        # Check no duplicate pending request for same canonical ID
        existing = await db.execute(
            select(DatasetOnboardingRequest).where(
                DatasetOnboardingRequest.proposed_canonical_id == payload.proposed_canonical_id,
                DatasetOnboardingRequest.status == OnboardingStatus.PENDING_REVIEW
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                f"A pending onboarding request for "
                f"'{payload.proposed_canonical_id}' already exists."
            )

        request = DatasetOnboardingRequest(
            proposed_canonical_id=payload.proposed_canonical_id,
            dataset_name=payload.dataset_name,
            description=payload.description,
            source_system=payload.source_system,
            owner_name=payload.owner_name,
            owner_team=payload.owner_team,
            domain_primary=payload.domain_primary,
            domain_tags=payload.domain_tags,
            proposed_trust_level=payload.proposed_trust_level,
            proposed_replay_compatibility=payload.proposed_replay_compatibility,
            proposed_simulation_compatibility=payload.proposed_simulation_compatibility,
            submitted_by=payload.submitted_by,
            submission_notes=payload.submission_notes,
        )
        db.add(request)
        await db.flush()
        return request

    @staticmethod
    async def review_request(
        db: AsyncSession,
        request_id: UUID,
        payload: OnboardingReviewRequest
    ) -> Optional[DatasetOnboardingRequest]:
        """
        Approve or reject an onboarding request.
        If approved — automatically registers the dataset.
        """
        result = await db.execute(
            select(DatasetOnboardingRequest).where(
                DatasetOnboardingRequest.id == request_id
            )
        )
        request = result.scalar_one_or_none()
        if not request:
            return None

        if request.status != OnboardingStatus.PENDING_REVIEW:
            raise ValueError(
                f"Request is already {request.status}. "
                f"Only PENDING_REVIEW requests can be reviewed."
            )

        request.reviewed_by = payload.reviewed_by
        request.reviewed_at = datetime.now(timezone.utc)
        request.review_notes = payload.review_notes

        if payload.decision == "APPROVED":
            request.status = OnboardingStatus.APPROVED

            # Auto-register the dataset
            from app.models.registry import ProvenanceRecord
            dataset = Dataset(
                canonical_id=request.proposed_canonical_id,
                dataset_name=request.dataset_name,
                description=request.description,
                source_system=request.source_system,
                owner_name=request.owner_name,
                owner_team=request.owner_team,
                domain_primary=request.domain_primary,
                domain_tags=request.domain_tags,
                trust_level=request.proposed_trust_level,
                replay_compatibility=request.proposed_replay_compatibility,
                simulation_compatibility=request.proposed_simulation_compatibility,
            )
            db.add(dataset)
            await db.flush()

            # Create ORIGIN provenance
            provenance = ProvenanceRecord(
                dataset_id=dataset.id,
                event_type="ORIGIN",
                source_system=request.source_system,
                trust_at_event=request.proposed_trust_level,
                recorded_by=payload.reviewed_by,
                notes=(
                    f"Dataset registered via formal onboarding process. "
                    f"Submitted by: {request.submitted_by}. "
                    f"Approved by: {payload.reviewed_by}. "
                    f"Review notes: {payload.review_notes or 'None'}"
                ),
                is_replay_safe=False,
            )
            db.add(provenance)

            request.registered_dataset_id = dataset.id
            request.status = OnboardingStatus.REGISTERED

        else:
            request.status = OnboardingStatus.REJECTED

        await db.flush()
        return request

    @staticmethod
    async def get_pending_requests(
        db: AsyncSession
    ) -> List[DatasetOnboardingRequest]:
        """Get all pending onboarding requests."""
        result = await db.execute(
            select(DatasetOnboardingRequest)
            .where(DatasetOnboardingRequest.status == OnboardingStatus.PENDING_REVIEW)
            .order_by(DatasetOnboardingRequest.submitted_at.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_requests(
        db: AsyncSession
    ) -> List[DatasetOnboardingRequest]:
        """Get all onboarding requests."""
        result = await db.execute(
            select(DatasetOnboardingRequest)
            .order_by(DatasetOnboardingRequest.submitted_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        request_id: UUID
    ) -> Optional[DatasetOnboardingRequest]:
        result = await db.execute(
            select(DatasetOnboardingRequest).where(
                DatasetOnboardingRequest.id == request_id
            )
        )
        return result.scalar_one_or_none()