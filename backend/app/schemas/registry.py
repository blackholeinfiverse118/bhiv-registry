"""
BHIV Registry — Pydantic API Schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
import re

from app.models.registry import (
    TrustLevel, ReplayCompatibility, SimulationCompatibility,
    DatasetStatus, SchemaStatus
)

CANONICAL_ID_PATTERN = re.compile(r"^BHIV-DS-[A-Z0-9\-]{3,80}$")

def validate_canonical_id(v: str) -> str:
    if not CANONICAL_ID_PATTERN.match(v):
        raise ValueError(
            "canonical_id must follow pattern: BHIV-DS-{DOMAIN}-{NAME}-{NUMBER} "
            "e.g. BHIV-DS-MARKET-EQUITY-001"
        )
    return v.upper()


class IngestionReference(BaseModel):
    system: str
    pipeline_id: Optional[str] = None
    frequency: Optional[str] = None
    last_ingested_at: Optional[datetime] = None


class DatasetRegisterRequest(BaseModel):
    canonical_id: str = Field(..., description="e.g. BHIV-DS-MARKET-EQUITY-001")
    dataset_name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    version: str = Field(default="1.0.0")
    source_system: str = Field(..., min_length=2, max_length=255)
    source_location: Optional[str] = None
    owner_name: str = Field(..., min_length=2, max_length=255)
    owner_team: Optional[str] = None
    owner_contact: Optional[str] = None
    domain_primary: str = Field(..., min_length=2, max_length=100)
    domain_tags: List[str] = Field(default_factory=list)
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    replay_compatibility: ReplayCompatibility = ReplayCompatibility.NONE
    replay_notes: Optional[str] = None
    simulation_compatibility: SimulationCompatibility = SimulationCompatibility.INCOMPATIBLE
    simulation_notes: Optional[str] = None
    ingestion_reference: Optional[IngestionReference] = None
    extended_metadata: Optional[Dict[str, Any]] = None

    @field_validator("canonical_id")
    @classmethod
    def check_canonical_id(cls, v):
        return validate_canonical_id(v)


class DatasetUpdateRequest(BaseModel):
    dataset_name: Optional[str] = None
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_team: Optional[str] = None
    owner_contact: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    trust_level: Optional[TrustLevel] = None
    replay_compatibility: Optional[ReplayCompatibility] = None
    replay_notes: Optional[str] = None
    simulation_compatibility: Optional[SimulationCompatibility] = None
    simulation_notes: Optional[str] = None
    ingestion_reference: Optional[IngestionReference] = None
    extended_metadata: Optional[Dict[str, Any]] = None
    status: Optional[DatasetStatus] = None


class DatasetResponse(BaseModel):
    id: UUID
    canonical_id: str
    dataset_name: str
    description: Optional[str]
    version: str
    status: DatasetStatus
    source_system: str
    source_location: Optional[str]
    owner_name: str
    owner_team: Optional[str]
    owner_contact: Optional[str]
    domain_primary: str
    domain_tags: List[str]
    trust_level: TrustLevel
    trust_verified_by: Optional[str]
    trust_verified_at: Optional[datetime]
    replay_compatibility: ReplayCompatibility
    replay_notes: Optional[str]
    simulation_compatibility: SimulationCompatibility
    simulation_notes: Optional[str]
    schema_version: Optional[str]
    ingestion_reference: Optional[Dict[str, Any]]
    extended_metadata: Optional[Dict[str, Any]]
    registered_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[DatasetResponse]


class FieldDefinition(BaseModel):
    field_name: str = Field(..., min_length=1)
    data_type: str
    nullable: bool = True
    description: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    example_value: Optional[Any] = None


class CompatibilityRules(BaseModel):
    backward_compatible: bool = True
    breaking_changes: List[str] = Field(default_factory=list)
    migration_notes: Optional[str] = None


class SchemaCreateRequest(BaseModel):
    dataset_id: UUID
    schema_version: str = Field(..., min_length=1, max_length=50)
    field_definitions: List[FieldDefinition] = Field(..., min_length=1)
    compatibility_rules: Optional[CompatibilityRules] = None
    previous_schema_id: Optional[UUID] = None
    schema_notes: Optional[str] = None
    created_by: str


class SchemaResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    schema_version: str
    status: SchemaStatus
    field_definitions: List[Dict[str, Any]]
    compatibility_rules: Optional[Dict[str, Any]]
    previous_schema_id: Optional[UUID]
    schema_notes: Optional[str]
    created_by: str
    created_at: datetime
    frozen_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ProvenanceCreateRequest(BaseModel):
    event_type: str = Field(..., description="ORIGIN | INGESTION | TRANSFORMATION | VALIDATION | TRUST_CHANGE | SCHEMA_CHANGE")
    source_system: Optional[str] = None
    source_reference: Optional[str] = None
    ingestion_pipeline: Optional[str] = None
    transformation_reference: Optional[Dict[str, Any]] = None
    trust_at_event: Optional[TrustLevel] = None
    recorded_by: str
    notes: Optional[str] = None
    is_replay_safe: bool = False
    replay_context: Optional[Dict[str, Any]] = None

    @field_validator("event_type")
    @classmethod
    def check_event_type(cls, v):
        valid = {"ORIGIN", "INGESTION", "TRANSFORMATION", "VALIDATION", "TRUST_CHANGE", "SCHEMA_CHANGE"}
        if v.upper() not in valid:
            raise ValueError(f"event_type must be one of: {valid}")
        return v.upper()


class ProvenanceResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    event_type: str
    source_system: Optional[str]
    source_reference: Optional[str]
    ingestion_pipeline: Optional[str]
    transformation_reference: Optional[Dict[str, Any]]
    trust_at_event: Optional[TrustLevel]
    recorded_by: str
    recorded_at: datetime
    notes: Optional[str]
    is_replay_safe: bool
    replay_context: Optional[Dict[str, Any]]

    model_config = {"from_attributes": True}


class DatasetSearchFilters(BaseModel):
    domain_primary: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    trust_level: Optional[TrustLevel] = None
    replay_compatibility: Optional[ReplayCompatibility] = None
    simulation_compatibility: Optional[SimulationCompatibility] = None
    owner_team: Optional[str] = None
    status: Optional[DatasetStatus] = DatasetStatus.ACTIVE
    search_text: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TrustUpdateRequest(BaseModel):
    trust_level: TrustLevel
    verified_by: str
    governance_notes: Optional[str] = None


class SuccessResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None