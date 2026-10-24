import client from './client';

export async function getMatches(limit = 50) {
  const res = await client.get('/matches', { params: { limit } });
  return res.data;
}

export async function getTrial(id: string) {
  const res = await client.get(`/trials/${id}`);
  return res.data;
}

export async function saveTrial(id: string, interested = false) {
  const res = await client.post(`/trials/${id}/save`, { interested });
  return res.data;
}

export async function unsaveTrial(id: string) {
  const res = await client.delete(`/trials/${id}/save`);
  return res.data;
}

export async function getSaved() {
  const res = await client.get('/saved');
  return res.data;
}
