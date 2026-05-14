import asyncio
import httpx

datasets = [
    {
        "canonical_id": "BHIV-DS-REPLAY-SEMANTIC-EVENTS-001",
        "dataset_name": "semantic_events",
        "description": "Stores semantic replay events",
        "source_system": "Replay Integrity Service",
        "owner_name": "AI Infra Team",
        "domain_primary": "replay",
        "domain_tags": ["semantic", "replay", "events"],
        "trust_level": "UNVERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "INCOMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-MUTATION-LOGS-001",
        "dataset_name": "mutation_logs",
        "description": "Tracks semantic mutation history",
        "source_system": "Governance Engine",
        "owner_name": "Security Team",
        "domain_primary": "governance",
        "domain_tags": ["mutation", "governance", "logs"],
        "trust_level": "UNVERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "INCOMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-RECOVERY-ROLLBACK-SNAPSHOTS-001",
        "dataset_name": "rollback_snapshots",
        "description": "Stores rollback checkpoints",
        "source_system": "Recovery Service",
        "owner_name": "Backend Team",
        "domain_primary": "recovery",
        "domain_tags": ["rollback", "snapshots", "recovery"],
        "trust_level": "UNVERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "INCOMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-GOVERNANCE-CONTRADICTION-AUDITS-001",
        "dataset_name": "contradiction_audits",
        "description": "Stores contradiction audit traces",
        "source_system": "Contradiction Engine",
        "owner_name": "Enforcement Team",
        "domain_primary": "governance",
        "domain_tags": ["contradiction", "audit", "governance"],
        "trust_level": "UNVERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "INCOMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-LINEAGE-CHAIN-001",
        "dataset_name": "lineage_chain",
        "description": "Maintains semantic lineage continuity",
        "source_system": "Lineage Verification Service",
        "owner_name": "Governance Team",
        "domain_primary": "lineage",
        "domain_tags": ["lineage", "tracking", "semantic"],
        "trust_level": "UNVERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "INCOMPATIBLE"
    },
    {
        "canonical_id": "BHIV-DS-TRUST-PROPAGATION-001",
        "dataset_name": "trust_propagation",
        "description": "Tracks downstream semantic trust propagation",
        "source_system": "Downstream Trust Gateway",
        "owner_name": "Trust Systems Team",
        "domain_primary": "trust",
        "domain_tags": ["trust", "propagation", "enforcement"],
        "trust_level": "UNVERIFIED",
        "replay_compatibility": "NONE",
        "simulation_compatibility": "INCOMPATIBLE"
    }
]

async def register():
    async with httpx.AsyncClient() as client:
        for ds in datasets:
            r = await client.post("http://localhost:8000/api/v1/datasets/", json=ds)
            if r.status_code == 201:
                print(f"REGISTERED: {ds['canonical_id']}")
            else:
                print(f"FAILED: {ds['canonical_id']} — {r.text}")

asyncio.run(register())