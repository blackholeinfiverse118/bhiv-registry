# BHIV Intelligence Data Universe Registry — V1

Canonical federated dataset metadata registry for the TANTRA ecosystem.

---

## What This Is

The BHIV Intelligence Data Universe Registry is a metadata registry — not a data warehouse, not an orchestration layer, not an intelligence engine.

It tracks information **about** datasets — not the datasets themselves.

Think of it like a library index. It tells you what datasets exist, where they came from, who owns them, whether they can be trusted, and whether they can be replayed deterministically.

---

## What This Registry Governs

- Dataset registration and discoverability
- Schema versioning and governance
- Provenance tracking and lineage
- Trust classification
- Replay-safe metadata
- Simulation compatibility metadata

## What This Registry Does NOT Do

- Store actual data
- Execute orchestration
- Route intelligence workflows
- Serve as centralized memory
- Make intelligence decisions

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI 0.115.0 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0.36 (async) |
| Validation | Pydantic 2.10.0 |
| Migrations | Alembic 1.14.0 |
| Runtime | Python 3.13 |

---

## Quick Start

### Prerequisites
- Python 3.11 or higher
- PostgreSQL installed and running
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourname/bhiv-registry.git
cd bhiv-registry
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file inside the `backend` folder:
```
DATABASE_URL=postgresql+asyncpg://bhiv:bhiv_secret@localhost:5432/bhiv_registry
APP_ENV=development
DEBUG=true
REGISTRY_ID=BHIV-IDU-REGISTRY-V1
TANTRA_ECOSYSTEM_VERSION=V1
```

### 5. Set up PostgreSQL database
Open pgAdmin or psql and run:
```sql
CREATE USER bhiv WITH PASSWORD 'bhiv_secret';
CREATE DATABASE bhiv_registry OWNER bhiv;
GRANT ALL PRIVILEGES ON DATABASE bhiv_registry TO bhiv;
GRANT ALL ON SCHEMA public TO bhiv;
```

### 6. Run the API
```bash
cd backend
# Windows
$env:PYTHONPATH = "."

# Mac / Linux
export PYTHONPATH=.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Open API docs
```
http://localhost:8000/docs
```

---

## Repository Structure

```
bhiv-registry/
│
├── docker-compose.yml
├── README.md
├── review_packet.md
├── .gitignore
│
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    ├── .env                        ← create this locally, not committed
    │
    └── app/
        ├── main.py
        ├── core/
        │   └── config.py
        ├── db/
        │   └── base.py
        ├── models/
        │   └── registry.py
        ├── schemas/
        │   └── registry.py
        ├── services/
        │   └── dataset_service.py
        ├── api/
        │   └── v1/
        │       ├── router.py
        │       └── endpoints/
        │           └── datasets.py
        └── tests/
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/datasets/` | Register a new dataset |
| `GET` | `/api/v1/datasets/` | Search and filter datasets |
| `GET` | `/api/v1/datasets/canonical/{canonical_id}` | Get dataset by canonical ID |
| `GET` | `/api/v1/datasets/{dataset_id}` | Get dataset by UUID |
| `PATCH` | `/api/v1/datasets/{dataset_id}` | Update dataset metadata |
| `POST` | `/api/v1/datasets/{dataset_id}/trust` | Update trust classification |
| `GET` | `/api/v1/datasets/{dataset_id}/provenance` | Get provenance chain |
| `POST` | `/api/v1/datasets/{dataset_id}/provenance` | Add provenance event |
| `GET` | `/health` | Health check |

---

## Canonical Dataset ID Format

All datasets must follow this naming convention:

```
BHIV-DS-{DOMAIN}-{NAME}-{NUMBER}
```

Examples:
- `BHIV-DS-MARKET-EQUITY-001`
- `BHIV-DS-MACRO-RATES-001`
- `BHIV-DS-SIMULATION-SYNTHETIC-001`

---

## Branch Rules

- Do not push directly to `main`
- Create your own branch for your work
- Raise a pull request — sprint lead will review and merge

---

## Team

| Name | Role |
|------|------|
| Nupur | Backend + Data Architecture + Sprint Lead |
| Soham | Fullstack + Dataset Explorer UI |
| Ankita | Schema Governance + Trust Metadata |
| Vijay | Integration Mapping + Dataset Onboarding |

---

## For detailed architecture and Day 1 sprint review

See `review_packet.md`
