"""
Full ecosystem seed script.
Registers Vijay's 6 datasets then registers all schemas.
Safe to run multiple times -- skips existing records.
"""

import asyncio
import httpx
import os

BASE_URL = "http://localhost:8000/api/v1"

API_KEY = os.environ.get("MDU_API_KEY", "")
if not API_KEY:
    raise SystemExit("Set MDU_API_KEY environment variable before running this script. Example: $env:MDU_API_KEY='your_key_here'")
HEADERS = {"X-API-Key": API_KEY}

VIJAY_DATASETS = [
    {
        "canonical_id": "BHIV-DS-REPLAY-SEMANTIC-EVENTS-001",
        "dataset_name": "semantic_events",
        "description": "Stores semantic replay events for replay integrity tracking",
        "source_system": "Replay Integrity Service",
        "owner_name": "Vijay",
        "owner_team": "InsightFlow Team",
        "domain_primary": "replay",
        "domain_tags": ["semantic", "replay", "events"],
        "trust_level": "TRUSTED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "NATIVE"
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-MUTATION-LOGS-001",
        "dataset_name": "mutation_logs",
        "description": "Tracks semantic mutation history for forensic governance",
        "source_system": "Governance Engine",
        "owner_name": "Vijay",
        "owner_team": "InsightFlow Team",
        "domain_primary": "governance",
        "domain_tags": ["mutation", "governance", "logs"],
        "trust_level": "VERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "COMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001",
        "dataset_name": "rollback_snapshots",
        "description": "Stores rollback checkpoints for state recovery operations",
        "source_system": "Recovery Service",
        "owner_name": "Vijay",
        "owner_team": "InsightFlow Team",
        "domain_primary": "recovery",
        "domain_tags": ["rollback", "snapshots", "recovery"],
        "trust_level": "PROVISIONAL",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "ADAPTABLE"
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001",
        "dataset_name": "contradiction_audits",
        "description": "Stores contradiction audit traces for governance visibility",
        "source_system": "Contradiction Engine",
        "owner_name": "Vijay",
        "owner_team": "InsightFlow Team",
        "domain_primary": "governance",
        "domain_tags": ["contradiction", "audit", "governance"],
        "trust_level": "TRUSTED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "COMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-LINEAGE-CHAIN-001",
        "dataset_name": "lineage_chain",
        "description": "Maintains semantic lineage continuity for provenance tracking",
        "source_system": "Lineage Verification Service",
        "owner_name": "Vijay",
        "owner_team": "InsightFlow Team",
        "domain_primary": "lineage",
        "domain_tags": ["lineage", "tracking", "semantic"],
        "trust_level": "VERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "NATIVE"
    },
    {
        "canonical_id": "BHIV-DS-TRUST-PROPAGATION-001",
        "dataset_name": "trust_propagation",
        "description": "Tracks downstream semantic trust propagation across services",
        "source_system": "Downstream Trust Gateway",
        "owner_name": "Vijay",
        "owner_team": "InsightFlow Team",
        "domain_primary": "trust",
        "domain_tags": ["trust", "propagation", "enforcement"],
        "trust_level": "PROVISIONAL",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "ADAPTABLE"
    }
]

