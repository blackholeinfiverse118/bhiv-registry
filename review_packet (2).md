BHIV Master Data Universe Registry
REVIEW PACKET

Registry ID: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
Sprint Lead: Nupur
Status: ACTIVE INFRASTRUCTURE


1. ENTRY POINT

The BHIV Master Data Universe Registry is the canonical federated dataset metadata layer for the TANTRA ecosystem.

It is a metadata registry. It stores information about datasets, not the datasets themselves.

Its job is to answer:

- What datasets exist in the BHIV ecosystem?
- Where did they come from and how were they transformed?
- Can this dataset be trusted for a given intelligence use case?
- Can this dataset be replayed deterministically?
- Is this dataset simulation-compatible?
- What are the field definitions of this dataset?
- What is the provenance chain of this dataset?

Single command deployment:
  docker compose up --build

API live at:
  http://localhost:8000
  http://localhost:8000/docs
  http://localhost:8000/health


2. WHAT THIS REGISTRY GOVERNS vs WHAT IT DOES NOT

Governs:
  Dataset metadata registration
  Schema versioning and governance
  Provenance tracking and lineage
  Trust classification
  Replay-safe metadata
  Simulation compatibility metadata
  Dataset discoverability
  Formal onboarding flow

Does NOT govern:
  Actual data storage
  Orchestration execution
  Intelligence routing
  Runtime decisions
  Semantic authority
  Data transformation


3. TEAM STRUCTURE

  Nupur     Backend + Data Architecture + Sprint Lead
  Soham     Fullstack + Dataset Explorer UI (Nikhil picks up on 23rd)
  Ankita    Schema Governance + Trust Metadata + Validation Standards
  Vijay     Integration Mapping + Dataset Onboarding + Ecosystem Convergence


4. TECH STACK

  API Framework    FastAPI 0.115.0
  Database         PostgreSQL 16
  ORM              SQLAlchemy 2.0.36 async
  Validation       Pydantic 2.10.0
  Migrations       Alembic 1.14.0
  Runtime          Python 3.12 in Docker container
  Containerization Docker Compose


5. REPOSITORY STRUCTURE

  bhiv-registry/
  |
  |-- docker-compose.yml
  |-- Dockerfile
  |-- .env.example
  |-- README.md
  |-- DEPLOYMENT_RUNBOOK.md
  |-- INFRA_ACTIVATION_REPORT.md
  |-- ECOSYSTEM_INTEGRATION_REPORT.md
  |-- ROAD_TO_PRODUCTION.md
  |-- review_packet.md
  |
  |-- docs/
  |   |-- architecture_overview.md
  |   |-- metadata_standards.md
  |   |-- onboarding_flow.md
  |   |-- tantra_readiness.md
  |   |-- governance/
  |       |-- dataset_trust_classification.md
  |       |-- governance_review.txt
  |
  |-- backend/
      |-- requirements.txt
      |-- alembic.ini
      |-- seed_data.py
      |-- full_ecosystem_seed.py
      |-- register_ais_dataset.py
      |-- migrations/
      |   |-- versions/
      |       |-- 351b5952de3b_initial_schema.py
      |       |-- 31f3a745de49_add_onboarding_table.py
      |-- app/
          |-- main.py
          |-- core/config.py
          |-- db/base.py
          |-- models/registry.py
          |-- schemas/registry.py
          |-- services/
          |   |-- dataset_service.py
          |   |-- schema_service.py
          |   |-- relationship_service.py
          |   |-- trust_service.py
          |   |-- discovery_service.py
          |   |-- provenance_service.py
          |   |-- onboarding_service.py
          |-- api/v1/
              |-- router.py
              |-- endpoints/
                  |-- datasets.py
                  |-- schemas.py
                  |-- relationships.py
                  |-- discovery.py
                  |-- onboarding.py


6. DATABASE MODELS

6.1 Dataset
Primary registry entity. Every dataset gets a canonical UUID and canonical ID.

Key fields:
  canonical_id              BHIV-DS-DOMAIN-NAME-NUMBER format enforced
  status                    ACTIVE, DEPRECATED, ARCHIVED, UNDER_REVIEW
  trust_level               VERIFIED, TRUSTED, PROVISIONAL, UNVERIFIED, QUARANTINE
  replay_compatibility      FULL, PARTIAL, CONDITIONAL, NONE
  simulation_compatibility  NATIVE, COMPATIBLE, ADAPTABLE, INCOMPATIBLE
  source_location           Reference pointer only -- not actual data
  ingestion_reference       JSONB pointer to ingestion pipeline
  extended_metadata         JSONB flexible metadata

6.2 DatasetSchema
Versioned field definitions. Immutable once frozen.

Key fields:
  schema_version        Semantic version string
  status                DRAFT, ACTIVE, FROZEN, RETIRED
  field_definitions     JSONB array of field objects
  compatibility_rules   JSONB backward compatibility metadata
  previous_schema_id    Link to prior version for lineage
  frozen_at             When frozen becomes immutable

