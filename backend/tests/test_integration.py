import pytest
from httpx import AsyncClient
import uuid

BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_dataset_lifecycle():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # Create a unique canonical ID to avoid conflicts
        unique_num = str(uuid.uuid4().int)[:6]
        canonical_id = f"BHIV-DS-MARKET-STOCKS-{unique_num}"
        
        # 1. Register a new dataset
        payload = {
            "canonical_id": canonical_id,
            "dataset_name": f"Stocks Data {unique_num}",
            "description": "Integration test dataset representing market stocks",
            "source_system": "Test Automation Suite",
            "owner_name": "QA Team",
            "owner_team": "Core Integration",
            "domain_primary": "market",
            "domain_tags": ["stocks", "equities", "prices"],
            "trust_level": "UNVERIFIED",
            "replay_compatibility": "NONE",
            "simulation_compatibility": "INCOMPATIBLE"
        }
        
        res = await ac.post(f"{BASE_URL}/datasets/", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["canonical_id"] == canonical_id
        dataset_id = data["id"]
        
        # 2. Get dataset by ID
        res = await ac.get(f"{BASE_URL}/datasets/{dataset_id}")
        assert res.status_code == 200
        assert res.json()["dataset_name"] == f"Stocks Data {unique_num}"
        
        # 3. Create a Schema Draft
        schema_payload = {
            "dataset_id": dataset_id,
            "schema_version": "1.0.0",
            "field_definitions": [
                {
                    "field_name": "ticker",
                    "data_type": "string",
                    "nullable": False,
                    "description": "Stock trading ticker symbol"
                },
                {
                    "field_name": "price",
                    "data_type": "float",
                    "nullable": False,
                    "description": "Stock close price"
                }
            ],
            "schema_notes": "First version draft schema",
            "created_by": "Test Suite"
        }
        
        res = await ac.post(f"{BASE_URL}/schemas/", json=schema_payload)
        assert res.status_code == 201
        schema_data = res.json()
        assert schema_data["status"] == "DRAFT"
        schema_id = schema_data["id"]
        
        # 4. Activate Schema Draft
        res = await ac.patch(f"{BASE_URL}/schemas/{schema_id}/activate")
        assert res.status_code == 200
        assert res.json()["status"] == "ACTIVE"
        
        # 5. Freeze Schema Version
        res = await ac.post(f"{BASE_URL}/schemas/{schema_id}/freeze")
        assert res.status_code == 200
        assert res.json()["status"] == "FROZEN"
        
        # 6. Try to activate frozen schema (should fail cleanly with 422)
        res = await ac.patch(f"{BASE_URL}/schemas/{schema_id}/activate")
        assert res.status_code == 422
        
        # 7. Check Trust Level Transition Constraints
        # UNVERIFIED -> VERIFIED is invalid!
        invalid_trust = {
            "trust_level": "VERIFIED",
            "verified_by": "Test Auditor",
            "governance_notes": "Attempting invalid direct transition"
        }
        res = await ac.post(f"{BASE_URL}/datasets/{dataset_id}/trust/transition", json=invalid_trust)
        assert res.status_code == 422
        assert "Invalid trust transition" in res.json()["detail"]
        
        # UNVERIFIED -> PROVISIONAL is valid!
        valid_trust = {
            "trust_level": "PROVISIONAL",
            "verified_by": "Test Auditor",
            "governance_notes": "Moving to provisional status"
        }
        res = await ac.post(f"{BASE_URL}/datasets/{dataset_id}/trust/transition", json=valid_trust)
        assert res.status_code == 200
        assert res.json()["trust_level"] == "PROVISIONAL"
        
        # 8. Provenance Validation Audit
        res = await ac.get(f"{BASE_URL}/discovery/provenance/validate/{dataset_id}")
        assert res.status_code == 200
        audit_data = res.json()
        assert audit_data["valid"] is True
        # Compatibility fields assertion
        assert audit_data["is_valid"] is True
        assert audit_data["event_count"] >= 2  # ORIGIN + TRUST_CHANGE

@pytest.mark.anyio
async def test_onboarding_workflow():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        unique_num = str(uuid.uuid4().int)[:6]
        proposed_id = f"BHIV-DS-INTEGRATE-ONBOARD-{unique_num}"
        
        # 1. Submit Onboarding Request
        payload = {
            "proposed_canonical_id": proposed_id,
            "dataset_name": f"Onboarded Dataset {unique_num}",
            "description": "Dataset submitted through formal onboarding",
            "source_system": "Integration Portal",
            "owner_name": "Vijay",
            "owner_team": "Dataset Onboarding",
            "domain_primary": "trust",
            "domain_tags": ["onboard", "verify"],
            "proposed_trust_level": "UNVERIFIED",
            "proposed_replay_compatibility": "NONE",
            "proposed_simulation_compatibility": "INCOMPATIBLE",
            "submitted_by": "Soham",
            "submission_notes": "Please onboard this system"
        }
        
        res = await ac.post(f"{BASE_URL}/onboarding/submit", json=payload)
        assert res.status_code == 201
        onboard_data = res.json()
        assert onboard_data["status"] == "PENDING_REVIEW"
        request_id = onboard_data["id"]
        
        # 2. Review Request: APPROVED (Must map decision)
        review_payload = {
            "decision": "APPROVED",
            "reviewed_by": "Sprint Lead Nupur",
            "review_notes": "Meets constitutional standards"
        }
        res = await ac.post(f"{BASE_URL}/onboarding/{request_id}/review", json=review_payload)
        assert res.status_code == 200
        reviewed_data = res.json()
        assert reviewed_data["status"] == "REGISTERED"
        assert reviewed_data["registered_dataset_id"] is not None
        
        # 3. Retrieve registered dataset and confirm it exists
        registered_id = reviewed_data["registered_dataset_id"]
        res = await ac.get(f"{BASE_URL}/datasets/{registered_id}")
        assert res.status_code == 200
        assert res.json()["canonical_id"] == proposed_id
