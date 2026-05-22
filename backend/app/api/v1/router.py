from fastapi import APIRouter
from app.api.v1.endpoints import datasets, schemas, relationships, discovery, onboarding

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(datasets.router)
api_router.include_router(schemas.router)
api_router.include_router(relationships.router)
api_router.include_router(discovery.router)
api_router.include_router(onboarding.router)