# BHIV Registry — Dataset Registration and Onboarding Flow

## Overview

There are two ways to register a dataset in the BHIV registry:

1. **Direct Registration** — for sprint leads and registry administrators
2. **Formal Onboarding Flow** — for all team members and external systems

The formal onboarding flow is the standard process for all new datasets going forward.

---

## Path 1 — Direct Registration (Admin Only)

Used by sprint leads and registry administrators for bulk registration or urgent cases.

### Endpoint
```
POST /api/v1/datasets/
```

### Required Fields
```json
{
  "canonical_id": "BHIV-DS-DOMAIN-NAME-001",
  "dataset_name": "Dataset Name",
  "source_system": "Source System Name",
  "owner_name": "Owner Name",
  "domain_primary": "domain",
  "domain_tags": ["tag1", "tag2"],
  "trust_level": "UNVERIFIED",
  "replay_compatibility": "NONE",
  "simulation_compatibility": "INCOMPATIBLE"
}
```

### Rules
- Canonical ID must follow the `BHIV-DS-{DOMAIN}-{NAME}-{NUMBER}` format
- An ORIGIN provenance record is created automatically
- Dataset starts at UNVERIFIED trust by default
- Trust must be updated separately after governance review

---

## Path 2 — Formal Onboarding Flow (Standard Process)

This is the required process for all new dataset submissions.

### Step 1 — Submit Onboarding Request

The dataset owner submits a request for review.

**Endpoint:**
```
POST /api/v1/onboarding/submit
```

**Payload:**
```json
{
  "proposed_canonical_id": "BHIV-DS-DOMAIN-NAME-001",
  "dataset_name": "Dataset Name",
  "description": "What this dataset contains",
  "source_system": "Source System Name",
  "owner_name": "Owner Name",
  "owner_team": "Team Name",
  "domain_primary": "domain",
  "domain_tags": ["tag1", "tag2"],
  "proposed_trust_level": "UNVERIFIED",
  "proposed_replay_compatibility": "NONE",
  "proposed_simulation_compatibility": "INCOMPATIBLE",
  "submitted_by": "submitter_name",
  "submission_notes": "Any relevant context"
}
```

**Result:** Request created with status `PENDING_REVIEW`

---

### Step 2 — Governance Review

The sprint lead or governance team reviews the request.

**Check the pending queue:**
```
GET /api/v1/onboarding/pending
```

**Review a specific request:**
```
POST /api/v1/onboarding/{request_id}/review
```

**Approve payload:**
```json
{
  "decision": "APPROVED",
  "reviewed_by": "reviewer_name",
  "review_notes": "Dataset meets governance standards"
}
```

**Reject payload:**
```json
{
  "decision": "REJECTED",
  "reviewed_by": "reviewer_name",
  "review_notes": "Reason for rejection"
}
```

---

### Step 3 — Auto Registration (on Approval)

When a request is APPROVED:
- Dataset is automatically registered in the canonical registry
- An ORIGIN provenance record is created with full audit trail
- Request status updates to `REGISTERED`
- `registered_dataset_id` is populated with the new dataset UUID

No manual registration step is needed.

---

### Step 4 — Trust Classification (Post Registration)

After registration the dataset starts at `UNVERIFIED` by default.
Governance team (Ankita) reviews and applies trust classification:

```
POST /api/v1/datasets/{dataset_id}/trust/transition
```

```json
{
  "trust_level": "TRUSTED",
  "verified_by": "governance_reviewer",
  "governance_notes": "Reason for trust classification"
}
```

---

## Onboarding Flow Diagram

```
Dataset Owner
     │
     ▼
POST /onboarding/submit
     │
     ▼
Status: PENDING_REVIEW
     │
     ▼
Governance Review
     │
     ├── APPROVED ──────────────────────────────┐
     │                                          │
     ▼                                          ▼
Status: REJECTED                    Auto-register in Dataset Registry
                                               │
                                               ▼
                                    Status: REGISTERED
                                               │
                                               ▼
                                    Trust Classification by Governance
                                               │
                                               ▼
                                    Dataset Active in Registry
```

---

## Checking Onboarding Status

| Action | Endpoint |
|--------|---------|
| View all pending requests | `GET /api/v1/onboarding/pending` |
| View all requests | `GET /api/v1/onboarding/all` |
| View specific request | `GET /api/v1/onboarding/{request_id}` |

---

## Post Registration — Schema Submission

After a dataset is registered, submit its schema:

```
POST /api/v1/schemas/
```

```json
{
  "dataset_id": "uuid-of-registered-dataset",
  "schema_version": "1.0.0",
  "field_definitions": [
    {
      "field_name": "field_name",
      "data_type": "string",
      "nullable": false,
      "description": "Field description"
    }
  ],
  "created_by": "schema_author"
}
```

Once reviewed, freeze the schema:
```
POST /api/v1/schemas/{schema_id}/freeze
```

Frozen schemas are immutable and safe for replay workflows.

---

*Document maintained by: Nupur — Backend + Data Architecture + Sprint Lead*
*Registry Version: V1 | Ecosystem: TANTRA*