VIJAY_SCHEMAS = [
    {
        "canonical_id": "BHIV-DS-REPLAY-SEMANTIC-EVENTS-001",
        "schema_notes": "Semantic replay event structure",
        "fields": [
            {"field_name": "event_id", "data_type": "uuid", "nullable": False, "description": "Unique replay event identifier"},
            {"field_name": "trace_id", "data_type": "string", "nullable": False, "description": "Immutable trace identifier"},
            {"field_name": "event_type", "data_type": "string", "nullable": False, "description": "Type of semantic replay event"},
            {"field_name": "replay_state", "data_type": "string", "nullable": False, "description": "Current replay state"},
            {"field_name": "source_node", "data_type": "string", "nullable": True, "description": "Origin node in replay chain"},
            {"field_name": "event_timestamp", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of event"},
            {"field_name": "validation_status", "data_type": "string", "nullable": True, "description": "Governance validation status"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-MUTATION-LOGS-001",
        "schema_notes": "Governance mutation log structure",
        "fields": [
            {"field_name": "mutation_id", "data_type": "uuid", "nullable": False, "description": "Unique mutation record identifier"},
            {"field_name": "entity_id", "data_type": "string", "nullable": False, "description": "ID of mutated entity"},
            {"field_name": "entity_type", "data_type": "string", "nullable": False, "description": "Type of entity mutated"},
            {"field_name": "mutation_type", "data_type": "string", "nullable": False, "description": "CREATE, UPDATE, DELETE, OVERRIDE"},
            {"field_name": "mutated_by", "data_type": "string", "nullable": False, "description": "Actor that performed mutation"},
            {"field_name": "previous_state", "data_type": "json", "nullable": True, "description": "State before mutation"},
            {"field_name": "mutation_timestamp", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of mutation"},
            {"field_name": "governance_approved", "data_type": "boolean", "nullable": False, "description": "Whether governance approved"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001",
        "schema_notes": "Rollback snapshot structure for state recovery",
        "fields": [
            {"field_name": "snapshot_id", "data_type": "uuid", "nullable": False, "description": "Unique snapshot identifier"},
            {"field_name": "entity_id", "data_type": "string", "nullable": False, "description": "ID of entity in snapshot"},
            {"field_name": "snapshot_type", "data_type": "string", "nullable": False, "description": "FULL, INCREMENTAL, CHECKPOINT"},
            {"field_name": "state_data", "data_type": "json", "nullable": False, "description": "Serialized state data"},
            {"field_name": "schema_version", "data_type": "string", "nullable": False, "description": "Schema version at snapshot time"},
            {"field_name": "snapshot_timestamp", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of snapshot"},
            {"field_name": "recovery_validated", "data_type": "boolean", "nullable": False, "description": "Recovery path validated"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001",
        "schema_notes": "Contradiction audit structure for anomaly inspection",
        "fields": [
            {"field_name": "audit_id", "data_type": "uuid", "nullable": False, "description": "Unique audit record identifier"},
            {"field_name": "contradiction_type", "data_type": "string", "nullable": False, "description": "Type of contradiction detected"},
            {"field_name": "source_a", "data_type": "string", "nullable": False, "description": "First conflicting source"},
            {"field_name": "source_b", "data_type": "string", "nullable": False, "description": "Second conflicting source"},
            {"field_name": "severity", "data_type": "string", "nullable": False, "description": "LOW, MEDIUM, HIGH, CRITICAL"},
            {"field_name": "resolution_status", "data_type": "string", "nullable": False, "description": "OPEN, RESOLVED, ESCALATED"},
            {"field_name": "detected_at", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of detection"},
            {"field_name": "resolved_at", "data_type": "datetime", "nullable": True, "description": "UTC timestamp of resolution"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-LINEAGE-CHAIN-001",
        "schema_notes": "Lineage chain structure for provenance continuity",
        "fields": [
            {"field_name": "lineage_id", "data_type": "uuid", "nullable": False, "description": "Unique lineage record identifier"},
            {"field_name": "trace_id", "data_type": "string", "nullable": False, "description": "Immutable trace ID across chain"},
            {"field_name": "parent_id", "data_type": "uuid", "nullable": True, "description": "Parent lineage record"},
            {"field_name": "dataset_reference", "data_type": "string", "nullable": False, "description": "Source dataset canonical ID"},
            {"field_name": "schema_version", "data_type": "string", "nullable": False, "description": "Schema version at this lineage point"},
            {"field_name": "lineage_type", "data_type": "string", "nullable": False, "description": "ORIGIN, DERIVED, MERGED, FILTERED"},
            {"field_name": "is_append_only", "data_type": "boolean", "nullable": False, "description": "Append-only lineage integrity confirmed"},
            {"field_name": "recorded_at", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of lineage record"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-TRUST-PROPAGATION-001",
        "schema_notes": "Trust propagation structure for downstream enforcement",
        "fields": [
            {"field_name": "propagation_id", "data_type": "uuid", "nullable": False, "description": "Unique propagation record identifier"},
            {"field_name": "source_dataset_id", "data_type": "string", "nullable": False, "description": "Canonical ID of trust source"},
            {"field_name": "target_service", "data_type": "string", "nullable": False, "description": "Downstream service receiving trust"},
            {"field_name": "trust_level", "data_type": "string", "nullable": False, "description": "Trust level being propagated"},
            {"field_name": "propagation_status", "data_type": "string", "nullable": False, "description": "PENDING, PROPAGATED, REJECTED, EXPIRED"},
            {"field_name": "cross_service_validated", "data_type": "boolean", "nullable": False, "description": "Cross-service validation complete"},
            {"field_name": "propagated_at", "data_type": "datetime", "nullable": True, "description": "UTC timestamp of propagation"}
        ]
    }
]


async def seed():
    async with httpx.AsyncClient(timeout=30.0) as client:

        print("=== PHASE 1: REGISTERING VIJAY DATASETS ===")
        print()

        dataset_ids = {}

        for ds in VIJAY_DATASETS:
            r = await client.post(f"{BASE_URL}/datasets/", json=ds, headers=HEADERS)
            if r.status_code == 201:
                dataset_ids[ds["canonical_id"]] = r.json()["id"]
                print(f"REGISTERED: {ds['canonical_id']}")
            elif r.status_code == 409:
                er = await client.get(f"{BASE_URL}/datasets/canonical/{ds['canonical_id']}", headers=HEADERS)
                dataset_ids[ds["canonical_id"]] = er.json()["id"]
                print(f"EXISTS: {ds['canonical_id']}")
            else:
                print(f"FAILED: {ds['canonical_id']} -- {r.text}")

        print()
        print("=== PHASE 2: REGISTERING SCHEMAS ===")
        print()

        for schema_def in VIJAY_SCHEMAS:
            canonical_id = schema_def["canonical_id"]
            dataset_id = dataset_ids.get(canonical_id)

            if not dataset_id:
                print(f"SKIPPED: {canonical_id} -- no dataset ID")
                continue

            # Check existing
            existing_r = await client.get(f"{BASE_URL}/schemas/dataset/{dataset_id}", headers=HEADERS)
            if existing_r.status_code == 200 and len(existing_r.json()) > 0:
                print(f"SCHEMA EXISTS: {canonical_id}")
                continue

            field_defs = [
                {
                    "field_name": f["field_name"],
                    "data_type": f["data_type"],
                    "nullable": f["nullable"],
                    "description": f["description"]
                }
                for f in schema_def["fields"]
            ]

            payload = {
                "dataset_id": dataset_id,
                "schema_version": "1.0.0",
                "field_definitions": field_defs,
                "compatibility_rules": {
                    "backward_compatible": True,
                    "breaking_changes": [],
                    "migration_notes": "Initial schema version"
                },
                "schema_notes": schema_def["schema_notes"],
                "created_by": "Vijay"
            }

            sr = await client.post(f"{BASE_URL}/schemas/", json=payload, headers=HEADERS)
            if sr.status_code == 201:
                schema_id = sr.json()["id"]
                print(f"SCHEMA REGISTERED: {canonical_id} | {len(field_defs)} fields")
                fr = await client.post(f"{BASE_URL}/schemas/{schema_id}/freeze", headers=HEADERS)
                if fr.status_code == 200:
                    print(f"SCHEMA FROZEN: {canonical_id}")
            else:
                print(f"FAILED: {canonical_id} -- {sr.text}")

        print()
        print("=== PHASE 3: REGISTRY SUMMARY ===")
        sr = await client.get(f"{BASE_URL}/discovery/summary", headers=HEADERS)
        if sr.status_code == 200:
            summary = sr.json()
            print(f"Total datasets: {summary['total_datasets']}")
            print(f"By trust: {summary['by_trust_level']}")
            print(f"By domain: {summary['by_domain']}")

        print()
        print("=== FULL ECOSYSTEM SEED COMPLETE ===")

asyncio.run(seed())