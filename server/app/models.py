"""Database models.

Two-schema separation for HIPAA compliance:
  auth   — user identity (email/phone, password hash, refresh tokens)
  medical — PHI (conditions, meds, allergies, etc.) linked by internal UUID
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, Enum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enumerations ──────────────────────────────────────────────────────────────

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
    active = "active"          # active, not recruiting
    completed = "completed"
    not_yet_recruiting = "not_yet_recruiting"
    terminated = "terminated"
    withdrawn = "withdrawn"
    unknown = "unknown"


class MatchStrength(str, PyEnum):
    high = "high"
    medium = "medium"
    low = "low"


# ── AUTH schema (identity) ────────────────────────────────────────────────────

class User(Base):
    """User identity — stored in the `auth` schema."""
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Basic onboarding fields (not PHI — demographics used for matching)
    age = Column(Integer, nullable=True)
    sex_assigned_at_birth = Column(Enum(SexAssignedAtBirth), nullable=True)
    location_text = Column(String(255), nullable=True)  # "Boston, MA" or "02115"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Push notification token (FCM)
    fcm_token = Column(String(255), nullable=True)
    notifications_enabled = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """JWT refresh tokens for session management."""
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")


# ── MEDICAL schema (PHI) ───────────────────────────────────────────────────────

class MedicalProfile(Base):
    """Protected health information — stored in the `medical` schema.

    Linked to auth.users only by the internal UUID. Never log this data.
    """
    __tablename__ = "medical_profiles"
    __table_args__ = {"schema": "medical"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)

    conditions = Column(JSONB, default=list, nullable=False)          # ["Diabetes Type 2", "Hypertension"]
    medications = Column(JSONB, default=list, nullable=False)          # ["Metformin", "Lisinopril"]
    allergies = Column(JSONB, default=list, nullable=False)            # ["Penicillin"]
    medical_history = Column(Text, nullable=True)                     # surgeries, hospitalizations
    biomarkers = Column(Text, nullable=True)                           # free text lab values
    smoking_status = Column(Enum(SmokingStatus), nullable=True)
    alcohol_use = Column(Enum(AlcoholUse), nullable=True)
    pregnancy_status = Column(Enum(PregnancyStatus), nullable=True)
    travel_radius_miles = Column(Integer, default=50, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ── Clinical trials (public data) ─────────────────────────────────────────────

class Trial(Base):
    """Normalized clinical trial pulled from ClinicalTrials.gov v2 API."""
    __tablename__ = "trials"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nct_id = Column(String(20), unique=True, nullable=False, index=True)  # NCT01234567
    title = Column(Text, nullable=False)
    brief_summary = Column(Text, nullable=True)
    detailed_description = Column(Text, nullable=True)
    phase = Column(String(50), nullable=True)
    conditions = Column(JSONB, default=list, nullable=False)        # ["Diabetes Type 2"]
    keywords = Column(JSONB, default=list, nullable=False)         # search keywords
    sponsor = Column(String(500), nullable=True)
    locations = Column(JSONB, default=list, nullable=False)        # [{city, state, country, lat, lng, facility}]
    eligibility_inclusion = Column(Text, nullable=True)
    eligibility_exclusion = Column(Text, nullable=True)
    eligibility_sex = Column(String(50), nullable=True)            # "All", "Male", "Female"
    eligibility_min_age = Column(String(50), nullable=True)        # "18 Years" or "N/A"
    eligibility_max_age = Column(String(50), nullable=True)
    enrollment_status = Column(Enum(TrialStatus), default=TrialStatus.unknown, nullable=False)
    contact_name = Column(String(500), nullable=True)
    contact_phone = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    url = Column(String(1000), nullable=True)                    # ClinicalTrials.gov link
    last_updated = Column(DateTime(timezone=True), nullable=True)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

    saved_by = relationship("SavedTrial", back_populates="trial", cascade="all, delete-orphan")


class SavedTrial(Base):
    """User bookmarked trials."""
    __tablename__ = "saved_trials"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True)
    trial_id = Column(UUID(as_uuid=True), ForeignKey("public.trials.id", ondelete="CASCADE"), nullable=False)
    interested = Column(Boolean, default=False, nullable=False)  # "I'm interested" vs just saved
    last_known_status = Column(Enum(TrialStatus), nullable=True)  # track status changes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trial = relationship("Trial", back_populates="saved_by")
