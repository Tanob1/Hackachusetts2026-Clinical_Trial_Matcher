"""Pydantic schemas for API request/response validation."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# â”€â”€ Auth â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class RegisterRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=8, max_length=128)
    age: int = Field(ge=0, le=150)
    sex_assigned_at_birth: str
    location_text: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str | None
    phone: str | None
    age: int | None
    sex_assigned_at_birth: str | None
    location_text: str | None


# â”€â”€ Medical Profile â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class MedicalProfileRequest(BaseModel):
    conditions: list[str] = []
    medications: list[str] = []
    allergies: list[str] = []
    medical_history: str | None = None
    biomarkers: str | None = None
    smoking_status: str | None = None
    alcohol_use: str | None = None
    pregnancy_status: str | None = None
    travel_radius_miles: int = Field(default=50, ge=1, le=1000)


class MedicalProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    conditions: list[str]
    medications: list[str]
    allergies: list[str]
    medical_history: str | None
    biomarkers: str | None
    smoking_status: str | None
    alcohol_use: str | None
    pregnancy_status: str | None
    travel_radius_miles: int
    updated_at: datetime | None = None


# â”€â”€ Trials â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class LocationInfo(BaseModel):
    city: str | None
    state: str | None
    country: str | None
    facility: str | None
    lat: float | None
    lng: float | None
    distance_miles: float | None = None


class TrialSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nct_id: str
    title: str
    phase: str | None
    conditions: list[str]
    sponsor: str | None
    locations: list[dict]
    eligibility_inclusion: str | None
    eligibility_exclusion: str | None
    enrollment_status: str
    last_updated: datetime | None
    # Computed match fields
    match_score: float | None = None
    match_strength: str | None = None
    matched_conditions: list[str] | None = None
    nearest_distance_miles: float | None = None
    eligibility_summary: str | None = None
    # NEW: ICD-10 medical code match details
    match_explanation: str | None = None
    icd10_matches: list[dict] | None = None


class TrialDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nct_id: str
    title: str
    brief_summary: str | None
    detailed_description: str | None
    phase: str | None
    conditions: list[str]
    keywords: list[str]
    sponsor: str | None
    locations: list[dict]
    eligibility_inclusion: str | None
    eligibility_exclusion: str | None
    eligibility_sex: str | None
    eligibility_min_age: str | None
    eligibility_max_age: str | None
    enrollment_status: str
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    url: str | None
    last_updated: datetime | None
    is_saved: bool = False
    is_interested: bool = False


# â”€â”€ Saved Trials â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class SavedTrialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    trial: TrialSummary
    interested: bool
    last_known_status: str | None
    status_changed: bool = False
    created_at: datetime


class SaveTrialRequest(BaseModel):
    interested: bool = False


# â”€â”€ Misc â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class MessageResponse(BaseModel):
    message: str


class DataExportResponse(BaseModel):
    user: dict
    medical_profile: dict | None
    saved_trials: list[dict]


class UpdateFCMTokenRequest(BaseModel):
    fcm_token: str


class NotificationPreferenceRequest(BaseModel):
    notifications_enabled: bool

