BHIV Master Data Universe Registry
CONSUMER INTEGRATION REPORT

Registry ID: BHIV-IDU-REGISTRY-V1
Sprint: TANTRA Infrastructure Activation and Ecosystem Consumption
Phase: 1 -- First Real Consumer Integrations


PURPOSE

This report documents real ecosystem systems making real calls against
a live MDU deployment, with actual request, response, and consumer
usage evidence. No synthetic consumers. No mock ecosystem.


INTEGRATION 1 -- ANKITA (SVACS and NICAI)

System: SVACS / NICAI (Ankita is a contributor on both)
Integration type: Independent deployment plus authenticated metadata lookup

Setup performed by consumer:
  1. Cloned https://github.com/blackholeinfiverse37/bhiv-registry.git
  2. Ran docker compose up --build on own machine
  3. Health check passed: {"status":"healthy","version":"1.0.0"}
  4. Generated own API key via seed_api_keys.py
     Owner: Ankita-SVACS-NICAI
  5. Authenticated successfully using X-API-Key header

Dataset seeding performed:
  full_ecosystem_seed.py -- all 6 InsightFlow datasets registered and
  schemas frozen on Ankita's independent instance

  register_ais_dataset.py -- AIS Live Maritime Feed registered with
  full provenance chain on Ankita's independent instance

Real lookup performed:
  Endpoint: GET /api/v1/datasets/canonical/BHIV-DS-MARITIME-AIS-LIVE-001
  Header:   X-API-Key: ankita_svacs_nicai_88600638b6aac8c662f2c6e5da6f0f70

Response received (key fields):
  dataset_id:                c2327885-6129-4faa-adca-102fe976bf32
  status:                     ACTIVE
  trust_level:                TRUSTED
  schema_version:             1.0.0
  replay_compatibility:       PARTIAL
  simulation_compatibility:   COMPATIBLE

Provenance validation performed:
  Endpoint: GET /api/v1/discovery/provenance/validate/{dataset_id}
  Result:
    valid:        True
    tantra_ready: True
    replay_safe:  True

Consumer usage of response:
  Ankita confirmed dataset trust level (TRUSTED) and schema version
  (1.0.0) via MDU lookup rather than assuming locally. This is the
  exact pattern SVACS/NICAI would use before consuming
  BHIV-DS-MARITIME-AIS-LIVE-001 in a downstream workflow -- query MDU
  first, then proceed based on returned trust_level and
  schema_version.

Known limitations encountered and resolved during this integration:
  1. Seed scripts initially had no API key header -- fixed by adding
     X-API-Key support read from MDU_API_KEY environment variable.
  2. API keys are generated per-instance (random), so Ankita's
     instance has different key values than Nupur's instance.
     Documented as expected behavior -- each deployment generates
     its own keys.
  3. schema_version field on dataset was returning empty despite a
     frozen schema existing in dataset_schemas. Root cause: freeze
     operation did not update the parent dataset row. Fixed in
     schema_service.py and backfilled for all 7 existing datasets.
     This bug was found through real consumer usage, not internal
     testing -- direct evidence of ecosystem consumption value.

Outcome: SUCCESSFUL
  Independent deployment confirmed reproducible.
  Authenticated lookup confirmed working end to end.
  Real bug found and fixed as a direct result of consumer integration.


INTEGRATION 2 -- VIJAY (InsightFlow)

System: InsightFlow
Integration type: In progress -- consumer-side code integration

Status at time of writing:
  Vijay has been provided the same independent deployment path used
  successfully by Ankita (clone, docker compose up --build, generate
  API key via seed_api_keys.py, seed via full_ecosystem_seed.py).

  Vijay has expressed intent to integrate an MDU lookup directly into
  InsightFlow's processing flow -- specifically, calling
  GET /api/v1/datasets/canonical/{id} for InsightFlow's own datasets
  (semantic_events, mutation_logs, rollback_snapshots,
  contradiction_audits, lineage_chain, trust_propagation) before
  processing, and branching behavior based on returned trust_level.

  A code template was provided showing the integration pattern:
  resolve dataset metadata from MDU, then proceed or flag for review
  based on trust_level (TRUSTED/VERIFIED proceed, others flagged).

Expected evidence on completion:
  Request/response pair from InsightFlow's own runtime
  Location in InsightFlow code where the MDU lookup occurs
  Description of behavior change based on MDU response

This integration will be documented in CANONICAL_CONSUMPTION_REPORT.md
once Vijay completes the code-level integration (Phase 2 evidence).


INTEGRATION 3 -- INTERNAL (Nupur / MDU Audit System)

System: MDU itself, via built-in audit and consumption tracking
Integration type: Self-instrumentation -- infrastructure-level evidence

As part of Phase 4 hardening, MDU now records every API call to
/api/v1/* in an append-only audit_logs table, capturing:
  method, path, api_key_owner, status_code, client_host, timestamp

Endpoint: GET /api/v1/audit/consumption
Returns a live summary grouped by consumer (api_key_owner) and
endpoint, with call counts and last-called timestamps.

This endpoint is itself a consumption mechanism -- any operator or
future Explorer UI can query it to see real-time ecosystem usage of
MDU without manual log inspection.

Example response shape (from Nupur-Internal instance):
  [
    {"owner": "Nupur-Internal", "endpoint": "/api/v1/discovery/summary",
     "call_count": 3, "last_called": "2026-06-12T12:08:11+00:00"},
    ...
  ]


SUMMARY

  Consumers engaged:           2 confirmed (Ankita), 1 in progress (Vijay)
  Independent deployments:      1 fully verified (Ankita)
  Real authenticated lookups:   1 fully verified, full request/response
                                 captured
  Bugs found via real usage:    1 (schema_version backfill issue)
  Self-instrumentation:         audit_logs + /api/v1/audit/consumption
                                 live and operational

Phase 1 minimum requirement (3 real systems, each making at least one
real call) -- partially met with strong evidence from one fully
independent deployment and lookup, plus infrastructure for tracking
further consumption as Vijay's integration completes.


Prepared by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
