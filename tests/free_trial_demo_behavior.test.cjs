const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

// Exercise the real script and event handlers. Only browser DOM/download and
// network boundaries are doubled; deferred fetches make response order deterministic.
function harness() {
  class Element {
    constructor() { this.children = []; this.listeners = {}; this.value = ''; this.textContent = ''; this.disabled = false; this.classes = new Set(); this.classList = { toggle: (c, on) => on ? this.classes.add(c) : this.classes.delete(c) }; }
    set innerHTML(value) { this.html = value; this.children = []; }
    get innerHTML() { return this.html || ''; }
    appendChild(node) { this.children.push(node); }
    removeChild(node) { this.children.splice(this.children.indexOf(node), 1); }
    addEventListener(event, fn) { this.listeners[event] = fn; }
    click() { return this.listeners.click?.(); }
    querySelector() { const match = this.innerHTML.match(/<strong>(.*?)<\/strong>/); return match && { textContent: match[1] }; }
  }
  const nodes = new Map();
  const get = id => { if (!nodes.has(id)) nodes.set(id, new Element()); return nodes.get(id); };
  const exports = ['jira', 'ado', 'rally', 'asana'].map(platform => Object.assign(new Element(), { dataset: { platform } }));
  const requests = [], downloads = [];
  const context = vm.createContext({
    window: {}, document: { getElementById: get, createElement: () => new Element(), body: new Element(), querySelectorAll: () => exports },
    Blob, URL: { createObjectURL: blob => { downloads.push(blob); return 'blob:test'; }, revokeObjectURL() {} },
    fetch: (url, options) => new Promise((resolve, reject) => requests.push({ url, body: JSON.parse(options.body), resolve: data => resolve({ ok: true, json: async () => data }), reject }))
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../apps/free-trial-demo/app.js'), 'utf8'), context);
  const flush = () => new Promise(resolve => setImmediate(resolve));
  return { get, requests, downloads, exports, flush,
    analyze(text) { get('intake').value = text; return get('analyze').click(); },
    async complete(index, data) { requests[index].resolve(data); await flush(); },
    async fail(index) { requests[index].reject(new Error('offline')); await flush(); },
    async csv(platform = 0) { exports[platform].click(); return downloads.at(-1)?.text(); }
  };
}
function result(score, label) {
  return { summary: { overall_score: score, launch_position: 'not_launchable', engine_score: score, ticket_count: 1 }, scorecard: { launch_blockers: [{ blocker: label, required_resolution: 'Review' }] }, tickets: [{ title: label, owner_role: 'QA' }], evidence_packet: { evidence_items: [{ required_artifact: label, owner_role: 'QA' }] }, platform_profile_report: { detected_profiles: [{ name: label }] }, exports: Object.fromEntries(['jira', 'ado', 'rally', 'asana'].map(p => [p + '_csv', p + ':' + label])) };
}

test('latest success wins over older success, including all CSV exports', async () => {
  const h = harness(); h.analyze('second');
  await h.complete(1, result(91, 'new')); await h.complete(0, result(12, 'old'));
  assert.equal(h.get('score').textContent, '91 / 100');
  assert.match(h.get('tickets').children[0].innerHTML, /new/);
  for (let i = 0; i < 4; i++) assert.equal(await h.csv(i), ['jira', 'ado', 'rally', 'asana'][i] + ':new');
});
test('stale errors cannot replace the latest successful result', async () => {
  const h = harness(); h.analyze('second'); await h.complete(1, result(91, 'new')); await h.fail(0);
  assert.equal(h.get('score').textContent, '91 / 100'); assert.equal(await h.csv(), 'jira:new');
});
test('stale completions do not stop the newest loading state or enable exports', async () => {
  const h = harness(); h.analyze('second'); await h.complete(0, result(12, 'old'));
  assert.equal(h.get('score').textContent, 'Analyzing...');
  assert.ok(h.exports.every(button => button.disabled));
  await h.csv(); assert.equal(h.downloads.length, 0);
  await h.complete(1, result(91, 'new')); assert.ok(h.exports.every(button => !button.disabled));
});
test('starting another analysis invalidates previous downloadable data', async () => {
  const h = harness(); await h.complete(0, result(12, 'old')); h.analyze('second');
  await h.csv(); assert.equal(h.downloads.length, 0);
  await h.complete(1, result(91, 'new')); assert.equal(await h.csv(), 'jira:new');
});
for (const outcome of ['success', 'error']) test(`Clear invalidates pending ${outcome}`, async () => {
  const h = harness(); h.get('clear').click();
  const clearedScore = h.get('score').textContent;
  if (outcome === 'success') await h.complete(0, result(12, 'old')); else await h.fail(0);
  assert.equal(h.get('intake').value, ''); assert.equal(h.get('score').textContent, clearedScore);
  assert.equal(h.get('tickets').children.length, 0);
  assert.ok(h.exports.every(button => !button.disabled));
  assert.doesNotMatch(await h.csv(), /old/);
});
test('demo selection wins over the previous pending analysis', async () => {
  const h = harness(); h.get('load-file-mover').click();
  assert.match(h.requests[1].body.title, /File Mover/);
  await h.complete(1, result(77, 'file mover')); await h.complete(0, result(12, 'old'));
  assert.equal(h.get('score').textContent, '77 / 100'); assert.equal(await h.csv(), 'jira:file mover');
});
test('latest failure renders its fallback and older success cannot replace it', async () => {
  const h = harness(); h.analyze('Snowflake warehouse'); await h.fail(1);
  const fallbackScore = h.get('score').textContent;
  assert.match(h.get('score-summary').textContent, /Backend unavailable/);
  assert.ok(h.exports.every(button => !button.disabled));
  await h.complete(0, result(12, 'old'));
  assert.equal(h.get('score').textContent, fallbackScore);
  assert.match(await h.csv(), /Review Snowflake governance controls/);
  assert.doesNotMatch(await h.csv(), /old/);
});
test('repeated Analyze clicks keep only the last response authoritative', async () => {
  const h = harness(); h.analyze('same'); h.analyze('same'); h.analyze('same');
  await h.complete(3, result(99, 'last')); await h.fail(1); await h.complete(2, result(33, 'middle')); await h.complete(0, result(12, 'old'));
  assert.equal(h.get('hero-score').textContent, '99 / 100'); assert.equal(await h.csv(), 'jira:last');
});
test('stale rejection leaves the newer request pending and exports unavailable', async () => {
  const h = harness(); h.analyze('second'); await h.fail(0);
  assert.equal(h.get('score').textContent, 'Analyzing...');
  assert.ok(h.exports.every(button => button.disabled));
  await h.csv(); assert.equal(h.downloads.length, 0);
  await h.complete(1, result(91, 'new')); assert.equal(await h.csv(), 'jira:new');
});
