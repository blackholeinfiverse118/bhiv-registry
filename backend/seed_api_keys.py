"""
BHIV Registry — API Key Seeding Script

Generates API keys for ecosystem consumers.
Run once after migrations to populate api_keys table.
"""

import asyncio
import secrets
from app.db.base import AsyncSessionLocal
from app.models.registry import ApiKey
from sqlalchemy import select


CONSUMERS = [
    {"owner_name": "Nupur-Internal", "description": "Internal sprint lead access"},
    {"owner_name": "Vijay-InsightFlow", "description": "InsightFlow ecosystem consumer"},
    {"owner_name": "Ankita-SVACS-NICAI", "description": "SVACS and NICAI ecosystem consumer"},
    {"owner_name": "Nikhil-Explorer", "description": "Dataset Explorer UI consumer"},
]


async def seed_keys():
    async with AsyncSessionLocal() as db:
        print("=== SEEDING API KEYS ===")
        print()

        for consumer in CONSUMERS:
            existing = await db.execute(
                select(ApiKey).where(ApiKey.owner_name == consumer["owner_name"])
            )
            if existing.scalar_one_or_none():
                print(f"EXISTS: {consumer['owner_name']}")
                continue

            key_value = f"{consumer['owner_name'].lower().replace('-', '_')}_{secrets.token_hex(16)}"

            api_key = ApiKey(
                key=key_value,
                owner_name=consumer["owner_name"],
                description=consumer["description"],
                is_active=True,
            )
            db.add(api_key)
            print(f"CREATED: {consumer['owner_name']}")
            print(f"  KEY: {key_value}")

        await db.commit()
        print()
        print("=== DONE ===")
        print("Save these keys securely. They will not be shown again by this script.")


asyncio.run(seed_keys())