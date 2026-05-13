# BHIV Intelligence Data Universe Registry — V1
## Sprint Review Packet | Day 1

---

## 1. Project Overview

The **BHIV Intelligence Data Universe Registry** is the canonical federated dataset metadata layer for the TANTRA ecosystem.

It is a **metadata registry** — not a data warehouse, not an orchestration layer, not an intelligence engine.

Its purpose is to answer:
- What datasets exist in the BHIV ecosystem?
- Where did they come from and how were they transformed?
- Can this dataset be trusted for a given use case?
- Can this dataset be replayed deterministically?
- Is this dataset simulation-compatible?

---

## 2. What We Are Building vs What We Are Not

| We ARE Building | We Are NOT Building |
|----------------|-------------------|
| Federated dataset registry | Data warehouse |
| Metadata governance infrastructure | Orchestration layer |
| Discoverability layer | AI / intelligence engine |
| Provenance tracking system | Massive ingestion infrastructure |
| Trust classification system | Centralized data storage |
| Replay-safe metadata foundations | Runtime routing |
| Simulation compatibility metadata | Semantic authority |

---

## 3. Team Structure

| Name | Role |
|------|------|
| Nupur | Backend + Data Architecture + Sprint Lead |
| Soham | Fullstack + Dataset Explorer UI |
| Ankita | Schema Governance + Trust Metadata + Validation Standards |
| Vijay | Integration Mapping + Dataset Onboarding + Ecosystem Convergence |

---

## 4. Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI 0.115.0 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0.36 (async) |
| Validation | Pydantic 2.10.0 |
| Migrations | Alembic 1.14.0 |
| Runtime | Python 3.13 |
| Containerization | Docker Desktop |

---

## 5. Repository Structure

```
bhiv-registry/
│
├── docker-compose.yml               # Docker setup for API + PostgreSQL
├── README.md                        # Project overview and quick start
├── .gitignore                       # Git ignore rules
│
└── backend/
    ├── Dockerfile                   # Docker image for FastAPI
    ├── requirements.txt             # All Python dependencies
    ├── .env                         # Environment variables (not committed)
    │
    └── app/
        ├── main.py                  # FastAPI app entry point + lifespan
        │
        ├── core/
        │   └── config.py            # App settings and environment config
        │
        ├── db/
        │   └── base.py              # Database engine, session, init_db
        │
        ├── models/
        │   └── registry.py          # SQLAlchemy database models (canonical metadata architecture)
        │
        ├── schemas/
        │   └── registry.py          # Pydantic request/response schemas (API contracts)
        │
        ├── services/
        │   └── dataset_service.py   # Business logic layer
        │
        ├── api/
        │   └── v1/
        │       ├── router.py        # API router — assembles all endpoints
        │       └── endpoints/
        │           └── datasets.py  # Dataset API endpoints
        │
        └── tests/                   # Test directory (Day 2 onwards)
```

---

## 6. Canonical Metadata Architecture

### 6.1 Core Database Models

#### Dataset
The primary registry entity. Every dataset registered in the BHIV ecosystem gets a canonical UUID and a human-readable canonical ID.

Key fields:
- `canonical_id` — e.g. `BHIV-DS-MARKET-EQUITY-001`
- `dataset_name`, `description`, `version`, `status`
- `source_system`, `source_location`, `owner_name`, `owner_team`
- `domain_primary`, `domain_tags`
- `trust_level` — VERIFIED / TRUSTED / PROVISIONAL / UNVERIFIED / QUARANTINE
- `replay_compatibility` — FULL / PARTIAL / CONDITIONAL / NONE
- `simulation_compatibility` — NATIVE / COMPATIBLE / ADAPTABLE / INCOMPATIBLE
- `ingestion_reference` — pointer to pipeline, not the pipeline itself
- `registered_at`, `updated_at`

#### DatasetSchema
Versioned field definitions for a dataset. Immutable once frozen.

Key fields:
- `schema_version`, `status` — DRAFT / ACTIVE / FROZEN / RETIRED
- `field_definitions` — JSONB array of field objects
- `compatibility_rules` — backward compatibility metadata
- `previous_schema_id` — links to prior version for lineage

#### ProvenanceRecord
Append-only chain of events for every dataset. Never modified, only added to.

Event types:
- `ORIGIN` — initial registration
- `INGESTION` — data ingestion event
- `TRANSFORMATION` — data transformation applied
- `VALIDATION` — validation event
- `TRUST_CHANGE` — trust level updated
- `SCHEMA_CHANGE` — schema version updated

