import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator,
  Alert, Linking, Share,
} from 'react-native';
import { getTrial, saveTrial, unsaveTrial } from '../api/trials';

export default function TrialDetailScreen({ route }: { route: any }) {
  const { trialId } = route.params;
  const [trial, setTrial] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => { loadTrial(); }, [trialId]);

  const loadTrial = async () => {
    try {
      const data = await getTrial(trialId);
      setTrial(data);
    } catch (e) {
      Alert.alert('Error', 'Failed to load trial');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (interested = false) => {
    setSaving(true);
    try {
      if (trial.is_saved) {
        await unsaveTrial(trialId);
        setTrial({ ...trial, is_saved: false, is_interested: false });
      } else {
        await saveTrial(trialId, interested);
        setTrial({ ...trial, is_saved: true, is_interested: interested });
        if (interested) {
          Alert.alert('✅', 'Your interest has been noted. The trial team will contact you if you may qualify.');
        }
      }
    } catch (e) {
      Alert.alert('Error', 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  const shareTrial = async () => {
    if (!trial?.url) return;
    try {
      await Share.share({ url: trial.url, message: `${trial.title}\n${trial.url}` });
    } catch {}
  };

  if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#0F7B7B" /></View>;
  if (!trial) return <View style={styles.center}><Text>Trial not found</Text></View>;

  const inclusionLines = (trial.eligibility_inclusion || '')
    .split('\n').map((l: string) => l.trim()).filter((l: string) => l);
  const exclusionLines = (trial.eligibility_exclusion || '')
    .split('\n').map((l: string) => l.trim()).filter((l: string) => l);

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 30 }}>
      {/* Title + status */}
      <View style={styles.header}>
        {trial.phase && <Text style={styles.phaseBadge}>{trial.phase}</Text>}
        <Text style={[styles.statusBadge, { backgroundColor: '#2E7D3215' }]}>
          {trial.enrollment_status?.replace(/_/g, ' ')}
        </Text>
      </View>
      <Text style={styles.title}>{trial.title}</Text>
      <Text style={styles.nctId}>{trial.nct_id}</Text>

      {/* Sponsor */}
      {trial.sponsor && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Sponsor</Text>
          <Text style={styles.sectionBody}>{trial.sponsor}</Text>
        </View>
      )}

      {/* Conditions */}
      {trial.conditions?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Conditions</Text>
          <View style={styles.tagRow}>
            {trial.conditions.map((c: string, i: number) => (
              <Text key={i} style={styles.tag}>{c}</Text>
            ))}
          </View>
        </View>
      )}

      {/* Summary */}
      {trial.brief_summary && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Summary</Text>
          <Text style={styles.sectionBody}>{trial.brief_summary}</Text>
        </View>
      )}

      {/* Eligibility */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Eligibility Criteria</Text>

        {inclusionLines.length > 0 && (
          <>
            <Text style={styles.subHeader}>Inclusion Criteria:</Text>
            {inclusionLines.map((line: string, i: number) => (
              <Text key={i} style={styles.bullet}>✓ {line}</Text>
            ))}
          </>
        )}

        {exclusionLines.length > 0 && (
          <>
            <Text style={styles.subHeader}>Exclusion Criteria:</Text>
            {exclusionLines.map((line: string, i: number) => (
              <Text key={i} style={styles.bulletRed}>✗ {line}</Text>
            ))}
          </>
        )}

        {/* Age + Sex */}
        <View style={styles.eligibilityRow}>
          {trial.eligibility_sex && <Text style={styles.eligChip}>Sex: {trial.eligibility_sex}</Text>}
          {trial.eligibility_min_age && <Text style={styles.eligChip}>Min age: {trial.eligibility_min_age}</Text>}
          {trial.eligibility_max_age && <Text style={styles.eligChip}>Max age: {trial.eligibility_max_age}</Text>}
        </View>
      </View>

      {/* Locations */}
      {trial.locations?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Locations ({trial.locations.length})</Text>
          {trial.locations.map((loc: any, i: number) => (
            <Text key={i} style={styles.location}>📍 {loc.facility || 'Facility'}{'\n'}
              {loc.city}{loc.city && loc.state ? ', ' : ''}{loc.state}{loc.country ? `, ${loc.country}` : ''}
            </Text>
          ))}
        </View>
      )}

      {/* Contact */}
      {(trial.contact_name || trial.contact_phone || trial.contact_email) && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contact</Text>
          {trial.contact_name && <Text style={styles.sectionBody}>{trial.contact_name}</Text>}
          {trial.contact_phone && <Text style={styles.sectionBody}>📞 {trial.contact_phone}</Text>}
          {trial.contact_email && <Text style={styles.sectionBody}>✉ {trial.contact_email}</Text>}
        </View>
      )}

      {/* Disclaimer — required wording */}
      <View style={styles.disclaimer}>
        <Text style={styles.disclaimerText}>
          This is informational matching, not medical advice. It does not diagnose,
          treat, or tell you to join any study. Talk to your doctor or the study team
          before acting.
        </Text>
      </View>

      {/* Buttons */}
      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={[styles.button, trial.is_saved ? styles.buttonSaved : styles.buttonOutline]}
          onPress={() => handleSave(false)} disabled={saving}
        >
          <Text style={[styles.buttonText, trial.is_saved ? styles.buttonTextSaved : styles.buttonTextOutline]}>
            {trial.is_saved ? '★ Saved' : '☆ Save'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.buttonInterested]}
          onPress={() => handleSave(true)} disabled={saving || trial.is_saved}
        >
          <Text style={styles.buttonText}>I'm Interested</Text>
        </TouchableOpacity>
      </View>

      {/* Share + external link */}
      <View style={styles.linkRow}>
        <TouchableOpacity onPress={shareTrial}>
          <Text style={styles.linkText}>Share this trial</Text>
        </TouchableOpacity>
        {trial.url && (
          <TouchableOpacity onPress={() => Linking.openURL(trial.url)}>
            <Text style={styles.linkText}>View on ClinicalTrials.gov →</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', gap: 8, padding: 20, paddingBottom: 0 },
  phaseBadge: { fontSize: 13, fontWeight: '600', color: '#0F7B7B', backgroundColor: '#E0F7F7', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  statusBadge: { fontSize: 13, fontWeight: '600', color: '#2E7D32', borderRadius: 12, paddingHorizontal: 10, paddingVertical: 4 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#222', padding: 20, paddingBottom: 4 },
  nctId: { fontSize: 13, color: '#999', paddingHorizontal: 20, marginBottom: 8 },
  section: { paddingHorizontal: 20, paddingVertical: 12, borderTopWidth: 1, borderTopColor: '#f0f0f0' },
  sectionTitle: { fontSize: 17, fontWeight: 'bold', color: '#222', marginBottom: 8 },
  sectionBody: { fontSize: 15, color: '#444', lineHeight: 22 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  tag: { fontSize: 14, color: '#0F7B7B', backgroundColor: '#E0F7F7', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  subHeader: { fontSize: 15, fontWeight: '600', color: '#333', marginTop: 8, marginBottom: 4 },
  bullet: { fontSize: 14, color: '#2E7D32', paddingLeft: 12, marginBottom: 3, lineHeight: 20 },
  bulletRed: { fontSize: 14, color: '#C62828', paddingLeft: 12, marginBottom: 3, lineHeight: 20 },
  eligibilityRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 12 },
  eligChip: { fontSize: 13, color: '#666', backgroundColor: '#f5f5f5', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  location: { fontSize: 14, color: '#444', lineHeight: 20, marginBottom: 8 },
  disclaimer: { marginHorizontal: 20, marginTop: 12, backgroundColor: '#FFF8E1', borderRadius: 10, padding: 12, borderLeftWidth: 4, borderLeftColor: '#FFC107' },
  disclaimerText: { fontSize: 13, color: '#795548', lineHeight: 18 },
  buttonRow: { flexDirection: 'row', gap: 12, paddingHorizontal: 20, marginTop: 16 },
  button: { flex: 1, borderRadius: 12, padding: 16, alignItems: 'center', minHeight: 50 },
  buttonOutline: { borderWidth: 2, borderColor: '#0F7B7B', backgroundColor: '#fff' },
  buttonSaved: { backgroundColor: '#E0F7F7', borderWidth: 2, borderColor: '#0F7B7B' },
  buttonInterested: { backgroundColor: '#0F7B7B' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  buttonTextOutline: { color: '#0F7B7B', fontSize: 16, fontWeight: '600' },
  buttonTextSaved: { color: '#0F7B7B', fontSize: 16, fontWeight: '600' },
  linkRow: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 20, marginTop: 16, marginBottom: 8 },
  linkText: { fontSize: 15, color: '#0F7B7B', fontWeight: '500' },
});
