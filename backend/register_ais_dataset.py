"""
Register the AIS Live Maritime Feed dataset from Ankita
into the BHIV MDU Registry with complete metadata flow.

This demonstrates:
- Dataset registration with canonical ID
- Schema registration with all field definitions
- Provenance records (ORIGIN + INGESTION)
- Trust classification
- Simulation and replay compatibility
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

API_KEY = "ankita_svacs_nicai_2720440eb88befb90043d700a55e4721"
HEADERS = {"X-API-Key": API_KEY}

async def register_ais_dataset():
    async with httpx.AsyncClient(timeout=30.0) as client:

        print("=== REGISTERING AIS LIVE MARITIME FEED DATASET ===")
        print()

        # Step 1 - Register the dataset (or get existing)
        print("Step 1: Registering dataset...")
        dataset_payload = {
            "canonical_id": "BHIV-DS-MARITIME-AIS-LIVE-001",
            "dataset_name": "AIS Live Maritime Feed",
            "description": "Real-time Automatic Identification System vessel tracking data. Contains MMSI, position coordinates, speed, and vessel type for maritime vessels. 10,000 records from 2022-01-01. Source: Ankita SVACS governance sprint.",
            "source_system": "AIS Maritime Tracking Infrastructure",
            "source_location": "svacs-unified-core/ais_feed",
            "owner_name": "Ankita",
            "owner_team": "SVACS Governance Team",
            "owner_contact": "ankita@bhiv",
            "domain_primary": "maritime",
            "domain_tags": ["maritime", "AIS", "vessel-tracking", "geospatial", "telemetry", "live-feed"],
            "trust_level": "TRUSTED",
            "replay_compatibility": "PARTIAL",
            "replay_notes": "Telemetry continuity verified. May contain minor gaps in timestamp sequences.",
            "simulation_compatibility": "COMPATIBLE",
            "simulation_notes": "Compatible with maritime simulation use cases. Vessel type codes follow ITU standards.",
            "ingestion_reference": {
                "system": "SVACS AIS Ingestor",
                "pipeline_id": "ais-live-ingest-v1",
                "frequency": "real-time"
            }
        }

        r = await client.post(f"{BASE_URL}/datasets/", json=dataset_payload, headers=HEADERS)
        if r.status_code == 201:
            dataset = r.json()
            print(f"REGISTERED: {dataset['canonical_id']} | ID: {dataset['id']}")
        elif r.status_code == 409:
            print(f"ALREADY EXISTS: fetching existing record...")
            er = await client.get(f"{BASE_URL}/datasets/canonical/BHIV-DS-MARITIME-AIS-LIVE-001", headers=HEADERS)
            dataset = er.json()
            print(f"FOUND: {dataset['canonical_id']} | ID: {dataset['id']}")
        else:
            print(f"FAILED: {r.text}")
            return

        dataset_id = dataset["id"]
        print()

        # Step 2 - Register the schema (or get existing)
        print("Step 2: Registering schema v1.0.0...")
        schema_payload = {
            "dataset_id": dataset_id,
            "schema_version": "1.0.0",
            "field_definitions": [
                {
                    "field_name": "MMSI",
                    "data_type": "integer",
                    "nullable": False,
                    "description": "Maritime Mobile Service Identity -- unique vessel identifier",
                    "constraints": {"min": 100000000, "max": 999999999},
                    "example_value": 368084090
                },
                {
                    "field_name": "BaseDateTime",
                    "data_type": "datetime",
                    "nullable": False,
                    "description": "UTC timestamp of position report in ISO 8601 format",
                    "constraints": {"format": "ISO8601"},
                    "example_value": "2022-01-01T00:00:00"
                },
                {
                    "field_name": "LAT",
                    "data_type": "float",
                    "nullable": False,
                    "description": "Latitude coordinate in decimal degrees WGS84",
                    "constraints": {"min": -90.0, "max": 90.0},
                    "example_value": 29.93174
                },
                {
                    "field_name": "LON",
                    "data_type": "float",
                    "nullable": False,
                    "description": "Longitude coordinate in decimal degrees WGS84",
                    "constraints": {"min": -180.0, "max": 180.0},
                    "example_value": -89.99243
                },
                {
                    "field_name": "SOG",
                    "data_type": "float",
                    "nullable": True,
                    "description": "Speed over ground in knots",
                    "constraints": {"min": 0.0, "max": 102.3},
                    "example_value": 6.0
                },
                {
                    "field_name": "VesselType",
                    "data_type": "float",
                    "nullable": True,
                    "description": "ITU vessel type code. Common values: 31=Tug, 36=Sailing, 37=Pleasure, 57=Passenger, 60=Cargo",
                    "constraints": {"min": 0, "max": 99},
                    "example_value": 57.0
                }
            ],
            "compatibility_rules": {
                "backward_compatible": True,
                "breaking_changes": [],
                "migration_notes": "Initial schema version. All fields sourced directly from AIS protocol."
            },
            "schema_notes": "Schema derived from ITU-R M.1371 AIS standard. VesselType follows MMSI type codes.",
            "created_by": "Ankita"
        }

        sr = await client.post(f"{BASE_URL}/schemas/", json=schema_payload, headers=HEADERS)
        if sr.status_code == 201:
            schema = sr.json()
            schema_id = schema["id"]
            print(f"SCHEMA REGISTERED: v{schema['schema_version']} | ID: {schema_id}")
        elif sr.status_code == 409:
            print(f"SCHEMA ALREADY EXISTS: fetching existing...")
            schemas_r = await client.get(f"{BASE_URL}/schemas/dataset/{dataset_id}", headers=HEADERS)
            schemas = schemas_r.json()
            schema = schemas[0]
            schema_id = schema["id"]
            print(f"FOUND: v{schema['schema_version']} | ID: {schema_id}")
        else:
            print(f"FAILED to register schema: {sr.text}")
            return
        print()

        # Step 3 - Freeze the schema
        print("Step 3: Freezing schema...")
        fr = await client.post(f"{BASE_URL}/schemas/{schema_id}/freeze", headers=HEADERS)
        if fr.status_code == 200:
            print(f"SCHEMA FROZEN: v{fr.json()['schema_version']} -- now immutable and replay-safe")
        print()

        # Step 4 - Add INGESTION provenance record
        print("Step 4: Adding INGESTION provenance record...")
        prov_payload = {
            "event_type": "INGESTION",
            "source_system": "AIS Maritime Tracking Infrastructure",
            "source_reference": "svacs-unified-core/ais_feed",
            "ingestion_pipeline": "ais-live-ingest-v1",
            "trust_at_event": "TRUSTED",
            "recorded_by": "Ankita",
            "notes": "Initial ingestion of 10,000 AIS vessel tracking records from 2022-01-01. Data sourced from SVACS AIS ingestor. Telemetry continuity verified by SVACS governance sprint.",
            "is_replay_safe": True,
            "replay_context": {
                "replay_window": "2022-01-01T00:00:00Z to 2022-01-01T23:59:59Z",
                "deterministic": True,
                "constraints": "Timestamp gaps possible in high-traffic zones"
            }
        }

        pr = await client.post(f"{BASE_URL}/datasets/{dataset_id}/provenance", json=prov_payload, headers=HEADERS)
        if pr.status_code == 201:
            print(f"PROVENANCE ADDED: INGESTION event recorded")
        print()

        # Step 5 - Add VALIDATION provenance record
        print("Step 5: Adding VALIDATION provenance record...")
        val_prov_payload = {
            "event_type": "VALIDATION",
            "source_system": "SVACS Governance Engine",
            "recorded_by": "Ankita",
            "notes": "Governance validation completed. Telemetry continuity verified. Append-only lineage confirmed. Schema stability reviewed. Dataset classified as TRUSTED by SVACS governance sprint.",
            "trust_at_event": "TRUSTED",
            "is_replay_safe": True
        }

        vr = await client.post(f"{BASE_URL}/datasets/{dataset_id}/provenance", json=val_prov_payload, headers=HEADERS)
        if vr.status_code == 201:
            print(f"PROVENANCE ADDED: VALIDATION event recorded")
        print()

        # Step 5b - Add TRUST_CHANGE provenance record
        print("Step 5b: Adding TRUST_CHANGE provenance record...")
        trust_prov_payload = {
            "event_type": "TRUST_CHANGE",
            "source_system": "SVACS Governance Engine",
            "recorded_by": "Ankita",
            "notes": "Trust classified as TRUSTED. Governance validation completed by SVACS sprint. Telemetry continuity verified. Append-only lineage confirmed.",
            "trust_at_event": "TRUSTED",
            "is_replay_safe": False
        }

        tpr = await client.post(f"{BASE_URL}/datasets/{dataset_id}/provenance", json=trust_prov_payload, headers=HEADERS)
        if tpr.status_code == 201:
            print(f"PROVENANCE ADDED: TRUST_CHANGE event recorded")
        print()


       # Step 6 - Add extended metadata noting ecosystem relationships
        print("Step 6: Updating dataset with ecosystem integration notes...")
        update_payload = {
            "extended_metadata": {
                "ecosystem_relationships": ["BHIV-DS-LINEAGE-CHAIN-001"],
                "source_sprint": "SVACS-Distributed-Replay-Resilience",
                "data_volume": "10000 records",
                "time_range": "2022-01-01",
                "geographic_coverage": "US coastal waters",
                "integration_status": "ACTIVE"
            }
        }
        ur = await client.patch(f"{BASE_URL}/datasets/{dataset_id}", json=update_payload, headers=HEADERS)
        if ur.status_code == 200:
            print(f"DATASET UPDATED: Extended metadata added")
        print()

        # Step 7 - Validate provenance chain
        print("Step 7: Validating provenance chain...")
        vpr = await client.get(f"{BASE_URL}/discovery/provenance/validate/{dataset_id}", headers=HEADERS)
        if vpr.status_code == 200:
            validation = vpr.json()
            print(f"PROVENANCE VALID: {validation['valid']}")
            print(f"RECORD COUNT: {validation['record_count']}")
            print(f"EVENT TYPES: {validation['event_types_present']}")
            print(f"TANTRA READY: {validation['tantra_ready']}")
            print(f"REPLAY SAFE: {validation['replay_safe']}")
        print()

        print("=== AIS DATASET REGISTRATION COMPLETE ===")
        print(f"Dataset ID: {dataset_id}")
        print(f"Schema ID: {schema_id}")
        print("Full metadata flow demonstrated:")
        print("  Registration -> Schema -> Freeze -> Provenance -> Relationship -> Validation")

asyncio.run(register_ais_dataset())
