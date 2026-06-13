"""
Backfill dataset.schema_version and current_schema_id
for datasets whose schema was frozen before the fix
that links frozen schemas back to the parent dataset.
"""

import asyncio
from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from app.models.registry import Dataset, DatasetSchema, SchemaStatus


async def backfill():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Dataset))
        datasets = result.scalars().all()

        updated = 0
        for dataset in datasets:
            if dataset.schema_version:
                continue

            sr = await db.execute(
                select(DatasetSchema)
                .where(
                    DatasetSchema.dataset_id == dataset.id,
                    DatasetSchema.status == SchemaStatus.FROZEN
                )
                .order_by(DatasetSchema.created_at.desc())
            )
            schema = sr.scalars().first()

            if schema:
                dataset.current_schema_id = schema.id
                dataset.schema_version = schema.schema_version
                updated += 1
                print(f"UPDATED: {dataset.canonical_id} -> schema_version {schema.schema_version}")

        await db.commit()
        print()
        print(f"Backfill complete. {updated} datasets updated.")


asyncio.run(backfill())