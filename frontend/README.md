# BHIV Registry — Dataset Explorer & Metadata Interaction Surface

A high-fidelity, premium dark-glassmorphism operator interface designed for the TANTRA Ecosystem Dataset Metadata Registry.

---

## What This UI Does

1. **Dashboard & Summary**: Visualizes dataset counts, trust distributions, and runs a global provenance chain audit report.
2. **Dataset Catalog**: Interactive card grid supporting dynamic search, tags, and sidebar filtering. Sliding detail drawer displays metadata, ownership, and event histories.
3. **Schema Hub**: Lists dataset versions, active/frozen states, and field definitions. Operators can create schema drafts and formally freeze/activate versions.
4. **Lineage Explorer**: Automatically maps parent-child dependencies using smooth interactive nodes and Bezier arrow curves.
5. **Onboarding Portal**: Submission portal for new dataset metadata registration and an administrative queue to review, approve, or reject pending requests.

---

## Quick Start Guide

### 1. Start the FastAPI Backend
Ensure your database is created and migrations are up-to-date, then run uvicorn:
```powershell
cd backend
$env:PYTHONPATH = "."
..\venv\Scripts\uvicorn app.main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

### 2. Start the Frontend Web Server
Use Python's zero-dependency static HTTP server inside this directory:
```powershell
cd frontend
python -m http.server 3000
```

### 3. Open the Explorer
Point your browser to:
```
http://localhost:3000
```
The client will automatically link to the FastAPI backend running on port 8000!
