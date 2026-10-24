"""Database models.

SQLite-compatible version - schemas removed for SQLite support.
For PostgreSQL, schemas would be: auth, medical, public
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, Enum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON  # Use JSON instead of JSONB for SQLite compatibility
from sqlalchemy.orm import relationship

from app.database import Base


# -- Enumerations --

class SexAssignedAtBirth(str, PyEnum):
    male = "male"
    female = "female"
    intersex = "intersex"
    prefer_not_to_answer = "prefer_not_to_answer"


class SmokingStatus(str, PyEnum):
    never = "never"
    former = "former"
    current = "current"


class AlcoholUse(str, PyEnum):
    none = "none"
    occasional = "occasional"
    moderate = "moderate"
    heavy = "heavy"


class PregnancyStatus(str, PyEnum):
    not_pregnant = "not_pregnant"
    pregnant = "pregnant"
    unsure = "unsure"
    not_applicable = "not_applicable"


class TrialStatus(str, PyEnum):
    recruiting = "recruiting"
    active = "active"
    completed = "completed"
    not_yet_recruiting = "not_yet_recruiting"
    terminated = "terminated"
    withdrawn = "withdrawn"
    unknown = "unknown"


class MatchStrength(str, PyEnum):
    high = "high"
    medium = "medium"
    low = "low"


# -- Models (no schema specifications for SQLite) --

class User(Base):
    """User identity."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)

    age = Column(Integer, nullable=True)
    sex_assigned_at_birth = Column(String(50), nullable=True)
    location_text = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    fcm_token = Column(String(255), nullable=True)
    notifications_enabled = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """JWT refresh tokens."""
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")


class MedicalProfile(Base):
    """Protected health information."""
    __tablename__ = "medical_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    conditions = Column(JSON, default=list, nullable=False)
    medications = Column(JSON, default=list, nullable=False)
    allergies = Column(JSON, default=list, nullable=False)
    medical_history = Column(Text, nullable=True)
    biomarkers = Column(Text, nullable=True)
    smoking_status = Column(String(50), nullable=True)
    alcohol_use = Column(String(50), nullable=True)
    pregnancy_status = Column(String(50), nullable=True)
    travel_radius_miles = Column(Integer, default=50, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Trial(Base):
    """Clinical trial from ClinicalTrials.gov."""
    __tablename__ = "trials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nct_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    brief_summary = Column(Text, nullable=True)
    detailed_description = Column(Text, nullable=True)
    phase = Column(String(50), nullable=True)
    conditions = Column(JSON, default=list, nullable=False)
    keywords = Column(JSON, default=list, nullable=False)
    sponsor = Column(String(500), nullable=True)
    locations = Column(JSON, default=list, nullable=False)
    eligibility_inclusion = Column(Text, nullable=True)
    eligibility_exclusion = Column(Text, nullable=True)
    eligibility_sex = Column(String(50), nullable=True)
    eligibility_min_age = Column(String(50), nullable=True)
    eligibility_max_age = Column(String(50), nullable=True)
    enrollment_status = Column(String(50), default="unknown", nullable=False)
    contact_name = Column(String(500), nullable=True)
    contact_phone = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    url = Column(String(1000), nullable=True)
    last_updated = Column(DateTime, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)

    saved_by = relationship("SavedTrial", back_populates="trial", cascade="all, delete-orphan")


class SavedTrial(Base):
    """User bookmarked trials."""
    __tablename__ = "saved_trials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trial_id = Column(String(36), ForeignKey("trials.id", ondelete="CASCADE"), nullable=False)
    interested = Column(Boolean, default=False, nullable=False)
    last_known_status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trial = relationship("Trial", back_populates="saved_by")
