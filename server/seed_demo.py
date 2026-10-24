"""Demo data seeder.

Reads the healthcare/trials/data.csv file (3,131 MA recruiting trials)
and loads them into the database so you can test the app immediately
without waiting for a full ClinicalTrials.gov sync.

Also creates a demo user with a sample medical profile.
"""
from __future__ import annotations

import asyncio
import csv
import os
import sys
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import async_session, init_db
from app.models import Trial, TrialStatus, User, MedicalProfile
from app.security import hash_password, create_access_token, create_refresh_token
from app.config import get_settings


DEMO_CSV = os.path.expanduser("~/Downloads/healthcare/trials/data.csv")

# Demo user credentials
DEMO_EMAIL = "demo@trialmatcher.app"
DEMO_PASSWORD = "demodemo123"
DEMO_PROFILE = {
    "conditions": ["Diabetes Type 2", "Hypertension"],
    "medications": ["Metformin", "Lisinopril"],
    "allergies": ["Penicillin"],
    "medical_history": "Hospitalized for pneumonia in 2020",
    "biomarkers": "A1C 7.2",
    "smoking_status": "former",
    "alcohol_use": "occasional",
    "pregnancy_status": "not_applicable",
    "travel_radius_miles": 50,
}


def parse_csv_row(row: dict) -> dict:
    """Convert a CSV row to a normalized trial dict."""
    nct_id = row.get("nct_id", "").strip()
    if not nct_id:
        return None

    conditions = [c.strip() for c in (row.get("conditions") or "").split(",") if c.strip()]
    phase = row.get("phase", "").strip() or None
    status_str = (row.get("status") or "").strip().upper()
    status_map = {
        "RECRUITING": TrialStatus.recruiting,
        "ACTIVE_NOT_RECRUITING": TrialStatus.active,
        "COMPLETED": TrialStatus.completed,
        "NOT_YET_RECRUITING": TrialStatus.not_yet_recruiting,
    }
    enrollment_status = status_map.get(status_str, TrialStatus.recruiting)

    city = row.get("massachusetts_city", "").strip() or None

    return {
        "nct_id": nct_id,
        "title": row.get("title", "").strip() or nct_id,
        "brief_summary": None,
        "detailed_description": None,
        "phase": phase,
        "conditions": conditions,
        "keywords": [],
        "sponsor": None,
        "locations": [{"city": city, "state": "Massachusetts", "country": "United States", "facility": None, "lat": None, "lng": None}] if city else [{"city": "Boston", "state": "Massachusetts", "country": "United States", "facility": None, "lat": 42.3601, "lng": -71.0589}],
        "eligibility_inclusion": None,
        "eligibility_exclusion": None,
        "eligibility_sex": "All",
        "eligibility_min_age": None,
        "eligibility_max_age": None,
        "enrollment_status": enrollment_status,
        "contact_name": None,
        "contact_phone": None,
        "contact_email": None,
        "url": f"https://clinicaltrials.gov/study/{nct_id}",
        "last_updated": None,
    }


async def seed_demo_data():
    """Seed the database with demo trials + a demo user."""
    print("=== Trial Matcher Demo Data Seeder ===\n")

    # Ensure tables exist
    print("Creating tables...")
    await init_db()

    async with async_session() as db:
        # ── Seed trials from CSV ────────────────────────────────────────────────
        if not os.path.exists(DEMO_CSV):
            print(f"⚠️  Demo CSV not found at {DEMO_CSV}")
            print("   Falling back to live ClinicalTrials.gov API (20 studies)...")
            from app.ctgov_sync import sync_trials
            count = await sync_trials(db, max_studies=20)
            print(f"   Synced {count} studies from API.\n")
        else:
            print(f"Reading demo data from: {DEMO_CSV}")
            with open(DEMO_CSV, "r") as f:
                reader = csv.DictReader(f)
                trials_added = 0
                trials_updated = 0
                for row in reader:
                    data = parse_csv_row(row)
                    if not data:
                        continue

                    existing = await db.execute(select(Trial).where(Trial.nct_id == data["nct_id"]))
                    existing_trial = existing.scalar_one_or_none()

                    if existing_trial:
                        for key, value in data.items():
                            setattr(existing_trial, key, value)
                        existing_trial.synced_at = datetime.now(timezone.utc)
                        trials_updated += 1
                    else:
                        trial = Trial(**data)
                        db.add(trial)
                        trials_added += 1

                await db.commit()
            print(f"   ✅ Loaded {trials_added} new + {trials_updated} updated = {trials_added + trials_updated} total trials.\n")

        # ── Create demo user ──────────────────────────────────────────────────
        print("Creating demo user...")
        result = await db.execute(select(User).where(User.email == DEMO_EMAIL))
        demo_user = result.scalar_one_or_none()

        if not demo_user:
            demo_user = User(
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                age=55,
                sex_assigned_at_birth="male",
                location_text="Boston, MA",
                latitude=42.3601,
                longitude=-71.0589,
            )
            db.add(demo_user)
            await db.flush()

            # Create medical profile
            from app.models import SmokingStatus, AlcoholUse, PregnancyStatus
            profile = MedicalProfile(
                user_id=demo_user.id,
                conditions=DEMO_PROFILE["conditions"],
                medications=DEMO_PROFILE["medications"],
                allergies=DEMO_PROFILE["allergies"],
                medical_history=DEMO_PROFILE["medical_history"],
                biomarkers=DEMO_PROFILE["biomarkers"],
                smoking_status=SmokingStatus.former,
                alcohol_use=AlcoholUse.occasional,
                pregnancy_status=PregnancyStatus.not_applicable,
                travel_radius_miles=DEMO_PROFILE["travel_radius_miles"],
            )
            db.add(profile)
            await db.commit()
            print(f"   ✅ Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print(f"   ℹ️  Demo user already exists: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # ── Print login info ───────────────────────────────────────────────────
        access_token, expires_in = create_access_token(str(demo_user.id))
        print(f"\n   Access token (for API testing): {access_token[:50]}...\n")

        # ── Print a few sample matches ─────────────────────────────────────────
        print("Sample matches for demo user (Diabetes Type 2, Hypertension):")
        from app.matching import get_matches
        from app.models import MedicalProfile as MP
        result = await db.execute(select(MP).where(MP.user_id == demo_user.id))
        mp = result.scalar_one()
        matches = await get_matches(db, demo_user, mp, limit=5)
        for m in matches:
            print(f"   [{m.strength.upper():6s}] {m.trial.nct_id} — {m.trial.title[:60]}")
            print(f"          Score: {m.score:.0f} | Distance: {m.nearest_distance_miles} mi | Conditions: {', '.join(m.matched_conditions)}")

    print("\n=== Demo data ready ===")
    print(f"\nLogin: {DEMO_EMAIL}")
    print(f"Password: {DEMO_PASSWORD}")
    print(f"\nStart the server:  uvicorn app.main:app --reload --port 8000")
    print(f"API docs:           http://localhost:8000/docs")
    print(f"Health check:       http://localhost:8000/health")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
