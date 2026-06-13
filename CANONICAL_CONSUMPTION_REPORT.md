BHIV Master Data Universe Registry
CANONICAL CONSUMPTION REPORT

Registry ID: BHIV-IDU-REGISTRY-V1
Sprint: TANTRA Infrastructure Activation and Ecosystem Consumption
Phase: 2 -- Canonical Registry Participation


PURPOSE

This report demonstrates a consumer moving from locally-assumed or
incomplete metadata to MDU-resolved canonical metadata, with a real
before/after/benefit/gaps narrative backed by actual request and
response evidence.


CASE -- AIS LIVE MARITIME FEED SCHEMA RESOLUTION (Ankita / SVACS-NICAI)

System startup to downstream operation flow demonstrated:
  Consumer deployment startup
    --> MDU lookup (GET /api/v1/datasets/canonical/{id})
    --> metadata resolution (schema_version field)
    --> downstream operation (consumer decision based on schema
        version for replay/processing)


BEFORE

Ankita independently deployed MDU (docker compose up --build),
seeded the AIS Live Maritime Feed dataset
(BHIV-DS-MARITIME-AIS-LIVE-001) including a frozen schema v1.0.0,
and performed an authenticated lookup:

  GET /api/v1/datasets/canonical/BHIV-DS-MARITIME-AIS-LIVE-001
  Header: X-API-Key: ankita_svacs_nicai_88600638b6aac8c662f2c6e5da6f0f70

Response received (relevant field):
  schema_version: ""    (empty)

At this point, despite a schema existing and being FROZEN in the
dataset_schemas table (verified via
GET /api/v1/schemas/dataset/{id}), the canonical dataset record
itself did not expose which schema version was active. A downstream
consumer reading only the dataset record (the typical canonical
lookup pattern) would see no schema version -- effectively
locally-unresolved metadata, since the consumer would need to make a
second call to the schemas endpoint and infer the active version
itself, or fall back to its own locally assumed schema version.


ROOT CAUSE IDENTIFIED

SchemaService.freeze_schema() set the schema's own status to FROZEN
and recorded frozen_at, but never wrote back to the parent Dataset
row's current_schema_id or schema_version columns. The canonical
dataset record and its schema were therefore disconnected after
freeze.


FIX APPLIED

1. schema_service.py freeze_schema() now also sets, on the parent
   Dataset:
     dataset.current_schema_id = schema.id
     dataset.schema_version = schema.schema_version

2. backfill_schema_versions.py was run once to repair the 7 datasets
   that were frozen prior to the fix. Output:
     UPDATED: BHIV-DS-MARITIME-AIS-LIVE-001 -> schema_version 1.0.0
     UPDATED: BHIV-DS-REPLAY-SEMANTIC-EVENTS-001 -> schema_version 1.0.0
     UPDATED: BHIV-DS-GOVERNANCE-MUTATION-LOGS-001 -> schema_version 1.0.0
     UPDATED: BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001 -> schema_version 1.0.0
     UPDATED: BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001 -> schema_version 1.0.0
     UPDATED: BHIV-DS-LINEAGE-CHAIN-001 -> schema_version 1.0.0
     UPDATED: BHIV-DS-TRUST-PROPAGATION-001 -> schema_version 1.0.0
     Backfill complete. 7 datasets updated.


AFTER

Ankita pulled the fix, re-ran the backfill on her independent
deployment, and repeated the same lookup:

  GET /api/v1/datasets/canonical/BHIV-DS-MARITIME-AIS-LIVE-001
  Header: X-API-Key: ankita_svacs_nicai_88600638b6aac8c662f2c6e5da6f0f70

Response received (relevant fields):
  trust_level:               TRUSTED
  schema_version:            1.0.0
  replay_compatibility:       PARTIAL
  simulation_compatibility:   COMPATIBLE

A single canonical lookup now resolves trust, schema version, replay
compatibility, and simulation compatibility together -- everything a
downstream system needs to decide whether and how to consume this
dataset, in one call.


BENEFIT

Before the fix, a consumer following the canonical lookup pattern
(GET /datasets/canonical/{id}) would receive incomplete metadata --
schema_version empty -- and would either:
  a) make a second call to /schemas/dataset/{id} and parse the array
     to infer the active version, or
  b) fall back to a locally assumed/hardcoded schema version, which
     is exactly the "locally assumed metadata" pattern this sprint
     phase targets for elimination.

After the fix, one canonical call returns a complete, self-consistent
metadata record. The consumer's downstream operation (e.g. deciding
whether AIS records can be processed against schema v1.0.0 field
definitions) can now be driven entirely by the MDU response with no
local assumption and no second call.

This also means the fix was discovered and corrected as a direct
result of real ecosystem consumption -- not internal testing. This is
itself evidence that MDU is being treated as relied-upon
infrastructure: a real consumer's workflow surfaced a defect that
internal seeding and validation scripts had not.


REMAINING GAPS

1. Vijay / InsightFlow integration (calling MDU from within
   InsightFlow's own processing code, branching on trust_level) is
   in progress at time of writing. This would extend the canonical
   consumption pattern from "lookup before manual review" to
   "lookup gates automated processing" -- a stronger Phase 2 case.
   To be added to this report or a follow-up once available.

2. RBAC is not yet implemented (see PRODUCTION_HARDENING_REPORT.md).
   Any authenticated consumer can currently write to the registry,
   including changing trust levels. Canonical consumption today
   relies on consumer discipline (read-only usage by convention) for
   write-capable endpoints.

3. Only one dataset (BHIV-DS-MARITIME-AIS-LIVE-001) has been used in
   a full real-consumer canonical lookup cycle. The other 6 datasets
   have schemas registered and frozen (and now correctly linked
   after the backfill) but have not yet been the subject of a
   real-consumer lookup.


Prepared by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
