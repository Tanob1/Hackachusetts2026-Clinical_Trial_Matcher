import React, { useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert,
  Switch, ActivityIndicator,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { exportData, setNotificationPreference, deleteAccount } from '../api/settings';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

export default function SettingsScreen({ navigation }: { navigation: NativeStackNavigationProp<any> }) {
  const { user, logout } = useAuth();
  const [notifEnabled, setNotifEnabled] = useState(true);
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await exportData();
      Alert.alert('Data Export', JSON.stringify(data, null, 2).substring(0, 5000));
    } catch (e) {
      Alert.alert('Error', 'Failed to export data');
    } finally {
      setExporting(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      'Delete Account',
      'This permanently deletes your account and ALL medical data. This cannot be undone. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete Forever', style: 'destructive', onPress: async () => {
            try {
              await deleteAccount();
              logout();
            } catch {
              Alert.alert('Error', 'Failed to delete account');
            }
          }
        }
      ]
    );
  };

  const toggleNotifications = async (value: boolean) => {
    setNotifEnabled(value);
    try {
      await setNotificationPreference(value);
    } catch { /* best-effort */ }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 30 }}>
      <Text style={styles.header}>Settings</Text>

      {/* Profile section */}
      <Text style={styles.sectionTitle}>Profile</Text>
      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('MedicalProfile')}>
        <Text style={styles.rowText}>Edit Medical Profile</Text>
        <Text style={styles.chevron}>→</Text>
      </TouchableOpacity>
      <View style={styles.row}>
        <Text style={styles.rowLabel}>Location</Text>
        <Text style={styles.rowValue}>{user?.location_text || 'Not set'}</Text>
      </View>

      {/* Notifications */}
      <Text style={styles.sectionTitle}>Notifications</Text>
      <View style={styles.row}>
        <Text style={styles.rowText}>Push notifications</Text>
        <Switch
          value={notifEnabled}
          onValueChange={toggleNotifications}
          trackColor={{ false: '#ccc', true: '#0F7B7B' }}
        />
      </View>
      <Text style={styles.helperText}>
        Get notified when a new trial matches your profile or a saved trial changes status.
      </Text>

      {/* Privacy */}
      <Text style={styles.sectionTitle}>Privacy & Data</Text>
      <TouchableOpacity style={styles.row} onPress={handleExport} disabled={exporting}>
        <Text style={styles.rowText}>{exporting ? 'Exporting...' : 'Export My Data'}</Text>
        {exporting && <ActivityIndicator size="small" color="#0F7B7B" />}
      </TouchableOpacity>
      <TouchableOpacity style={styles.row} onPress={handleDelete}>
        <Text style={[styles.rowText, { color: '#C62828' }]}>Delete Account</Text>
      </TouchableOpacity>

      {/* Privacy notice */}
      <View style={styles.privacyBox}>
        <Text style={styles.privacyTitle}>Privacy Notice</Text>
        <Text style={styles.privacyText}>
          Your medical profile is stored in a separate, encrypted database from your login info.
          We never share your medical data with third parties. Your data is never used for advertising.
        </Text>
      </View>

      {/* About */}
      <Text style={styles.sectionTitle}>About</Text>
      <View style={styles.row}>
        <Text style={styles.rowLabel}>Version</Text>
        <Text style={styles.rowValue}>1.0.0</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.rowLabel}>Data source</Text>
        <Text style={styles.rowValue}>ClinicalTrials.gov</Text>
      </View>

      {/* Logout */}
      <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>Trial Matcher is not a medical device or diagnostic tool.</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { fontSize: 28, fontWeight: 'bold', padding: 20, color: '#0F7B7B' },
  sectionTitle: { fontSize: 14, fontWeight: '600', color: '#0F7B7B', textTransform: 'uppercase',
    paddingHorizontal: 20, paddingTop: 20, paddingBottom: 6 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingVertical: 14, paddingHorizontal: 20, borderBottomWidth: 1, borderBottomColor: '#f0f0f0', minHeight: 50 },
  rowText: { fontSize: 16, color: '#333' },
  rowLabel: { fontSize: 16, color: '#666' },
  rowValue: { fontSize: 16, color: '#999' },
  chevron: { fontSize: 18, color: '#ccc' },
  helperText: { fontSize: 13, color: '#999', paddingHorizontal: 20, paddingBottom: 8 },
  privacyBox: { margin: 16, backgroundColor: '#F5F5F5', borderRadius: 10, padding: 16 },
  privacyTitle: { fontSize: 15, fontWeight: '600', color: '#333', marginBottom: 6 },
  privacyText: { fontSize: 14, color: '#666', lineHeight: 20 },
  logoutBtn: { margin: 20, backgroundColor: '#f5f5f5', borderRadius: 12, padding: 16, alignItems: 'center', minHeight: 50 },
  logoutText: { fontSize: 17, color: '#C62828', fontWeight: '600' },
  footer: { textAlign: 'center', fontSize: 12, color: '#bbb', paddingBottom: 10 },
});
