"""
BHIV Intelligence Data Universe Registry — Canonical Database Models

These models represent the constitutional metadata architecture for the registry.
They define how datasets, schemas, provenance, and trust are structured and stored.

IMPORTANT: This is a metadata registry — not a data warehouse.
All models here represent information ABOUT data, not the data itself.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Enum,
    ForeignKey, Integer, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class TrustLevel(str, PyEnum):
    VERIFIED    = "VERIFIED"
    TRUSTED     = "TRUSTED"
    PROVISIONAL = "PROVISIONAL"
    UNVERIFIED  = "UNVERIFIED"
    QUARANTINE  = "QUARANTINE"


class ReplayCompatibility(str, PyEnum):
    FULL        = "FULL"
    PARTIAL     = "PARTIAL"
    CONDITIONAL = "CONDITIONAL"
    NONE        = "NONE"


class SimulationCompatibility(str, PyEnum):
    NATIVE       = "NATIVE"
    COMPATIBLE   = "COMPATIBLE"
    ADAPTABLE    = "ADAPTABLE"
    INCOMPATIBLE = "INCOMPATIBLE"


class DatasetStatus(str, PyEnum):
    ACTIVE       = "ACTIVE"
    DEPRECATED   = "DEPRECATED"
    ARCHIVED     = "ARCHIVED"
    UNDER_REVIEW = "UNDER_REVIEW"


class SchemaStatus(str, PyEnum):
    DRAFT   = "DRAFT"
    ACTIVE  = "ACTIVE"
    FROZEN  = "FROZEN"
    RETIRED = "RETIRED"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    canonical_id = Column(String(100), unique=True, nullable=False, index=True)
    dataset_name = Column(String(255), nullable=False)
    description  = Column(Text, nullable=True)
    version      = Column(String(50), nullable=False, default="1.0.0")
    status       = Column(Enum(DatasetStatus), nullable=False, default=DatasetStatus.ACTIVE)

    source_system   = Column(String(255), nullable=False)
    source_location = Column(Text, nullable=True)
    owner_name      = Column(String(255), nullable=False)
    owner_team      = Column(String(255), nullable=True)
    owner_contact   = Column(String(255), nullable=True)

    domain_tags    = Column(ARRAY(String), nullable=False, default=list)
    domain_primary = Column(String(100), nullable=False)

    trust_level       = Column(Enum(TrustLevel), nullable=False, default=TrustLevel.UNVERIFIED)
    trust_verified_by = Column(String(255), nullable=True)
    trust_verified_at = Column(DateTime(timezone=True), nullable=True)
    governance_notes  = Column(Text, nullable=True)

    replay_compatibility     = Column(Enum(ReplayCompatibility), nullable=False, default=ReplayCompatibility.NONE)
    replay_notes             = Column(Text, nullable=True)
    simulation_compatibility = Column(Enum(SimulationCompatibility), nullable=False, default=SimulationCompatibility.INCOMPATIBLE)
    simulation_notes         = Column(Text, nullable=True)

    current_schema_id = Column(UUID(as_uuid=True), ForeignKey("dataset_schemas.id"), nullable=True)
    schema_version    = Column(String(50), nullable=True)

    ingestion_reference = Column(JSONB, nullable=True)
    extended_metadata   = Column(JSONB, nullable=True)

    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    provenance_records = relationship("ProvenanceRecord", back_populates="dataset", cascade="all, delete-orphan")
    schemas            = relationship("DatasetSchema", back_populates="dataset", foreign_keys="DatasetSchema.dataset_id")
    parent_relations   = relationship("DatasetRelationship", foreign_keys="DatasetRelationship.child_dataset_id", back_populates="child_dataset")
    child_relations    = relationship("DatasetRelationship", foreign_keys="DatasetRelationship.parent_dataset_id", back_populates="parent_dataset")

    __table_args__ = (
        Index("ix_datasets_domain_primary", "domain_primary"),
        Index("ix_datasets_trust_level", "trust_level"),
        Index("ix_datasets_status", "status"),
    )

    def __repr__(self):
        return f"<Dataset {self.canonical_id} | {self.dataset_name} | {self.trust_level}>"


class DatasetSchema(Base):
    __tablename__ = "dataset_schemas"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)

    schema_version      = Column(String(50), nullable=False)
    status              = Column(Enum(SchemaStatus), nullable=False, default=SchemaStatus.DRAFT)
    field_definitions   = Column(JSONB, nullable=False)
    compatibility_rules = Column(JSONB, nullable=True)
    previous_schema_id  = Column(UUID(as_uuid=True), ForeignKey("dataset_schemas.id"), nullable=True)
    schema_notes        = Column(Text, nullable=True)
    created_by          = Column(String(255), nullable=False)
    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    frozen_at           = Column(DateTime(timezone=True), nullable=True)

    dataset          = relationship("Dataset", back_populates="schemas", foreign_keys=[dataset_id])
    previous_version = relationship("DatasetSchema", remote_side=[id])

    __table_args__ = (
        UniqueConstraint("dataset_id", "schema_version", name="uq_schema_dataset_version"),
    )

    def __repr__(self):
        return f"<DatasetSchema dataset={self.dataset_id} v={self.schema_version}>"


class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)

    event_type               = Column(String(50), nullable=False)
    source_system            = Column(String(255), nullable=True)
    source_reference         = Column(Text, nullable=True)
    ingestion_pipeline       = Column(String(255), nullable=True)
    transformation_reference = Column(JSONB, nullable=True)
    trust_at_event           = Column(Enum(TrustLevel), nullable=True)
    recorded_by              = Column(String(255), nullable=False)
    recorded_at              = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes                    = Column(Text, nullable=True)
    is_replay_safe           = Column(Boolean, nullable=False, default=False)
    replay_context           = Column(JSONB, nullable=True)

    dataset = relationship("Dataset", back_populates="provenance_records")

    __table_args__ = (
        Index("ix_provenance_dataset_id", "dataset_id"),
        Index("ix_provenance_event_type", "event_type"),
        Index("ix_provenance_recorded_at", "recorded_at"),
    )

    def __repr__(self):
        return f"<ProvenanceRecord dataset={self.dataset_id} event={self.event_type}>"


class DatasetRelationship(Base):
    __tablename__ = "dataset_relationships"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    child_dataset_id  = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)
    description       = Column(Text, nullable=True)
    transformation_notes = Column(Text, nullable=True)
    chain_replay_safe    = Column(Boolean, nullable=False, default=False)
    created_by           = Column(String(255), nullable=False)
    created_at           = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    parent_dataset = relationship("Dataset", foreign_keys=[parent_dataset_id], back_populates="child_relations")
    child_dataset  = relationship("Dataset", foreign_keys=[child_dataset_id], back_populates="parent_relations")

    __table_args__ = (
        UniqueConstraint("parent_dataset_id", "child_dataset_id", "relationship_type", name="uq_dataset_relationship"),
    )

    def __repr__(self):
        return f"<DatasetRelationship {self.parent_dataset_id} → {self.child_dataset_id}>"