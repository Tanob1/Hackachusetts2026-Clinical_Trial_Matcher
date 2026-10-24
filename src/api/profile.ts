// OFFLINE profile api — reads/writes the on-device profile. No server.
import { readProfile, writeProfile } from '../data/store';

export async function getProfile() {
  return readProfile();
}

export async function updateProfile(data: {
  conditions: string[];
  medications: string[];
  allergies: string[];
  medical_history?: string;
  biomarkers?: string;
  smoking_status?: string;
  alcohol_use?: string;
  pregnancy_status?: string;
  travel_radius_miles: number;
}) {
  const current = await readProfile();
  return writeProfile({
    ...current,
    conditions: data.conditions,
    medications: data.medications,
    allergies: data.allergies,
    medical_history: data.medical_history ?? '',
    biomarkers: data.biomarkers ?? '',
    smoking_status: data.smoking_status ?? '',
    alcohol_use: data.alcohol_use ?? '',
    pregnancy_status: data.pregnancy_status ?? '',
    travel_radius_miles: data.travel_radius_miles,
  });
}
