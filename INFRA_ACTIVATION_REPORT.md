BHIV Master Data Universe Registry
INFRASTRUCTURE ACTIVATION REPORT

Registry ID: BHIV-IDU-REGISTRY-V1
Sprint: MDU Live Infrastructure Activation
Status: ACTIVE


DEPLOYMENT STATUS

The BHIV MDU Registry has been successfully activated as live deployable infrastructure.

Single command deployment is operational:
  docker compose up --build

Full stack comes up in under 90 seconds on standard hardware:
- PostgreSQL 16 database container starts and passes health check
- Alembic migrations run automatically
- FastAPI application starts and serves on port 8000

Health endpoint confirmed operational:
  GET /health
  Response: {"status":"healthy","version":"1.0.0"}


RUNTIME TOPOLOGY

Two containers running under a shared Docker network:

bhiv_mdu_db
  Image: postgres:16-alpine
  Port: 5432
  Volume: postgres_data (persistent across restarts)
  Health: pg_isready check every 10 seconds
  Restart policy: unless-stopped

bhiv_mdu_api
  Image: bhiv-registry-api (built from backend/Dockerfile)
  Port: 8000
  Startup sequence: wait for db healthy, run migrations, start uvicorn
  Restart policy: unless-stopped


DATABASE STATUS

Tables created via Alembic migrations:
  datasets                      -- canonical dataset registry
  dataset_schemas               -- versioned schema definitions
  provenance_records            -- append-only provenance chain
  dataset_relationships         -- parent-child lineage mapping
  dataset_onboarding_requests   -- formal submission and review flow

Migration versions applied:
  351b5952de3b -- initial_schema
  31f3a745de49 -- add_onboarding_table

Migrations are idempotent and run safely on every container restart.


API STATUS

All 34 endpoints operational across 6 sections:

Datasets (10 endpoints)
  POST   /api/v1/datasets/                          Register dataset
  GET    /api/v1/datasets/                          Search and filter
  GET    /api/v1/datasets/canonical/{id}            Get by canonical ID
  GET    /api/v1/datasets/{id}                      Get by UUID
  PATCH  /api/v1/datasets/{id}                      Update metadata
  POST   /api/v1/datasets/{id}/trust                Update trust direct
  POST   /api/v1/datasets/{id}/trust/transition     Governed trust transition
  GET    /api/v1/datasets/{id}/trust/history        Trust audit history
  GET    /api/v1/datasets/{id}/provenance           Get provenance chain
  POST   /api/v1/datasets/{id}/provenance           Add provenance event

Schemas (5 endpoints)
  POST   /api/v1/schemas/                           Create schema version
  GET    /api/v1/schemas/dataset/{id}               Get schemas for dataset
  GET    /api/v1/schemas/{id}                       Get specific schema
  POST   /api/v1/schemas/{id}/freeze                Freeze schema (immutable)
  PATCH  /api/v1/schemas/{id}/activate              Activate draft schema

Dataset Relationships (4 endpoints)
  POST   /api/v1/relationships/                     Create relationship
  GET    /api/v1/relationships/dataset/{id}         Get relationships for dataset
  GET    /api/v1/relationships/{id}                 Get specific relationship
  DELETE /api/v1/relationships/{id}                 Remove relationship

Discovery (8 endpoints)
  GET    /api/v1/discovery/summary                  Registry dashboard
  GET    /api/v1/discovery/replay-safe              Replay-safe datasets
  GET    /api/v1/discovery/simulation-ready         Simulation-ready datasets
  GET    /api/v1/discovery/trusted                  Trusted datasets
  GET    /api/v1/discovery/quarantined              Quarantined datasets
  GET    /api/v1/discovery/by-team/{team}           Datasets by team
  GET    /api/v1/discovery/provenance/validate/{id} Validate single chain
  GET    /api/v1/discovery/provenance/validate-all  Validate all chains

Onboarding (5 endpoints)
  POST   /api/v1/onboarding/submit                  Submit for review
  GET    /api/v1/onboarding/pending                 Get pending requests
  GET    /api/v1/onboarding/all                     Get all requests
  GET    /api/v1/onboarding/{id}                    Get specific request
  POST   /api/v1/onboarding/{id}/review             Approve or reject

Health (2 endpoints)
  GET    /                                          Registry identity
  GET    /health                                    Health check


INTEGRATED METADATA FLOWS DEMONSTRATED

Flow 1 -- AIS Live Maritime Feed (Real Ecosystem Data)
  Source: Ankita, SVACS Governance Sprint
  Dataset: BHIV-DS-MARITIME-AIS-LIVE-001
  Records: 10,000 vessel tracking records
  Flow completed:
    Registration with canonical ID
    Schema registration (6 fields, ITU-R M.1371 standard)
    Schema frozen (immutable, replay-safe)
    INGESTION provenance recorded
    VALIDATION provenance recorded
    TRUST_CHANGE provenance recorded
    Extended metadata with ecosystem integration notes
    Provenance chain validated: TANTRA READY, REPLAY SAFE

Flow 2 -- Sprint 1 Ecosystem Datasets (6 datasets)
  Source: Vijay, InsightFlow integration mapping
  Datasets registered with trust and simulation classification:
    BHIV-DS-REPLAY-SEMANTIC-EVENTS-001    TRUSTED    NATIVE
    BHIV-DS-GOVERNANCE-MUTATION-LOGS-001  VERIFIED   COMPATIBLE
    BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001  PROVISIONAL  ADAPTABLE
    BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001  TRUSTED  COMPATIBLE
    BHIV-DS-LINEAGE-CHAIN-001             VERIFIED   NATIVE
    BHIV-DS-TRUST-PROPAGATION-001         PROVISIONAL  ADAPTABLE


KNOWN LIMITS

1. No SSL/TLS. HTTP only in current configuration.
   Production requires nginx reverse proxy with HTTPS termination.

2. No authentication or authorization layer.
   All endpoints are publicly accessible.
   Production requires API key or OAuth integration.

3. Single node only.
   No database replication or API clustering.
   Suitable for current ecosystem scale.

4. No automated database backups.
   Data persists in Docker volume but no scheduled pg_dump.
   Production requires backup scheduling.

5. Port 5432 exposed to host.
   Production should restrict to internal Docker network only.

6. No rate limiting on API endpoints.
   Production requires rate limiting middleware.

7. Dataset Explorer UI pending.
   Assigned to Nikhil, available from 23rd.


Maintained by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
