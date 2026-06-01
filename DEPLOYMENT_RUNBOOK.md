BHIV Master Data Universe Registry
DEPLOYMENT RUNBOOK V1

Registry ID: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
Status: Active Infrastructure


OVERVIEW

This runbook covers the complete deployment lifecycle of the BHIV MDU Registry.
The registry runs as a two-container Docker Compose stack:
- bhiv_mdu_db: PostgreSQL 16 database
- bhiv_mdu_api: FastAPI application with automatic Alembic migrations

Single command bring-up is the primary deployment method.


PREREQUISITES

The following must be installed on the host machine before deployment:

- Docker Desktop (Windows/Mac) or Docker Engine (Linux) version 24 or higher
- Docker Compose version 2 or higher
- Git
- 2GB RAM minimum available to Docker
- Port 8000 free (API)
- Port 5432 free (PostgreSQL) -- only if running local Postgres simultaneously


BOOTSTRAP -- FIRST TIME SETUP

Step 1: Clone the repository
  git clone https://github.com/blackholeinfiverse37/bhiv-registry.git
  cd bhiv-registry

Step 2: Create environment file
  Copy .env.example to backend/.env
  cp .env.example backend/.env
  No changes needed for local development. The defaults work out of the box.

Step 3: Start the full stack
  docker compose up --build
  
  This command:
  - Pulls PostgreSQL 16 Alpine image
  - Builds the FastAPI application image
  - Starts the database container
  - Waits for database health check to pass
  - Runs all Alembic migrations automatically
  - Starts the API server on port 8000

Step 4: Verify deployment
  Open browser: http://localhost:8000/health
  Expected response: {"status":"healthy","version":"1.0.0"}
  
  Open API docs: http://localhost:8000/docs
  Expected: Full interactive API documentation with all 34 endpoints


STANDARD STARTUP

After first-time setup, use this command for subsequent starts:

  docker compose up

This reuses the existing built image and existing database volume.
Migrations run automatically on every startup -- safe to run repeatedly.

To run in background (detached mode):
  docker compose up -d

To view logs when running in detached mode:
  docker compose logs -f


SHUTDOWN

Graceful shutdown -- preserves all data:
  docker compose down

This stops and removes containers but preserves the postgres_data volume.
All registered datasets, schemas, provenance records remain intact.


FULL RESET -- DESTROYS ALL DATA

Only use this when you need a completely clean slate:
  docker compose down -v

The -v flag removes the postgres_data volume. All data is permanently deleted.
After this, run docker compose up --build to start fresh.


MIGRATION MANAGEMENT

Migrations run automatically on startup. For manual migration operations:

Enter the API container:
  docker compose exec api bash

Inside the container, run migrations manually:
  alembic upgrade head

Check current migration version:
  alembic current

View migration history:
  alembic history

Create a new migration after model changes:
  alembic revision --autogenerate -m "description_of_change"


ENVIRONMENT CONFIGURATION

The following environment variables control registry behavior:

DATABASE_URL
  Connection string for PostgreSQL.
  Default: postgresql+asyncpg://bhiv:bhiv_secret@db:5432/bhiv_registry
  In Docker: uses container name 'db' as host
  Local development: uses localhost

APP_ENV
  Application environment. Values: development, production
  Default: development

DEBUG
  Enable SQLAlchemy query logging. Values: true, false
  Default: false in production, true in development

REGISTRY_ID
  Canonical registry identifier.
  Default: BHIV-IDU-REGISTRY-V1

TANTRA_ECOSYSTEM_VERSION
  TANTRA ecosystem version this registry supports.
  Default: V1


HEALTH ENDPOINTS

GET /health
  Returns: {"status":"healthy","version":"1.0.0"}
  Use for: load balancer health checks, monitoring, deployment verification

GET /
  Returns: registry identity, version, status, docs URL
  Use for: ecosystem discovery, registry identification


RUNTIME TOPOLOGY

  Host Machine
  |
  |-- Docker Network: bhiv-registry_default
      |
      |-- bhiv_mdu_db (postgres:16-alpine)
      |   Port: 5432 (mapped to host 5432)
      |   Volume: postgres_data (persistent)
      |
      |-- bhiv_mdu_api (bhiv-registry-api)
          Port: 8000 (mapped to host 8000)
          Depends on: bhiv_mdu_db healthy
          Runs: alembic upgrade head on start
          Runs: uvicorn app.main:app


RECOVERY

API container crash:
  Docker restart policy is set to 'unless-stopped'.
  Container restarts automatically. Migrations are idempotent -- safe to re-run.

Database container crash:
  Docker restart policy is set to 'unless-stopped'.
  Container restarts automatically. Data persists in postgres_data volume.

Full host restart:
  Run: docker compose up -d
  Both containers restart and registry is operational.

Corrupted database:
  Run: docker compose down -v
  Run: docker compose up --build
  Note: All data is lost. Re-seed using seed_data.py if needed.


KNOWN LIMITATIONS

1. Single node deployment only. No clustering or replication in V1.
2. No SSL/TLS termination in current configuration. Add a reverse proxy (nginx) for production HTTPS.
3. Database credentials are in plain text in docker-compose.yml. Use Docker secrets or environment injection for production hardening.
4. No automated backup configured. Implement pg_dump scheduling for production.
5. Port 5432 exposed to host. Restrict in production to internal network only.


TEAM ONBOARDING

For a new team member to run the registry locally:

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Clone the repo: git clone https://github.com/blackholeinfiverse37/bhiv-registry.git
3. Run: cd bhiv-registry && docker compose up --build
4. Open: http://localhost:8000/docs

That is the complete setup. No Python, no PostgreSQL, no manual configuration required.


Maintained by: Nupur -- Backend + Data Architecture + Sprint Lead
Registry: BHIV-IDU-REGISTRY-V1
Ecosystem: TANTRA
