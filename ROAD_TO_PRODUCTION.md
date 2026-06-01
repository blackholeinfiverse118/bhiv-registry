BHIV Master Data Universe Registry
ROAD TO PRODUCTION

Registry ID: BHIV-IDU-REGISTRY-V1
Sprint: MDU Live Infrastructure Activation
Assessment type: Honest gap analysis


PURPOSE

This document provides an honest assessment of what is complete,
what still blocks production-grade infrastructure participation,
and what the path forward looks like.

This is not a marketing document.
It reflects the real state of the registry as of this sprint.


WHAT IS COMPLETE

Infrastructure
  Single command deployment via docker compose up
  Reproducible boot process with automatic migrations
  Health endpoints for monitoring and load balancer integration
  Persistent storage via Docker volumes
  Container restart policy configured

Core Registry Capabilities
  Canonical dataset registration with ID enforcement
  Schema versioning with freeze mechanism
  Append-only provenance chain
  Trust classification workflow with valid transition enforcement
  Dataset relationship mapping
  Formal onboarding flow with review and auto-registration
  Dataset discovery APIs across all metadata dimensions
  Provenance chain validation with TANTRA readiness check
  Registry summary dashboard

Real Ecosystem Participation
  7 real datasets registered from active ecosystem work
  AIS Live Maritime Feed with complete metadata flow demonstrated
  Governance artifacts integrated from Ankita SVACS sprint
  Simulation compatibility classifications from Vijay InsightFlow work
  Schema registered, frozen, and available for schema lookup

Documentation
  DEPLOYMENT_RUNBOOK.md -- complete bootstrap and operations guide
  INFRA_ACTIVATION_REPORT.md -- runtime and integration proof
  ECOSYSTEM_INTEGRATION_REPORT.md -- real artifact participation evidence
  architecture_overview.md -- system design documentation
  metadata_standards.md -- governance standards
  onboarding_flow.md -- submission and review process
  tantra_readiness.md -- TANTRA compatibility validation


WHAT STILL BLOCKS PRODUCTION

Blocker 1 -- No Authentication or Authorization
  Current state: All API endpoints are publicly accessible. No API keys,
  no OAuth, no role-based access control.
  
  Impact: Any system or person can register, modify, or delete datasets.
  Trust classification can be changed by anyone.
  
  Required for production: API key authentication at minimum.
  Recommended: OAuth 2.0 with role-based access (registry-admin,
  dataset-owner, read-only-consumer).

Blocker 2 -- No HTTPS
  Current state: HTTP only. All data including governance metadata
  transmitted in plain text.
  
  Impact: Not acceptable for ecosystem infrastructure carrying
  provenance and trust metadata.
  
  Required for production: nginx reverse proxy with TLS termination.
  Let's Encrypt or organizational certificate.

Blocker 3 -- No Automated Backups
  Current state: Data persists in Docker volume but no scheduled backup.
  A volume deletion or host failure destroys all registry data.
  
  Impact: Registry data is the canonical source of truth for the ecosystem.
  Loss is unrecoverable without backup.
  
  Required for production: Scheduled pg_dump to external storage.
  Minimum: daily backup with 7-day retention.

Blocker 4 -- No Rate Limiting
  Current state: No request throttling on any endpoint.
  
  Impact: Registry vulnerable to accidental or intentional flooding.
  
  Required for production: Rate limiting middleware on all endpoints.


WHAT IS PARTIALLY COMPLETE

Dataset Explorer UI
  Current state: Not started. Assigned to Nikhil, available from 23rd.
  Impact: Builders cannot visually explore the registry without API knowledge.
  Path: Nikhil picks up UI work on 23rd using the discovery API endpoints.

Replay Compatibility Classification
  Current state: All datasets marked NONE for replay compatibility
  except AIS Maritime Feed which is PARTIAL.
  
  Impact: Replay-safe workflow consumers cannot identify eligible datasets.
  
  Path: Vijay and Ankita need to review and classify each dataset
  for replay compatibility in next sprint.

Schema Coverage
  Current state: Only AIS Live Maritime Feed has a registered schema.
  The other 6 datasets have no schema definitions.
  
  Impact: Schema lookup workflows cannot serve consumers for 6 of 7 datasets.
  
  Path: Vijay to submit schemas for the 6 InsightFlow datasets.

Port Exposure
  Current state: Port 5432 is exposed to the host machine.
  Impact: Database directly accessible from outside Docker network.
  Path: Remove port 5432 from docker-compose.yml for production deployment.
  Only the API container needs to reach the database.


PRODUCTION READINESS CHECKLIST

  Infrastructure deployment       COMPLETE
  Database persistence            COMPLETE
  Automatic migrations            COMPLETE
  Core API functionality          COMPLETE
  Real ecosystem participation    COMPLETE
  Documentation                   COMPLETE
  Authentication                  NOT STARTED
  HTTPS / TLS                     NOT STARTED
  Automated backups               NOT STARTED
  Rate limiting                   NOT STARTED
  Dataset Explorer UI             IN PROGRESS (Nikhil)
  Schema coverage all datasets    PARTIAL
  Replay classification           PARTIAL


SUMMARY

The registry is operational and ready for ecosystem development use.
It is not yet hardened for external production exposure.

The four blockers above (auth, HTTPS, backups, rate limiting) are
standard production hardening requirements and are independent of
registry functionality. They can be addressed in a focused
infrastructure hardening sprint without changing any registry logic.

The partial items (UI, replay classification, schema coverage) are
content and feature gaps that can be filled incrementally as ecosystem
participation grows.

The registry is ready to serve as the canonical metadata layer for
BHIV/TANTRA ecosystem builders today.


Maintained by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
