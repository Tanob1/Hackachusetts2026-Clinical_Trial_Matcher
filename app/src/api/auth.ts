import client from './client';

export async function register(data: {
  email?: string;
  phone?: string;
  password: string;
  age: number;
  sex_assigned_at_birth: string;
  location_text: string;
}) {
  const res = await client.post('/auth/register', data);
  return res.data;
}

export async function login(data: { email?: string; phone?: string; password: string }) {
  const res = await client.post('/auth/login', data);
  return res.data;
}

export async function getMe() {
  const res = await client.get('/auth/me');
  return res.data;
}
