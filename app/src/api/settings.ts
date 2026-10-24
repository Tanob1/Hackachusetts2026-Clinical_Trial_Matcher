import client from './client';

export async function exportData() {
  const res = await client.get('/settings/export');
  return res.data;
}

export async function updateFCMToken(token: string) {
  const res = await client.put('/settings/fcm-token', { fcm_token: token });
  return res.data;
}

export async function setNotificationPreference(enabled: boolean) {
  const res = await client.put('/settings/notifications', { notifications_enabled: enabled });
  return res.data;
}

export async function deleteAccount() {
  const res = await client.delete('/settings/account');
  return res.data;
}
