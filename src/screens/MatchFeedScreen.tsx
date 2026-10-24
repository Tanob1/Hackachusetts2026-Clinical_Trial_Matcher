import React, { useState, useCallback } from 'react';
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl,
  ActivityIndicator, Linking,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { getMatches } from '../api/trials';
import { saveMatchesToCache, loadMatchesFromCache } from '../utils/cache';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type Match = {
  id: string;
  nct_id: string;
  title: string;
  phase: string | null;
  conditions: string[];
  sponsor: string | null;
  locations: any[];
  enrollment_status: string;
  match_group: string | null;
  matched_conditions: string[] | null;
  nearest_distance_miles: number | null;
  eligibility_summary: string | null;
};

const STATUS_COLORS: Record<string, string> = {
  recruiting: '#2E7D32',
  active: '#1565C0',
  not_yet_recruiting: '#F57C00',
  completed: '#757575',
};

export default function MatchFeedScreen({ navigation }: { navigation: NativeStackNavigationProp<any> }) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(false);

  const fetchMatches = useCallback(async (useCache = true) => {
    if (useCache) {
      const cached = await loadMatchesFromCache();
      if (cached.length > 0) setMatches(cached);
    }
    try {
      const data = await getMatches();
      setMatches(data);
      saveMatchesToCache(data);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchMatches();
    }, [fetchMatches])
  );

  const onRefresh = () => { setRefreshing(true); fetchMatches(false); };

  const renderItem = ({ item }: { item: Match }) => {
    const statusColor = STATUS_COLORS[item.enrollment_status] || '#757575';
    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate('TrialDetail', { trialId: item.id })}
        activeOpacity={0.8}
      >
        <View style={styles.cardHeader}>
          {item.phase && <Text style={styles.phaseBadge}>{item.phase}</Text>}
          <View style={[styles.statusBadge, { backgroundColor: statusColor + '22' }]}>
            <Text style={[styles.statusText, { color: statusColor }]}>
              {item.enrollment_status.replace(/_/g, ' ')}
            </Text>
          </View>
        </View>

        <Text style={styles.title}>{item.title}</Text>

        {item.sponsor && <Text style={styles.sponsor}>{item.sponsor}</Text>}

        <Text style={styles.conditions}>
          {item.conditions?.join(', ') || 'No conditions listed'}
        </Text>

        {/* Location + distance */}
        {item.locations?.length > 0 && (
          <Text style={styles.meta}>
            📍 {item.locations[0]?.city || item.locations[0]?.state || 'Location TBD'}
            {item.nearest_distance_miles != null && ` · ${item.nearest_distance_miles} mi`}
          </Text>
        )}

        {/* Neutral grouping — what the person appears to match (not a verdict) */}
        {item.match_group && (
          <Text style={styles.groupText}>{item.match_group}</Text>
        )}

        {/* Eligibility summary */}
        {item.eligibility_summary && (
          <Text style={styles.eligibility}>{item.eligibility_summary}</Text>
        )}

        {/* Matched criteria — the stated basis for showing this trial */}
        {item.matched_conditions && item.matched_conditions.length > 0 && (
          <Text style={styles.matchedText}>
            Criteria you appear to meet: {item.matched_conditions.join(', ')}
          </Text>
        )}
      </TouchableOpacity>
    );
  };

  if (loading && matches.length === 0) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#0F7B7B" /></View>;
  }

  return (
    <View style={styles.container}>
      {/* Disclaimer banner — required wording, visible without scrolling */}
      <View style={styles.disclaimer}>
        <Text style={styles.disclaimerText}>
          This is informational matching, not medical advice. It does not diagnose,
          treat, or tell you to join any study. Talk to your doctor or the study team
          before acting.
        </Text>
      </View>

      <FlatList
        data={matches}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No matches yet.</Text>
            <Text style={styles.emptySubtext}>Try updating your medical profile in Settings.</Text>
          </View>
        }
        contentContainerStyle={{ paddingBottom: 20 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  disclaimer: {
    backgroundColor: '#FFF8E1', paddingHorizontal: 16, paddingVertical: 10,
    borderLeftWidth: 3, borderLeftColor: '#FFC107',
  },
  disclaimerText: { fontSize: 13, color: '#795548' },
  card: {
    backgroundColor: '#fff', borderRadius: 12, padding: 16, marginHorizontal: 16,
    marginVertical: 6, elevation: 2, shadowColor: '#000', shadowOpacity: 0.08,
    shadowRadius: 4, shadowOffset: { width: 0, height: 2 },
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  groupText: { fontSize: 13, color: '#0F7B7B', fontWeight: '600', marginTop: 4 },
  phaseBadge: {
    fontSize: 12, fontWeight: '600', color: '#0F7B7B',
    backgroundColor: '#E0F7F7', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8,
  },
  statusBadge: { borderRadius: 12, paddingHorizontal: 8, paddingVertical: 4 },
  statusText: { fontSize: 12, fontWeight: '600' },
  title: { fontSize: 16, fontWeight: '600', color: '#222', lineHeight: 22, marginBottom: 4 },
  sponsor: { fontSize: 13, color: '#666', marginBottom: 4 },
  conditions: { fontSize: 14, color: '#0F7B7B', marginBottom: 6 },
  meta: { fontSize: 13, color: '#888', marginBottom: 4 },
  eligibility: { fontSize: 13, color: '#666', lineHeight: 18, marginTop: 4 },
  matchedText: { fontSize: 13, color: '#2E7D32', marginTop: 6, fontWeight: '500' },
  empty: { flex: 1, alignItems: 'center', paddingTop: 80 },
  emptyText: { fontSize: 18, color: '#666', fontWeight: '600' },
  emptySubtext: { fontSize: 14, color: '#999', marginTop: 8 },
});