Field definition structure:
  field_name, data_type, nullable, description, constraints, example_value

6.3 ProvenanceRecord
Append-only chain of events. Never modified, only appended.

Event types:
  ORIGIN          initial registration
  INGESTION       data ingestion event
  TRANSFORMATION  data transformation applied
  VALIDATION      validation event
  TRUST_CHANGE    trust level updated
  SCHEMA_CHANGE   schema version updated

Key fields:
  event_type, source_system, source_reference, trust_at_event,
  recorded_by, recorded_at, is_replay_safe, replay_context

6.4 DatasetRelationship
Parent-child and dependency mapping.

Relationship types:
  DERIVED_FROM, DEPENDS_ON, MERGED_FROM, FILTERED_FROM

6.5 DatasetOnboardingRequest
Formal submission and review flow.

Status flow:
  PENDING_REVIEW --> APPROVED --> REGISTERED
  PENDING_REVIEW --> REJECTED


7. API SURFACE -- 34 ENDPOINTS

Datasets (10)
  POST   /api/v1/datasets/
  GET    /api/v1/datasets/
  GET    /api/v1/datasets/canonical/{canonical_id}
  GET    /api/v1/datasets/{id}
  PATCH  /api/v1/datasets/{id}
  POST   /api/v1/datasets/{id}/trust
  POST   /api/v1/datasets/{id}/trust/transition
  GET    /api/v1/datasets/{id}/trust/history
  GET    /api/v1/datasets/{id}/provenance
  POST   /api/v1/datasets/{id}/provenance

Schemas (5)
  POST   /api/v1/schemas/
  GET    /api/v1/schemas/dataset/{id}
  GET    /api/v1/schemas/{id}
  POST   /api/v1/schemas/{id}/freeze
  PATCH  /api/v1/schemas/{id}/activate

Dataset Relationships (4)
  POST   /api/v1/relationships/
  GET    /api/v1/relationships/dataset/{id}
  GET    /api/v1/relationships/{id}
  DELETE /api/v1/relationships/{id}

Discovery (8)
  GET    /api/v1/discovery/summary
  GET    /api/v1/discovery/replay-safe
  GET    /api/v1/discovery/simulation-ready
  GET    /api/v1/discovery/trusted
  GET    /api/v1/discovery/quarantined
  GET    /api/v1/discovery/by-team/{team}
  GET    /api/v1/discovery/provenance/validate/{id}
  GET    /api/v1/discovery/provenance/validate-all

Onboarding (5)
  POST   /api/v1/onboarding/submit
  GET    /api/v1/onboarding/pending
  GET    /api/v1/onboarding/all
  GET    /api/v1/onboarding/{id}
  POST   /api/v1/onboarding/{id}/review

Health (2)
  GET    /
  GET    /health


8. CORE FLOWS

8.1 Dataset Registration Flow

  POST /api/v1/datasets/
  canonical ID validated on entry
  ORIGIN provenance record created automatically
  dataset active in registry immediately

8.2 Formal Onboarding Flow

  POST /api/v1/onboarding/submit
  status: PENDING_REVIEW
  GET /api/v1/onboarding/pending to see review queue
  POST /api/v1/onboarding/{id}/review with decision APPROVED
  dataset auto-registered with full audit trail
  status: REGISTERED

8.3 Schema Registration Flow

  POST /api/v1/schemas/               status: DRAFT
  PATCH /api/v1/schemas/{id}/activate status: ACTIVE
  POST /api/v1/schemas/{id}/freeze    status: FROZEN (immutable, replay-safe)

8.4 Trust Classification Flow

  POST /api/v1/datasets/{id}/trust/transition
  valid transitions enforced
  TRUST_CHANGE provenance record created automatically
  governance note required for QUARANTINE and UNVERIFIED

  Valid transitions:
    UNVERIFIED  --> PROVISIONAL, QUARANTINE
    PROVISIONAL --> TRUSTED, UNVERIFIED, QUARANTINE
    TRUSTED     --> VERIFIED, PROVISIONAL, QUARANTINE
    VERIFIED    --> TRUSTED, QUARANTINE
    QUARANTINE  --> UNVERIFIED after review only

8.5 Provenance Validation Flow

  GET /api/v1/discovery/provenance/validate-all
  checks every dataset chain
  confirms ORIGIN event present
  confirms trust changes are recorded
  returns TANTRA readiness for each dataset


9. REAL ECOSYSTEM DATASETS REGISTERED

9.1 BHIV-DS-MARITIME-AIS-LIVE-001
  Source:       Ankita, SVACS Governance Sprint
  Domain:       maritime
  Trust:        TRUSTED
  Replay:       PARTIAL
  Simulation:   COMPATIBLE
  Data:         10,000 real vessel tracking records from 2022-01-01
  Schema:       v1.0.0 FROZEN -- 6 fields
                MMSI, BaseDateTime, LAT, LON, SOG, VesselType
  Provenance:   ORIGIN, INGESTION, VALIDATION, TRUST_CHANGE
  TANTRA Ready: True
  Replay Safe:  True

