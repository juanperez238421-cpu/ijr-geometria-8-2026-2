import { randomBytes, randomUUID } from 'node:crypto';

const API = 'https://rlfxnjbqxbozjdzkbwlz.supabase.co/functions/v1/geo8-circle-clash';
const GOOD_ORIGIN = 'https://juanperez238421-cpu.github.io';
const started = Date.now();

function assert(condition, message) {
  if (!condition) throw new Error(`FAIL: ${message}`);
  console.log(`PASS: ${message}`);
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const token = () => randomBytes(48).toString('hex');

async function request(payload, { origin = GOOD_ORIGIN, expect = 200 } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Origin': origin, 'X-Client-Version': 'circle-clash-integration-qa' },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    const data = await response.json().catch(() => ({}));
    if (response.status !== expect) {
      throw new Error(`Expected HTTP ${expect}, got ${response.status}: ${JSON.stringify(data)}`);
    }
    return { response, data };
  } finally {
    clearTimeout(timeout);
  }
}

async function snap(team, lastEventId = 0) {
  const { data } = await request({ action: 'snapshot', team_id: team.id, team_token: team.token, last_event_id: lastEventId });
  return data;
}

async function waitForPhase(team, phase, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let latest;
  while (Date.now() < deadline) {
    latest = await snap(team);
    if (latest?.room?.phase === phase) return latest;
    await sleep(650);
  }
  throw new Error(`Timed out waiting for phase=${phase}; last=${latest?.room?.phase}`);
}

console.log('Circle Clash Arena · live integration QA');
console.log(`Endpoint: ${API}`);

const healthResponse = await fetch(API, { headers: { Origin: GOOD_ORIGIN } });
const health = await healthResponse.json();
assert(healthResponse.ok && health.ok === true, 'Edge Function health check is live');
assert(health.rounds === 12, 'Server exposes exactly 12 circle rounds');

const badOrigin = await request({ action: 'snapshot', team_id: randomUUID(), team_token: token(), last_event_id: 0 }, { origin: 'https://example.com', expect: 403 });
assert(badOrigin.data.error === 'origin_denied', 'CORS/custom origin guard rejects non-course origins');

const room = `QA${Date.now().toString(36).slice(-8)}`.toUpperCase();
const teamA = { name: 'QA Circle Alpha', token: token(), joinId: randomUUID() };
const teamB = { name: 'QA Circle Beta', token: token(), joinId: randomUUID() };

const joinedA = (await request({ action: 'join', join_code: room, group_code: '8C', team_name: teamA.name, team_token: teamA.token, client_join_id: teamA.joinId })).data;
teamA.id = joinedA.session.team_id;
assert(Boolean(teamA.id), 'Team A joins and receives an opaque server team id');
assert(joinedA.snapshot.me.grade_points === 100, 'Team A starts at 100 grade points = 5.0');

const joinedB = (await request({ action: 'join', join_code: room, group_code: '8C', team_name: teamB.name, team_token: teamB.token, client_join_id: teamB.joinId })).data;
teamB.id = joinedB.session.team_id;
assert(Boolean(teamB.id), 'Team B joins the same room');
assert(joinedB.snapshot.room.id === joinedA.snapshot.room.id, 'Both teams resolve to one authoritative room');
assert(joinedB.snapshot.room.lobby_ends_at, 'Second team starts the server-side lobby countdown');

console.log('Waiting for the real 15 s lobby countdown…');
let solveA = await waitForPhase(teamA, 'solve', 22000);
assert(solveA.room.current_round === 1, 'Server advances lobby to round 1 solve phase');
assert(solveA.question?.round === 1, 'Round 1 circle question is delivered');
assert(!('correct_option' in solveA.question), 'Correct answer is hidden during solve phase');

const submitAId = randomUUID();
const submitA = (await request({ action: 'submit', team_id: teamA.id, team_token: teamA.token, client_event_id: submitAId, round_no: 1, selected_option: 'B' })).data;
assert(submitA.correct === true, 'Team A correct diameter answer is graded server-side');
assert(submitA.awarded_charge >= 10, 'Correct answer awards enough charge for Arc Bolt');

const duplicateSubmit = (await request({ action: 'submit', team_id: teamA.id, team_token: teamA.token, client_event_id: submitAId, round_no: 1, selected_option: 'B' })).data;
assert(duplicateSubmit.duplicate === true, 'Repeated answer event is idempotent');
assert(duplicateSubmit.awarded_charge === submitA.awarded_charge, 'Idempotent retry does not double-award charge');

const submitB = (await request({ action: 'submit', team_id: teamB.id, team_token: teamB.token, client_event_id: randomUUID(), round_no: 1, selected_option: 'A' })).data;
assert(submitB.correct === false && submitB.grade_penalty === 2, 'Wrong answer applies exactly −2 grade points');
assert(submitB.team.grade_points === 98, 'Team B grade points are authoritative after wrong answer');

console.log('Waiting for the real 40 s solve clock to enter battle phase…');
const attackPhase = await waitForPhase(teamA, 'attack', 47000);
assert(attackPhase.question.correct_option === 'B', 'Correct option is revealed only after solve phase closes');
assert(typeof attackPhase.question.explanation === 'string' && attackPhase.question.explanation.length > 10, 'Explanation is revealed for feedback');

const wrongTeamAttack = await request({ action: 'battle_action', team_id: teamB.id, team_token: teamB.token, client_event_id: randomUUID(), round_no: 1, battle_action: 'shield', target_team_id: null }, { expect: 409 });
assert(wrongTeamAttack.data.error === 'correct_answer_required', 'Incorrect team cannot attack or shield');

const actionId = randomUUID();
const attack = (await request({ action: 'battle_action', team_id: teamA.id, team_token: teamA.token, client_event_id: actionId, round_no: 1, battle_action: 'arc', target_team_id: teamB.id })).data;
assert(attack.damage === 5, 'Arc Bolt subtracts exactly 5 grade points');
assert(attack.target.grade_points === 93, 'Target falls from 98 to 93 after attack');

const duplicateAttack = (await request({ action: 'battle_action', team_id: teamA.id, team_token: teamA.token, client_event_id: actionId, round_no: 1, battle_action: 'arc', target_team_id: teamB.id })).data;
assert(duplicateAttack.duplicate === true, 'Repeated attack event is idempotent');
assert(duplicateAttack.damage === 5, 'Idempotent attack retry reports original result without extra damage');

const finalB = await snap(teamB, 0);
assert(finalB.me.grade_points === 93, 'Reconnect snapshot preserves the exact grade state');
assert(Math.abs(finalB.me.grade_points / 20 - 4.65) < 1e-9, 'Final points convert deterministically to 4.65/5 before display rounding');
const eventTypes = new Set((finalB.events || []).map(e => e.event_type));
assert(eventTypes.has('answer_correct') && eventTypes.has('answer_wrong') && eventTypes.has('attack'), 'Reconnect-safe event stream contains answer and attack history');
assert((finalB.teams || []).length === 2, 'Snapshot synchronizes both teams after battle');

console.log(`\nCircle Clash live integration QA: PASS in ${((Date.now() - started) / 1000).toFixed(1)} s`);
