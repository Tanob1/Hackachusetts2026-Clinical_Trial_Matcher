import client from './client';

export async function getProfile() {
  const res = await client.get('/profile');
  return res.data;
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
  const res = await client.put('/profile', data);
  return res.data;
}
