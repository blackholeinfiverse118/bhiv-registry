"""
BHIV Registry — Trust Classification Workflow Service

Governs how datasets move between trust levels.
Enforces valid transitions and creates detailed audit provenance.

Valid Trust Transitions:
UNVERIFIED  → PROVISIONAL, QUARANTINE
PROVISIONAL → TRUSTED, UNVERIFIED, QUARANTINE
TRUSTED     → VERIFIED, PROVISIONAL, QUARANTINE
VERIFIED    → TRUSTED, QUARANTINE
QUARANTINE  → UNVERIFIED (only after review)
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.registry import Dataset, ProvenanceRecord, TrustLevel
from app.schemas.registry import TrustUpdateRequest


# Valid transitions map — what each level can move to
VALID_TRANSITIONS = {
    TrustLevel.UNVERIFIED:  [TrustLevel.PROVISIONAL, TrustLevel.QUARANTINE],
    TrustLevel.PROVISIONAL: [TrustLevel.TRUSTED, TrustLevel.UNVERIFIED, TrustLevel.QUARANTINE],
    TrustLevel.TRUSTED:     [TrustLevel.VERIFIED, TrustLevel.PROVISIONAL, TrustLevel.QUARANTINE],
    TrustLevel.VERIFIED:    [TrustLevel.TRUSTED, TrustLevel.QUARANTINE],
    TrustLevel.QUARANTINE:  [TrustLevel.UNVERIFIED],
}

# Transitions that require a governance note
REQUIRES_REASON = {
    TrustLevel.QUARANTINE,
    TrustLevel.UNVERIFIED,
}


class TrustService:

    @staticmethod
    async def transition_trust(
        db: AsyncSession,
        dataset_id: UUID,
        payload: TrustUpdateRequest
    ) -> Optional[Dataset]:
        """
        Formally transition a dataset's trust level.
        Enforces valid transitions and creates audit provenance.
        """
        result = await db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            return None

        current_trust = dataset.trust_level
        new_trust = payload.trust_level

        # No change needed
        if current_trust == new_trust:
            raise ValueError(f"Dataset is already at trust level {new_trust}.")

        # Validate transition
        allowed = VALID_TRANSITIONS.get(current_trust, [])
        if new_trust not in allowed:
            raise ValueError(
                f"Invalid trust transition: {current_trust} → {new_trust}. "
                f"Allowed transitions from {current_trust}: {[t.value for t in allowed]}"
            )

        # Require governance note for sensitive transitions
        if new_trust in REQUIRES_REASON and not payload.governance_notes:
            raise ValueError(
                f"A governance note is required when transitioning to {new_trust}."
            )

        # Apply the transition
        old_trust = dataset.trust_level
        dataset.trust_level = new_trust
        dataset.trust_verified_by = payload.verified_by
        dataset.trust_verified_at = datetime.now(timezone.utc)
        if payload.governance_notes:
            dataset.governance_notes = payload.governance_notes

        # Create detailed audit provenance record
        provenance = ProvenanceRecord(
            dataset_id=dataset_id,
            event_type="TRUST_CHANGE",
            trust_at_event=new_trust,
            recorded_by=payload.verified_by,
            notes=(
                f"Trust transition: {old_trust.value} → {new_trust.value}. "
                f"Authorized by: {payload.verified_by}. "
                f"Reason: {payload.governance_notes or 'Not specified'}"
            ),
            is_replay_safe=False,
        )
        db.add(provenance)
        await db.flush()
        return dataset

    @staticmethod
    async def get_trust_history(
        db: AsyncSession,
        dataset_id: UUID
    ):
        """Get all trust change events for a dataset."""
        result = await db.execute(
            select(ProvenanceRecord)
            .where(
                ProvenanceRecord.dataset_id == dataset_id,
                ProvenanceRecord.event_type == "TRUST_CHANGE"
            )
            .order_by(ProvenanceRecord.recorded_at.asc())
        )
        return result.scalars().all()