#### DatasetRelationship
Maps parent-child and dependency relationships between datasets.

Relationship types:
- `DERIVED_FROM`
- `DEPENDS_ON`
- `MERGED_FROM`
- `FILTERED_FROM`

---

### 6.2 Trust Classification

| Level | Meaning |
|-------|---------|
| `VERIFIED` | Formally audited, provenance confirmed |
| `TRUSTED` | Source known, lineage traceable |
| `PROVISIONAL` | Source known, lineage partially verified |
| `UNVERIFIED` | Source unknown or unconfirmed |
| `QUARANTINE` | Flagged — not safe for intelligence use |

---

### 6.3 Replay Compatibility

| Value | Meaning |
|-------|---------|
| `FULL` | Fully deterministic, safe for all replay |
| `PARTIAL` | Replay with known constraints |
| `CONDITIONAL` | Replay if external conditions met |
| `NONE` | Not replay-safe — live or volatile data |

---

### 6.4 Canonical ID Convention

All datasets must follow this format:

```
BHIV-DS-{DOMAIN}-{NAME}-{NUMBER}
```

Examples:
- `BHIV-DS-MARKET-EQUITY-001`
- `BHIV-DS-MACRO-RATES-001`
- `BHIV-DS-SIMULATION-SYNTHETIC-001`

---

## 7. API Endpoints — Live at localhost:8000/docs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/datasets/` | Register a new dataset |
| `GET` | `/api/v1/datasets/` | Search and filter datasets |
| `GET` | `/api/v1/datasets/canonical/{canonical_id}` | Get dataset by canonical ID |
| `GET` | `/api/v1/datasets/{dataset_id}` | Get dataset by UUID |
| `PATCH` | `/api/v1/datasets/{dataset_id}` | Update dataset metadata |
| `POST` | `/api/v1/datasets/{dataset_id}/trust` | Update trust classification |
| `GET` | `/api/v1/datasets/{dataset_id}/provenance` | Get full provenance chain |
| `POST` | `/api/v1/datasets/{dataset_id}/provenance` | Add provenance event |
| `GET` | `/` | Registry health + identity |
| `GET` | `/health` | Health check |

---

## 8. Day 1 Work Completed

### Environment
- Docker Desktop installed and configured
- Python 3.13 virtual environment created
- All backend dependencies installed
- Resolved Python 3.13 package compatibility issue — upgraded to compatible versions
- PostgreSQL database created — `bhiv_registry`

### Backend
- Full repository structure initialized
- Canonical metadata architecture designed and locked
- 9 core backend files written:
  - `config.py` — app settings
  - `base.py` — database engine and session
  - `registry.py` (models) — all 4 SQLAlchemy database models
  - `registry.py` (schemas) — all Pydantic API contracts
  - `dataset_service.py` — full business logic layer
  - `datasets.py` (endpoints) — all 8 API endpoints
  - `router.py` — API router
  - `main.py` — FastAPI application entry point

### Database
- All 4 core tables created successfully:
  - `datasets`
  - `dataset_schemas`
  - `provenance_records`
  - `dataset_relationships`
- Resolved database permissions issue — schema access granted to `bhiv` user
- Resolved duplicate index conflict — database cleaned and rebuilt cleanly

### API
- FastAPI backend running live
- All 8 endpoints operational
- Interactive API documentation live at `localhost:8000/docs`
- Auto-provenance on registration — every new dataset automatically gets an ORIGIN provenance record

---

## 9. Architecture Boundaries — Non Negotiable

The registry must NEVER drift into:
- Orchestration infrastructure
- Intelligence execution
- Runtime routing
- Centralized mega-storage
- Semantic authority

The registry governs:
- Data structure
- Provenance
- Trust
- Discoverability

NOT intelligence meaning.

---

## 10. Remaining Sprint Plan

| Day | Focus |
|-----|-------|
| Day 2 | GitHub onboarding, Schema API, Relationship API, Alembic migrations, Seed data |
| Day 3 | Discovery API refinement, Trust workflow, Provenance validation, UI foundation |
| Day 4 | Integration mapping, Onboarding flow, UI alignment, Backend stabilization |
| Day 5 | TANTRA readiness validation, Architecture audit, Full documentation, Sprint demo |

---

*Prepared by: Nupur — Backend + Data Architecture + Sprint Lead*
*Sprint: BHIV Intelligence Data Universe Registry V1 — TANTRA Convergence Sprint*
