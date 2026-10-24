// OFFLINE trials api. Same function names/shapes as the old networked version,
// but reads from the bundled dataset + on-device store. No server.
import trialsData from '../data/trials.json';
import { getMatches as runMatch, type Trial } from '../data/matching';
import { toFullTrial } from '../data/mapTrial';
import { readProfile, readSavedIds, setSaved, removeSaved } from '../data/store';

const TRIALS = trialsData as unknown as Trial[];
const byId = new Map(TRIALS.map((t) => [t.id, t]));

export async function getMatches(limit = 50) {
  const profile = await readProfile();
  const saved = await readSavedIds();
  const matches = runMatch(TRIALS, profile.conditions, limit);
  return matches.map((m) =>
    toFullTrial(m.trial, {
      match_group: m.group,
      matched_conditions: m.matched_conditions,
      eligibility_summary: m.eligibility_summary,
      nearest_distance_miles: m.nearest_distance_miles,
      is_saved: saved[m.trial.id] === true || saved[m.trial.id] === false,
    }),
  );
}

export async function getTrial(id: string) {
  const t = byId.get(id);
  if (!t) throw new Error('Trial not found');
  const saved = await readSavedIds();
  const isSaved = Object.prototype.hasOwnProperty.call(saved, id);
  return toFullTrial(t, { is_saved: isSaved, is_interested: saved[id] === true });
}

export async function saveTrial(id: string, interested = false) {
  await setSaved(id, interested);
  return { ok: true };
}

export async function unsaveTrial(id: string) {
  await removeSaved(id);
  return { ok: true };
}

export async function getSaved() {
  const saved = await readSavedIds();
  const ids = Object.keys(saved);
  return ids
    .map((id) => byId.get(id))
    .filter((t): t is Trial => !!t)
    .map((t) => ({
      id: t.id,
      trial: toFullTrial(t, { is_saved: true, is_interested: saved[t.id] === true }),
      interested: saved[t.id] === true,
      last_known_status: t.enrollment_status,
      status_changed: false,
      created_at: new Date().toISOString(),
    }));
}
