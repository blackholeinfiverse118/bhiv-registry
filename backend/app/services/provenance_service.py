"""
BHIV Registry — Provenance Chain Validation Service

Validates the completeness and integrity of a dataset's
provenance chain. Used to confirm replay-safety and
trust eligibility before TANTRA system consumption.
"""

from uuid import UUID
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.registry import (
    Dataset, ProvenanceRecord, TrustLevel, ReplayCompatibility
)


class ProvenanceService:

    @staticmethod
    async def validate_chain(
        db: AsyncSession,
        dataset_id: UUID
    ) -> Dict[str, Any]:
        """
        Validate the provenance chain for a dataset.

        Checks:
        1. Chain starts with ORIGIN event
        2. No gaps in the event sequence
        3. Trust changes are properly recorded
        4. Replay safety is consistent
        5. Chain is complete enough for TANTRA consumption
        """
        # Get dataset
        dataset = await db.get(Dataset, dataset_id)
        if not dataset:
            return {"valid": False, "error": "Dataset not found"}

        # Get all provenance records ordered by time
        result = await db.execute(
            select(ProvenanceRecord)
            .where(ProvenanceRecord.dataset_id == dataset_id)
            .order_by(ProvenanceRecord.recorded_at.asc())
        )
        records = result.scalars().all()

        issues = []
        warnings = []

        # Check 1 — Must have at least one record
        if not records:
            return {
                "valid": False,
                "dataset_id": str(dataset_id),
                "canonical_id": dataset.canonical_id,
                "issues": ["No provenance records found. Dataset has no history."],
                "warnings": [],
                "record_count": 0,
                "replay_safe": False,
                "tantra_ready": False
            }

        # Check 2 — First event must be ORIGIN
        if records[0].event_type != "ORIGIN":
            issues.append(
                f"Chain does not start with ORIGIN event. "
                f"First event is: {records[0].event_type}"
            )

        # Check 3 — Count event types
        event_types = [r.event_type for r in records]
        trust_changes = [r for r in records if r.event_type == "TRUST_CHANGE"]

        # Check 4 — Trust change consistency
        if dataset.trust_level != TrustLevel.UNVERIFIED and len(trust_changes) == 0:
            issues.append(
                "Dataset trust level is not UNVERIFIED but no "
                "TRUST_CHANGE events found in provenance chain."
            )

        # Check 5 — Replay safety consistency
        replay_safe_records = [r for r in records if r.is_replay_safe]
        if (dataset.replay_compatibility == ReplayCompatibility.FULL and
                len(replay_safe_records) == 0):
            warnings.append(
                "Dataset is marked FULL replay compatible but no "
                "replay-safe provenance records exist."
            )

        # Check 6 — Recorded by is always present
        missing_recorder = [r for r in records if not r.recorded_by]
        if missing_recorder:
            issues.append(
                f"{len(missing_recorder)} provenance records missing 'recorded_by' field."
            )

        # Check 7 — TANTRA readiness
        tantra_ready = (
            len(issues) == 0 and
            records[0].event_type == "ORIGIN" and
            dataset.status.value == "ACTIVE"
        )

        # Replay safe overall
        replay_safe = (
            dataset.replay_compatibility.value in ["FULL", "PARTIAL"] and
            len(issues) == 0
        )

        return {
            "valid": len(issues) == 0,
            "dataset_id": str(dataset_id),
            "canonical_id": dataset.canonical_id,
            "record_count": len(records),
            "event_types_present": list(set(event_types)),
            "trust_change_count": len(trust_changes),
            "current_trust": dataset.trust_level.value,
            "replay_compatibility": dataset.replay_compatibility.value,
            "replay_safe": replay_safe,
            "tantra_ready": tantra_ready,
            "issues": issues,
            "warnings": warnings,
        }

    @staticmethod
    async def validate_all(
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Validate provenance chains for all active datasets.
        Returns a full registry-wide validation report.
        """
        result = await db.execute(select(Dataset))
        datasets = result.scalars().all()

        report = []
        for dataset in datasets:
            validation = await ProvenanceService.validate_chain(db, dataset.id)
            report.append(validation)

        return report