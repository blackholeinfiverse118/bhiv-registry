BHIV Master Data Universe Registry
TANTRA CHAIN EVIDENCE

Registry ID: BHIV-IDU-REGISTRY-V1
Sprint: TANTRA Infrastructure Activation and Ecosystem Consumption
Phase: 3 -- Full TANTRA Chain Demonstration


PURPOSE

This report traces one complete, evidence-backed chain in which MDU
participates: dataset registration through MDU, consumer lookup,
downstream validation, and audit trail linkage. All identifiers,
timestamps, and responses below are real, captured from actual runs,
not constructed for illustration.


THE CHAIN

  Dataset (AIS Live Maritime Feed, real data, Ankita / SVACS)
    --> MDU registration (canonical ID, schema, provenance)
    --> Consumer lookup (Ankita, independent MDU deployment)
    --> Downstream validation (provenance chain validation,
        TANTRA readiness check)
    --> Audit trail linkage (audit_logs / consumption endpoint)


STEP 1 -- DATASET

Source: Ankita, SVACS Governance Sprint
Raw data: AIS_file.xls -- 10,000 real vessel tracking records,
fields MMSI, BaseDateTime, LAT, LON, SOG, VesselType, dated
2022-01-01.


STEP 2 -- MDU REGISTRATION

Canonical ID assigned: BHIV-DS-MARITIME-AIS-LIVE-001
Dataset UUID:          c2327885-6129-4faa-adca-102fe976bf32

Registration call:
  POST /api/v1/datasets/
  Payload included: source_system, owner_name (Ankita), domain_primary
  (maritime), trust_level (TRUSTED), replay_compatibility (PARTIAL),
  simulation_compatibility (COMPATIBLE)

Schema registration:
  POST /api/v1/schemas/
  schema_version: 1.0.0
  6 field definitions (MMSI, BaseDateTime, LAT, LON, SOG, VesselType)
  derived from ITU-R M.1371 AIS standard

Schema freeze:
  POST /api/v1/schemas/{schema_id}/freeze
  Result: status FROZEN, frozen_at timestamp recorded
  Side effect (after fix): parent dataset.schema_version set to
  1.0.0, dataset.current_schema_id set to schema UUID

Provenance chain built (append-only, in order):
  ORIGIN        -- created automatically at registration
  INGESTION     -- AIS Maritime Tracking Infrastructure,
                   pipeline ais-live-ingest-v1
  VALIDATION    -- SVACS Governance Engine, telemetry continuity
                   verified
  TRUST_CHANGE  -- trust classified TRUSTED by Ankita


STEP 3 -- CONSUMER LOOKUP (REAL, INDEPENDENT DEPLOYMENT)

Consumer: Ankita, on her own machine, own Docker Compose deployment,
own PostgreSQL instance, own generated API key.

Setup chain:
  git clone https://github.com/blackholeinfiverse37/bhiv-registry.git
  docker compose up --build
  GET /health -> {"status":"healthy","version":"1.0.0"}
  python seed_api_keys.py -> key for Ankita-SVACS-NICAI generated
  MDU_API_KEY=<ankita_key> python full_ecosystem_seed.py
  MDU_API_KEY=<ankita_key> python register_ais_dataset.py

Lookup call:
  GET /api/v1/datasets/canonical/BHIV-DS-MARITIME-AIS-LIVE-001
  Header: X-API-Key: ankita_svacs_nicai_88600638b6aac8c662f2c6e5da6f0f70

Response (after schema_version fix and backfill):
  dataset_id:                c2327885-6129-4faa-adca-102fe976bf32
  status:                     ACTIVE
  trust_level:                TRUSTED
  schema_version:             1.0.0
  replay_compatibility:       PARTIAL
  simulation_compatibility:   COMPATIBLE


STEP 4 -- DOWNSTREAM VALIDATION

Provenance chain validation call:
  GET /api/v1/discovery/provenance/validate/c2327885-6129-4faa-adca-102fe976bf32

Result:
  valid:        True
  tantra_ready: True
  replay_safe:  True
  event_types_present: [ORIGIN, INGESTION, VALIDATION, TRUST_CHANGE]
  record_count: 6

This is the point at which MDU formally certifies the dataset as fit
for TANTRA ecosystem consumption -- chain is complete, starts with
ORIGIN, trust level is backed by a recorded TRUST_CHANGE event, and
replay compatibility is consistent with recorded provenance.


STEP 5 -- AUDIT TRAIL LINKAGE

Every call above (registration, schema operations, provenance writes,
the canonical lookup, and the validation call) is recorded in
audit_logs on the instance where it occurred, capturing method, path,
api_key_owner, status_code, and timestamp.

Consumption summary endpoint:
  GET /api/v1/audit/consumption

Returns, grouped by consumer and endpoint:
  owner, endpoint, call_count, last_called

This functions as the "Bucket evidence linkage" for this chain --
a queryable, append-only record that the above sequence of calls
occurred, against which canonical_id, dataset_id, schema_version,
and timestamps can all be cross-referenced.


TRACEABLE IDENTIFIERS SUMMARY

  canonical_id:    BHIV-DS-MARITIME-AIS-LIVE-001
  dataset_id:      c2327885-6129-4faa-adca-102fe976bf32
  schema_version:  1.0.0
  trust_level:     TRUSTED (set via TRUST_CHANGE provenance event)
  provenance event_types: ORIGIN, INGESTION, VALIDATION, TRUST_CHANGE
  tantra_ready:    True
  replay_safe:     True
  consumer:        Ankita-SVACS-NICAI (independent deployment)
  api_key_owner (audit_logs): Ankita-SVACS-NICAI


WHAT THIS CHAIN PROVES

1. A dataset registered in MDU carries a canonical ID, frozen schema,
   and append-only provenance chain that another team's independent
   MDU deployment can reproduce identically (Ankita's seed run
   produced the same 7 datasets, same canonical IDs, same trust
   levels as the originating instance).

2. A real consumer, on infrastructure they deployed themselves, can
   authenticate and retrieve complete canonical metadata for that
   dataset in a single call.

3. MDU's own validation endpoint independently certifies the dataset
   as TANTRA ready and replay safe based on the provenance chain --
   this is not a claim made by the dataset owner, it is computed by
   MDU from the recorded event history.

4. Every step in this chain is captured in an append-only audit log
   queryable via the registry itself, without external tooling.


WHAT IS NOT YET IN THIS CHAIN

  Vijay / InsightFlow participation -- in progress at time of
  writing. Once available, this would extend the chain with a second
  independent consumer and a second dataset family
  (semantic_events / mutation_logs / etc.), strengthening the
  "multiple real systems" requirement.

  A true cross-instance audit trail -- currently each deployment
  (Nupur's, Ankita's) has its own audit_logs. A shared/centralized
  MDU instance would allow a single audit_logs table to show calls
  from multiple real consumers, which is the strongest form of this
  evidence.


Prepared by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
