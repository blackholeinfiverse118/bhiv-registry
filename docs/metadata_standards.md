# BHIV Registry — Metadata Standards

## Purpose

This document defines the canonical metadata standards for the BHIV Intelligence Data Universe Registry. All datasets, schemas, and provenance records must conform to these standards.

---

## 1. Dataset Metadata Standards

### Required Fields

| Field | Type | Standard |
|-------|------|----------|
| `canonical_id` | String | Must follow `BHIV-DS-{DOMAIN}-{NAME}-{NUMBER}` |
| `dataset_name` | String | 3-255 characters, descriptive |
| `source_system` | String | Name of origin system |
| `owner_name` | String | Individual or team name |
| `domain_primary` | String | Single primary domain classification |
| `trust_level` | Enum | Must be a valid TrustLevel value |
| `replay_compatibility` | Enum | Must be a valid ReplayCompatibility value |
| `simulation_compatibility` | Enum | Must be a valid SimulationCompatibility value |

### Optional but Recommended Fields

| Field | Purpose |
|-------|---------|
| `description` | Human-readable explanation of the dataset |
| `owner_team` | Team responsible for the dataset |
| `owner_contact` | Contact for dataset queries |
| `domain_tags` | Additional domain classification tags |
| `ingestion_reference` | Pointer to ingestion pipeline |

---

## 2. Trust Level Standards

| Level | Criteria | Use Cases |
|-------|----------|-----------|
| `VERIFIED` | Formally audited, provenance confirmed, lineage complete | Production intelligence workflows |
| `TRUSTED` | Source known, lineage traceable, no anomalies | Standard intelligence workflows |
| `PROVISIONAL` | Source known, lineage partially verified | Development and testing workflows |
| `UNVERIFIED` | Source unknown or unconfirmed | Staging only, not for intelligence use |
| `QUARANTINE` | Flagged for issues | No use — immediate review required |

### Trust Transition Rules

Valid transitions only:

```
UNVERIFIED  → PROVISIONAL, QUARANTINE
PROVISIONAL → TRUSTED, UNVERIFIED, QUARANTINE
TRUSTED     → VERIFIED, PROVISIONAL, QUARANTINE
VERIFIED    → TRUSTED, QUARANTINE
QUARANTINE  → UNVERIFIED (after review only)
```

Governance note is required when transitioning to QUARANTINE or UNVERIFIED.

---

## 3. Replay Compatibility Standards

| Value | Criteria |
|-------|----------|
| `FULL` | Fully deterministic, identical output on every replay |
| `PARTIAL` | Deterministic with known, documented constraints |
| `CONDITIONAL` | Deterministic only when external conditions are met |
| `NONE` | Not replay-safe — live, volatile, or destructively transformed |

---

## 4. Simulation Compatibility Standards

| Value | Criteria |
|-------|----------|
| `NATIVE` | Purpose-built for simulation use cases |
| `COMPATIBLE` | Can be used in simulation without transformation |
| `ADAPTABLE` | Can be used in simulation with known, documented transformation |
| `INCOMPATIBLE` | Not suitable for simulation use |

---

## 5. Schema Metadata Standards

### Field Definition Structure

Every field in a schema must include:

```json
{
  "field_name": "price",
  "data_type": "float",
  "nullable": false,
  "description": "Closing price of the instrument",
  "constraints": {
    "min": 0,
    "precision": 4
  },
  "example_value": 123.4567
}
```

### Supported Data Types

`string`, `integer`, `float`, `boolean`, `datetime`, `date`, `uuid`, `json`, `array`

### Schema Versioning Rules

- Versions follow semantic versioning: `1.0.0`, `1.1.0`, `2.0.0`
- Versions are immutable once frozen
- Breaking changes require a major version increment
- New optional fields are minor version increments
- Bug fixes to descriptions or constraints are patch increments

### Schema Status Lifecycle

```
DRAFT → ACTIVE → FROZEN → RETIRED
```

---

## 6. Provenance Metadata Standards

### Event Types

| Event Type | When to Use |
|-----------|-------------|
| `ORIGIN` | Initial dataset registration — created automatically |
| `INGESTION` | Data ingestion event from source system |
| `TRANSFORMATION` | Data transformation or processing applied |
| `VALIDATION` | Formal validation or audit event |
| `TRUST_CHANGE` | Trust level updated — created automatically |
| `SCHEMA_CHANGE` | Schema version updated |

### Provenance Rules

- Provenance records are **append-only** — never modified
- Every dataset must have at least one ORIGIN record
- Every trust change must have a corresponding TRUST_CHANGE record
- `recorded_by` must always be populated
- `is_replay_safe` must be explicitly set

---

## 7. Canonical ID Standards

### Format

```
BHIV-DS-{DOMAIN}-{NAME}-{NUMBER}
```

### Rules

- All uppercase
- Domain and name segments use hyphens as separators
- Number is zero-padded to 3 digits minimum
- Must be globally unique across the registry
- Once assigned, canonical IDs are permanent and immutable

### Domain Vocabulary

| Domain | Usage |
|--------|-------|
| `MARKET` | Market and financial data |
| `GOVERNANCE` | Governance and audit data |
| `REPLAY` | Replay and reconstruction data |
| `LINEAGE` | Lineage and provenance data |
| `TRUST` | Trust and validation data |
| `RECOVERY` | Recovery and rollback data |
| `SIMULATION` | Simulation and synthetic data |
| `INTELLIGENCE` | Intelligence signal data |

---

*Document maintained by: Nupur — Backend + Data Architecture + Sprint Lead*
*Registry Version: V1 | Ecosystem: TANTRA*