9.2 BHIV-DS-REPLAY-SEMANTIC-EVENTS-001
  Source: Vijay InsightFlow | Trust: TRUSTED | Simulation: NATIVE
  Schema: v1.0.0 FROZEN -- 7 fields
  Fields: event_id, trace_id, event_type, replay_state, source_node, event_timestamp, validation_status

9.3 BHIV-DS-GOVERNANCE-MUTATION-LOGS-001
  Source: Vijay InsightFlow | Trust: VERIFIED | Simulation: COMPATIBLE
  Schema: v1.0.0 FROZEN -- 8 fields
  Fields: mutation_id, entity_id, entity_type, mutation_type, mutated_by, previous_state, mutation_timestamp, governance_approved

9.4 BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001
  Source: Vijay InsightFlow | Trust: PROVISIONAL | Simulation: ADAPTABLE
  Schema: v1.0.0 FROZEN -- 7 fields
  Fields: snapshot_id, entity_id, snapshot_type, state_data, schema_version, snapshot_timestamp, recovery_validated

9.5 BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001
  Source: Vijay InsightFlow | Trust: TRUSTED | Simulation: COMPATIBLE
  Schema: v1.0.0 FROZEN -- 8 fields
  Fields: audit_id, contradiction_type, source_a, source_b, severity, resolution_status, detected_at, resolved_at

9.6 BHIV-DS-LINEAGE-CHAIN-001
  Source: Vijay InsightFlow | Trust: VERIFIED | Simulation: NATIVE
  Schema: v1.0.0 FROZEN -- 8 fields
  Fields: lineage_id, trace_id, parent_id, dataset_reference, schema_version, lineage_type, is_append_only, recorded_at

9.7 BHIV-DS-TRUST-PROPAGATION-001
  Source: Vijay InsightFlow | Trust: PROVISIONAL | Simulation: ADAPTABLE
  Schema: v1.0.0 FROZEN -- 7 fields
  Fields: propagation_id, source_dataset_id, target_service, trust_level, propagation_status, cross_service_validated, propagated_at


10. REGISTRY SUMMARY

  Total datasets:   7
  VERIFIED:         2
  TRUSTED:          3
  PROVISIONAL:      2
  UNVERIFIED:       0
  QUARANTINE:       0

  NATIVE:           2
  COMPATIBLE:       3
  ADAPTABLE:        2
  INCOMPATIBLE:     0

  All datasets:     ACTIVE
  All schemas:      FROZEN
  All chains:       VALID
  TANTRA ready:     All confirmed


11. DEPLOYMENT

  docker compose up --build

Automatic on startup:
  PostgreSQL 16 starts and passes health check
  Alembic runs 2 migration versions
  FastAPI starts on port 8000

Verify:
  http://localhost:8000/health
  Expected: {"status":"healthy","version":"1.0.0"}

Team onboarding -- 4 steps only:
  1. Install Docker Desktop
  2. git clone https://github.com/blackholeinfiverse37/bhiv-registry.git
  3. cd bhiv-registry
  4. docker compose up --build

No Python, no PostgreSQL, no manual configuration required.
Full details in DEPLOYMENT_RUNBOOK.md


12. MIGRATIONS

  351b5952de3b -- initial_schema (5 tables)
  31f3a745de49 -- add_onboarding_table

Run manually:
  docker compose exec api bash
  alembic upgrade head


13. ARCHITECTURE BOUNDARIES

The registry must NEVER drift into:
  Orchestration infrastructure
  Intelligence execution
  Runtime routing
  Centralized mega-storage
  Semantic authority
  Governance enforcement

The registry governs:
  Data structure
  Provenance
  Trust classification
  Discoverability

NOT intelligence meaning.


14. KNOWN GAPS AND REAL REMAINING WORK

Authentication and authorization
  No auth. All endpoints publicly accessible.
  Required: API key or OAuth 2.0 with role-based access.

HTTPS
  HTTP only.
  Required: nginx reverse proxy with TLS.

Automated database backups
  No scheduled backup.
  Required: Scheduled pg_dump to external storage.

Rate limiting
  No throttling.
  Required: Rate limiting middleware.

Dataset Explorer UI
  Not started. Assigned to Nikhil, available from 23rd.

Replay compatibility classification
  Most datasets at NONE. AIS Feed at PARTIAL.
  Needs classification by domain owners in next sprint.


15. SPRINT CONTRIBUTIONS

Ankita
  Governance review of all 7 datasets
  Trust classification for all datasets
  AIS Live Maritime Feed real data submission
  Governance artifacts in docs/governance/

Vijay
  Dataset inventory for 6 InsightFlow datasets
  Simulation compatibility classification
  Schema field structure for InsightFlow datasets

Nupur
  Full backend architecture and implementation
  Docker deployment infrastructure
  All 34 API endpoints
  All 7 service layers
  Alembic migrations
  All documentation
  Sprint coordination and convergence discipline


Prepared by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
