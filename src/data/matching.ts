// On-device matching engine.
// Ported from the server's app/matching.py (core logic). Because the bundled
// CSV carries only nct_id/title/phase/conditions/city/status, the offline
// matcher uses the fields that exist: condition overlap (hard filter) and
// recruiting-first ordering. Distance/age/sex filters from the server are not
// applied here because the bundled data does not include that detail.

export interface Trial {
  id: string;
  nct_id: string;
  title: string;
  phase: string | null;
  conditions: string[];
  city: string;
  enrollment_status: string;
  url: string;
}

export interface Match {
  trial: Trial;
  score: number;
  matched_conditions: string[];
  group: string;
  eligibility_summary: string;
  nearest_distance_miles: number | null;
}

const STOP = new Set([
  'the','and','or','of','to','in','for','with','without','a','an','is','are',
  'be','must','have','has','who','which','that','this','all','any','no','not',
]);

function tokenize(text: string | null | undefined): Set<string> {
  if (!text) return new Set();
  const toks = text.toLowerCase().match(/[a-z0-9]+/g) || [];
  return new Set(toks.filter((t) => t.length > 2 && !STOP.has(t)));
}

function neutralGroup(matched: string[]): string {
  if (matched.length === 0) return 'Related study';
  if (matched.length === 1) return `Matches your condition: ${matched[0]}`;
  return `Matches ${matched.length} of your conditions`;
}

// Score one trial against the user's conditions. Returns null on no overlap.
function scoreTrial(trial: Trial, userConditionTokens: Set<string>): Match | null {
  const trialTokens = new Set<string>();
  for (const c of trial.conditions) for (const t of tokenize(c)) trialTokens.add(t);

  const overlap = new Set<string>();
  for (const t of trialTokens) if (userConditionTokens.has(t)) overlap.add(t);
  if (overlap.size === 0) return null; // hard filter: must share a condition

  const matched = trial.conditions.filter((c) => {
    for (const t of tokenize(c)) if (overlap.has(t)) return true;
    return false;
  });

  let score = matched.length * 40;
  if (matched.length === trial.conditions.length && trial.conditions.length > 0) score += 15;
  if (trial.enrollment_status === 'recruiting') score += 10;
  else if (trial.enrollment_status === 'not_yet_recruiting') score += 5;

  const parts: string[] = [];
  if (trial.conditions.length) parts.push(`Conditions: ${trial.conditions.slice(0, 3).join(', ')}`);
  if (trial.city) parts.push(`Location: ${trial.city}`);
  if (trial.phase) parts.push(`Phase: ${trial.phase}`);

  return {
    trial,
    score,
    matched_conditions: matched,
    group: neutralGroup(matched),
    eligibility_summary: parts.join(' | ') || 'See full criteria for details.',
    nearest_distance_miles: null,
  };
}

export function getMatches(trials: Trial[], conditions: string[], limit = 50): Match[] {
  const userTokens = new Set<string>();
  for (const c of conditions) for (const t of tokenize(c)) userTokens.add(t);
  if (userTokens.size === 0) return [];

  const results: Match[] = [];
  for (const trial of trials) {
    const m = scoreTrial(trial, userTokens);
    if (m) results.push(m);
  }
  // recruiting first, then higher score
  results.sort((a, b) => {
    const ar = a.trial.enrollment_status === 'recruiting' ? 0 : 1;
    const br = b.trial.enrollment_status === 'recruiting' ? 0 : 1;
    if (ar !== br) return ar - br;
    return b.score - a.score;
  });
  return results.slice(0, limit);
}
