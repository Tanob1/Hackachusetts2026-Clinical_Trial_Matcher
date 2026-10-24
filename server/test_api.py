#!/usr/bin/env python3
"""Quick API test script.

Tests all backend endpoints end-to-end against a running server.
Run after: uvicorn app.main:app --port 8000 && python seed_demo.py

Usage: python test_api.py [BASE_URL]
"""
import sys
import httpx
import json

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
DEMO_EMAIL = "demo@trialmatcher.app"
DEMO_PASSWORD = "demodemo123"

client = httpx.Client(base_url=BASE, timeout=15)

def test(name: str, response: httpx.Response) -> bool:
    status = "✅" if response.status_code < 400 else "❌"
    print(f"{status} {name}: {response.status_code}")
    if response.status_code >= 400:
        print(f"   Body: {response.text[:200]}")
        return False
    return True


print(f"Testing API at {BASE}\n")

# Health check
r = client.get("/admin/health")
test("GET /admin/health", r)

# Root
r = client.get("/")
test("GET /", r)

# Register a NEW test user
r = client.post("/auth/register", json={
    "email": "test@example.com",
    "password": "testpass123",
    "age": 40,
    "sex_assigned_at_birth": "female",
    "location_text": "Worcester, MA",
})
if r.status_code == 409:
    # Already exists — login instead
    r = client.post("/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    test("POST /auth/login (existing)", r)
else:
    test("POST /auth/register", r)

tokens = r.json()
access = tokens["access_token"]
headers = {"Authorization": f"Bearer {access}"}

# Get me
r = client.get("/auth/me", headers=headers)
test("GET /auth/me", r)

# Get profile (empty initially)
r = client.get("/profile", headers=headers)
test("GET /profile", r)

# Update profile
r = client.put("/profile", json={
    "conditions": ["Diabetes Type 2", "Hypertension", "Asthma"],
    "medications": ["Metformin", "Lisinopril", "Albuterol"],
    "allergies": ["Penicillin"],
    "medical_history": "Hospitalized 2020",
    "biomarkers": "A1C 7.2",
    "smoking_status": "former",
    "alcohol_use": "occasional",
    "pregnancy_status": "not_applicable",
    "travel_radius_miles": 100,
}, headers=headers)
test("PUT /profile", r)

# Get matches
r = client.get("/matches", headers=headers)
test("GET /matches", r)
matches = r.json()
print(f"   Found {len(matches)} matches")
if matches:
    print(f"   Top match: {matches[0]['title'][:60]} (strength: {matches[0].get('match_strength')})")

    # Get trial detail
    trial_id = matches[0]["id"]
    r = client.get(f"/trials/{trial_id}", headers=headers)
    test("GET /trials/:id", r)

    # Save trial
    r = client.post(f"/trials/{trial_id}/save", json={"interested": true}, headers=headers)
    test("POST /trials/:id/save", r)

    # Get saved
    r = client.get("/saved", headers=headers)
    test("GET /saved", r)
    saved = r.json()
    print(f"   Saved: {len(saved)} trials")

    # Unsave
    r = client.delete(f"/trials/{trial_id}/save", headers=headers)
    test("DELETE /trials/:id/save", r)

# Data export
r = client.get("/settings/export", headers=headers)
test("GET /settings/export", r)

# Notification preference
r = client.put("/settings/notifications", json={"notifications_enabled": True}, headers=headers)
test("PUT /settings/notifications", r)

# FCM token
r = client.put("/settings/fcm-token", json={"fcm_token": "fake-token-123"}, headers=headers)
test("PUT /settings/fcm-token", r)

# Login as demo user
r = client.post("/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
test("POST /auth/login (demo)", r)

if r.status_code == 200:
    demo_tokens = r.json()
    demo_headers = {"Authorization": f"Bearer {demo_tokens['access_token']}"}
    r = client.get("/matches", headers=demo_headers)
    test("GET /matches (demo user)", r)
    demo_matches = r.json()
    print(f"   Demo user has {len(demo_matches)} matches")

print("\n=== Test complete ===")
