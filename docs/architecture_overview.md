# BHIV Intelligence Data Universe Registry — Architecture Overview

## System Identity

**Registry Name:** BHIV Intelligence Data Universe Registry V1
**Registry ID:** BHIV-IDU-REGISTRY-V1
**Ecosystem:** TANTRA
**Classification:** Canonical Federated Dataset Metadata Registry

---

## Architecture Philosophy

The BHIV Registry is built on four non-negotiable principles:

**Metadata-First**
The registry stores information about datasets — not the datasets themselves. Every field, every endpoint, every model exists to describe data, not to store or process it.

**Governance-First**
Every dataset entering the registry goes through a formal onboarding and trust classification process. Nothing enters the registry without provenance.

**Discoverability-First**
The primary value of the registry is making datasets findable. Every design decision prioritizes search, filter, and lookup performance.

**Federated by Design**
The registry does not own the data it describes. It references data that lives in other systems. This federation principle must never be violated.

---

## What the Registry Governs

| Governs | Does NOT Govern |
|---------|----------------|
| Dataset metadata | Actual data storage |
| Schema versioning | Orchestration execution |
| Provenance tracking | Intelligence routing |
| Trust classification | Runtime decisions |
| Replay-safe metadata | Semantic authority |
| Simulation compatibility | Data transformation |
| Dataset discoverability | Centralized memory |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              BHIV Intelligence Data Universe Registry        │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Onboarding API  │  │  Dataset API     │                   │
│  │  Submit/Review   │  │  Register/Search │                   │
│  └────────┬─────────┘  └────────┬────────┘                   │
│           │                     │                            │
│  ┌────────▼─────────────────────▼────────┐                   │
│  │           Service Layer                │                   │
│  │  OnboardingService  DatasetService     │                   │
│  │  SchemaService      TrustService       │                   │
│  │  DiscoveryService   ProvenanceService  │                   │
│  │  RelationshipService                   │                   │
│  └────────────────────┬──────────────────┘                   │
│                       │                                      │
│  ┌────────────────────▼──────────────────┐                   │
│  │           PostgreSQL Database          │                   │
│  │  datasets                              │                   │
│  │  dataset_schemas                       │                   │
│  │  provenance_records                    │                   │
│  │  dataset_relationships                 │                   │
│  │  dataset_onboarding_requests           │                   │
│  └───────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Dataset Registry
The primary entity. Every dataset in the BHIV ecosystem gets a canonical UUID and human-readable canonical ID. Tracks ownership, domain, trust, replay, and simulation metadata.

### 2. Schema Registry
Versioned field definitions for datasets. Schema versions are immutable once frozen — ensuring replay-safe schema resolution across the TANTRA ecosystem.

### 3. Provenance Engine
Append-only chain of events for every dataset. Records ORIGIN, INGESTION, TRANSFORMATION, VALIDATION, TRUST_CHANGE, and SCHEMA_CHANGE events. Never modified — only appended.

### 4. Trust Classification System
Formal governance workflow for classifying dataset trustworthiness. Enforces valid trust transitions and creates audit provenance on every change.

### 5. Discovery Layer
Advanced search and filtering across all metadata dimensions. Includes registry summary dashboard, replay-safe dataset discovery, simulation-ready dataset discovery, and provenance chain validation.

### 6. Dataset Onboarding Flow
Formal submission and review process. Datasets must be submitted, reviewed, and approved before entering the canonical registry.

### 7. Relationship Mapping
Maps parent-child and dependency relationships between datasets. Enables lineage traversal and impact analysis.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| API Framework | FastAPI | 0.115.0 |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy (async) | 2.0.36 |
| Validation | Pydantic | 2.10.0 |
| Migrations | Alembic | 1.14.0 |
| Runtime | Python | 3.13 |

---

## API Surface

| Section | Endpoints | Purpose |
|---------|-----------|---------|
| Datasets | 10 | Registration, retrieval, trust, provenance |
| Schemas | 5 | Schema versioning and governance |
| Relationships | 4 | Dataset lineage mapping |
| Discovery | 8 | Search, filter, validate |
| Onboarding | 5 | Formal submission and review |
| Health | 2 | System health |
| **Total** | **34** | |

---

## Canonical Dataset ID Convention

```
BHIV-DS-{DOMAIN}-{NAME}-{NUMBER}
```

Examples:
- `BHIV-DS-MARKET-EQUITY-001`
- `BHIV-DS-GOVERNANCE-MUTATION-LOGS-001`
- `BHIV-DS-REPLAY-SEMANTIC-EVENTS-001`

---

## TANTRA Integration Readiness

The registry exposes the following capabilities for future TANTRA system consumption:

- Dataset discovery by any metadata dimension
- Provenance chain validation and TANTRA readiness check
- Trust lookup for governance-safe dataset selection
- Replay-safe dataset identification
- Simulation-compatible dataset identification
- Schema version resolution for deterministic replay

---

*Document maintained by: Nupur — Backend + Data Architecture + Sprint Lead*
*Registry Version: V1 | Ecosystem: TANTRA*
