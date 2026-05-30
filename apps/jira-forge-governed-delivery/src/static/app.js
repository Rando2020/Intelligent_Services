import { invoke } from '@forge/bridge';

let lastResult = null;

const title = document.getElementById('title');
const intake = document.getElementById('intake');
const score = document.getElementById('score');
const summary = document.getElementById('summary');
const platforms = document.getElementById('platforms');
const blockers = document.getElementById('blockers');
const tickets = document.getElementById('tickets');
const payloads = document.getElementById('payloads');

function renderList(node, items, renderItem) {
  node.innerHTML = '';
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = renderItem(item);
    node.appendChild(li);
  });
}

async function analyze() {
  score.textContent = 'Analyzing...';
  payloads.textContent = 'No payloads prepared.';

  const response = await invoke('analyzeIntake', {
    title: title.value,
    intake: intake.value,
  });

  if (!response.ok) {
    score.textContent = 'Analysis failed';
    summary.textContent = response.error || 'Unknown error';
    return;
  }

  lastResult = response.result;
  const resultSummary = lastResult.summary || {};
  score.textContent = `${resultSummary.overall_score || 'N/A'} / 100`;
  summary.textContent = `Rating: ${resultSummary.overall_rating || 'unknown'} | Launch: ${resultSummary.launch_position || 'unknown'} | Tickets: ${resultSummary.ticket_count || 0}`;

  renderList(platforms, lastResult.platform_profile_report?.detected_profiles || [], (profile) => `${profile.name} (${profile.suggested_current_level || 'L0'})`);
  renderList(blockers, lastResult.scorecard?.launch_blockers || [], (blocker) => `${blocker.blocker}: ${blocker.required_resolution}`);
  renderList(tickets, (lastResult.tickets || []).slice(0, 20), (ticket) => `${ticket.title} — ${ticket.owner_role || 'TBD'}`);
}

async function preparePayloads() {
  if (!lastResult) {
    payloads.textContent = 'Run analysis first.';
    return;
  }

  const projectKey = prompt('Enter Jira project key for dry run payloads:', 'GOV');
  if (!projectKey) return;

  const response = await invoke('createJiraIssuesFromTickets', {
    projectKey,
    tickets: (lastResult.tickets || []).slice(0, 10),
  });

  payloads.textContent = JSON.stringify(response, null, 2);
}

document.getElementById('analyze').addEventListener('click', analyze);
document.getElementById('prepare').addEventListener('click', preparePayloads);
