"""
Register schemas for Vijay's 6 BHIV ecosystem datasets.
Schema structures derived from dataset domain context
and Vijay's submitted field structure patterns.
"""

import asyncio
import httpx
import os

BASE_URL = "http://localhost:8000/api/v1"

API_KEY = os.environ.get("MDU_API_KEY", "")
if not API_KEY:
    raise SystemExit("Set MDU_API_KEY environment variable before running this script. Example: $env:MDU_API_KEY='your_key_here'")
HEADERS = {"X-API-Key": API_KEY}

SCHEMAS = [
    {
        "canonical_id": "BHIV-DS-REPLAY-SEMANTIC-EVENTS-001",
        "schema_version": "1.0.0",
        "created_by": "Vijay",
        "schema_notes": "Semantic replay event structure for replay integrity tracking",
        "fields": [
            {"field_name": "event_id", "data_type": "uuid", "nullable": False, "description": "Unique replay event identifier"},
            {"field_name": "trace_id", "data_type": "string", "nullable": False, "description": "Immutable trace identifier across replay chain"},
            {"field_name": "event_type", "data_type": "string", "nullable": False, "description": "Type of semantic replay event"},
            {"field_name": "replay_state", "data_type": "string", "nullable": False, "description": "Current replay state: PENDING, ACTIVE, COMPLETE, FAILED"},
            {"field_name": "source_node", "data_type": "string", "nullable": True, "description": "Origin node in replay chain"},
            {"field_name": "event_timestamp", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of event occurrence"},
            {"field_name": "validation_status", "data_type": "string", "nullable": True, "description": "Governance validation status"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-MUTATION-LOGS-001",
        "schema_version": "1.0.0",
        "created_by": "Vijay",
        "schema_notes": "Governance mutation log structure for forensic audit tracking",
        "fields": [
            {"field_name": "mutation_id", "data_type": "uuid", "nullable": False, "description": "Unique mutation record identifier"},
            {"field_name": "entity_id", "data_type": "string", "nullable": False, "description": "ID of the entity that was mutated"},
            {"field_name": "entity_type", "data_type": "string", "nullable": False, "description": "Type of entity mutated"},
            {"field_name": "mutation_type", "data_type": "string", "nullable": False, "description": "Type of mutation: CREATE, UPDATE, DELETE, OVERRIDE"},
            {"field_name": "mutated_by", "data_type": "string", "nullable": False, "description": "System or actor that performed the mutation"},
            {"field_name": "previous_state", "data_type": "json", "nullable": True, "description": "State before mutation for rollback reference"},
            {"field_name": "mutation_timestamp", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of mutation event"},
            {"field_name": "governance_approved", "data_type": "boolean", "nullable": False, "description": "Whether mutation was governance approved"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001",
        "schema_version": "1.0.0",
        "created_by": "Vijay",
        "schema_notes": "Rollback snapshot structure for state recovery operations",
        "fields": [
            {"field_name": "snapshot_id", "data_type": "uuid", "nullable": False, "description": "Unique snapshot identifier"},
            {"field_name": "entity_id", "data_type": "string", "nullable": False, "description": "ID of entity captured in snapshot"},
            {"field_name": "snapshot_type", "data_type": "string", "nullable": False, "description": "Snapshot type: FULL, INCREMENTAL, CHECKPOINT"},
            {"field_name": "state_data", "data_type": "json", "nullable": False, "description": "Serialized state data at snapshot time"},
            {"field_name": "schema_version", "data_type": "string", "nullable": False, "description": "Schema version at time of snapshot"},
            {"field_name": "snapshot_timestamp", "data_type": "datetime", "nullable": False, "description": "UTC timestamp when snapshot was taken"},
            {"field_name": "recovery_validated", "data_type": "boolean", "nullable": False, "description": "Whether recovery path has been validated"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001",
        "schema_version": "1.0.0",
        "created_by": "Vijay",
        "schema_notes": "Contradiction audit structure for governance anomaly inspection",
        "fields": [
            {"field_name": "audit_id", "data_type": "uuid", "nullable": False, "description": "Unique contradiction audit record identifier"},
            {"field_name": "contradiction_type", "data_type": "string", "nullable": False, "description": "Type of contradiction detected"},
            {"field_name": "source_a", "data_type": "string", "nullable": False, "description": "First conflicting source reference"},
            {"field_name": "source_b", "data_type": "string", "nullable": False, "description": "Second conflicting source reference"},
            {"field_name": "severity", "data_type": "string", "nullable": False, "description": "Severity level: LOW, MEDIUM, HIGH, CRITICAL"},
            {"field_name": "resolution_status", "data_type": "string", "nullable": False, "description": "Resolution state: OPEN, RESOLVED, ESCALATED"},
            {"field_name": "detected_at", "data_type": "datetime", "nullable": False, "description": "UTC timestamp when contradiction was detected"},
            {"field_name": "resolved_at", "data_type": "datetime", "nullable": True, "description": "UTC timestamp when contradiction was resolved"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-LINEAGE-CHAIN-001",
        "schema_version": "1.0.0",
        "created_by": "Vijay",
        "schema_notes": "Lineage chain structure for provenance continuity tracking",
        "fields": [
            {"field_name": "lineage_id", "data_type": "uuid", "nullable": False, "description": "Unique lineage record identifier"},
            {"field_name": "trace_id", "data_type": "string", "nullable": False, "description": "Immutable trace ID preserved across full lineage chain"},
            {"field_name": "parent_id", "data_type": "uuid", "nullable": True, "description": "Parent lineage record -- null for origin"},
            {"field_name": "dataset_reference", "data_type": "string", "nullable": False, "description": "Reference to source dataset canonical ID"},
            {"field_name": "schema_version", "data_type": "string", "nullable": False, "description": "Schema version at this lineage point"},
            {"field_name": "lineage_type", "data_type": "string", "nullable": False, "description": "Type: ORIGIN, DERIVED, MERGED, FILTERED"},
            {"field_name": "is_append_only", "data_type": "boolean", "nullable": False, "description": "Confirms append-only lineage integrity"},
            {"field_name": "recorded_at", "data_type": "datetime", "nullable": False, "description": "UTC timestamp of lineage record creation"}
        ]
    },
    {
        "canonical_id": "BHIV-DS-TRUST-PROPAGATION-001",
        "schema_version": "1.0.0",
        "created_by": "Vijay",
        "schema_notes": "Trust propagation structure for downstream trust enforcement",
        "fields": [
            {"field_name": "propagation_id", "data_type": "uuid", "nullable": False, "description": "Unique trust propagation record identifier"},
            {"field_name": "source_dataset_id", "data_type": "string", "nullable": False, "description": "Canonical ID of trust source dataset"},
            {"field_name": "target_service", "data_type": "string", "nullable": False, "description": "Downstream service receiving trust signal"},
            {"field_name": "trust_level", "data_type": "string", "nullable": False, "description": "Trust level being propagated: VERIFIED, TRUSTED, PROVISIONAL"},
            {"field_name": "propagation_status", "data_type": "string", "nullable": False, "description": "Status: PENDING, PROPAGATED, REJECTED, EXPIRED"},
            {"field_name": "cross_service_validated", "data_type": "boolean", "nullable": False, "description": "Whether cross-service validation is complete"},
            {"field_name": "propagated_at", "data_type": "datetime", "nullable": True, "description": "UTC timestamp when trust was propagated"}
        ]
    }
]


async def register_schemas():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=== REGISTERING VIJAY ECOSYSTEM DATASET SCHEMAS ===")
        print()

        for schema_def in SCHEMAS:
            canonical_id = schema_def["canonical_id"]
            print(f"Processing: {canonical_id}")

            # Get dataset
            r = await client.get(f"{BASE_URL}/datasets/canonical/{canonical_id}", headers=HEADERS)
            if r.status_code != 200:
                print(f"  SKIPPED: Dataset not found in registry")
                print()
                continue

            dataset_id = r.json()["id"]

            # Check if schema already exists
            existing_r = await client.get(f"{BASE_URL}/schemas/dataset/{dataset_id}", headers=HEADERS)
            if existing_r.status_code == 200 and len(existing_r.json()) > 0:
                print(f"  SCHEMA ALREADY EXISTS: v{existing_r.json()[0]['schema_version']}")
                print()
                continue

            # Build field definitions
            field_defs = []
            for f in schema_def["fields"]:
                field_defs.append({
                    "field_name": f["field_name"],
                    "data_type": f["data_type"],
                    "nullable": f["nullable"],
                    "description": f["description"]
                })

            # Register schema
            payload = {
                "dataset_id": dataset_id,
                "schema_version": schema_def["schema_version"],
                "field_definitions": field_defs,
                "compatibility_rules": {
                    "backward_compatible": True,
                    "breaking_changes": [],
                    "migration_notes": "Initial schema version"
                },
                "schema_notes": schema_def["schema_notes"],
                "created_by": schema_def["created_by"]
            }

            sr = await client.post(f"{BASE_URL}/schemas/", json=payload, headers=HEADERS)
            if sr.status_code == 201:
                schema_id = sr.json()["id"]
                print(f"  SCHEMA REGISTERED: v1.0.0 | {len(field_defs)} fields")

                # Freeze it
                fr = await client.post(f"{BASE_URL}/schemas/{schema_id}/freeze", headers=HEADERS)
                if fr.status_code == 200:
                    print(f"  SCHEMA FROZEN: immutable and replay-safe")
            else:
                print(f"  FAILED: {sr.text}")

            print()

        print("=== SCHEMA REGISTRATION COMPLETE ===")

asyncio.run(register_schemas())