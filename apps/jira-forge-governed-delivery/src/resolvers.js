import api, { route } from '@forge/api';

const DEFAULT_API_URL = 'http://localhost:8787/api/analyze';

function getBackendUrl() {
  return process.env.GOVERNED_DELIVERY_API_URL || DEFAULT_API_URL;
}

export async function analyzeIntake(request) {
  const payload = request.payload || {};
  const intake = String(payload.intake || '').trim();
  const title = String(payload.title || 'Jira Governed Delivery Intake').trim();

  if (!intake) {
    return { ok: false, error: 'Intake is required.' };
  }

  const response = await fetch(getBackendUrl(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, intake }),
  });

  const body = await response.json();
  if (!response.ok) {
    return { ok: false, error: body.message || 'Backend analysis failed.', backend: body };
  }

  return { ok: true, result: body };
}

export async function getIssueContext(request) {
  const context = request.context || {};
  const issueKey = context.extension?.issue?.key;

  if (!issueKey) {
    return { ok: true, issue: null };
  }

  const response = await api.asApp().requestJira(route`/rest/api/3/issue/${issueKey}?fields=summary,issuetype,status,labels,project`);
  const issue = await response.json();

  return {
    ok: response.ok,
    issue: response.ok ? issue : null,
    error: response.ok ? null : issue,
  };
}

export async function createJiraIssuesFromTickets(request) {
  const payload = request.payload || {};
  const tickets = Array.isArray(payload.tickets) ? payload.tickets : [];
  const projectKey = String(payload.projectKey || '').trim();

  if (!projectKey) {
    return { ok: false, error: 'projectKey is required.' };
  }

  if (!tickets.length) {
    return { ok: false, error: 'At least one generated ticket is required.' };
  }

  const preparedIssues = tickets.slice(0, 25).map((ticket) => toJiraIssuePayload(projectKey, ticket));

  return {
    ok: true,
    dryRun: true,
    message: 'Dry run only. No Jira issues were created by this scaffold.',
    preparedIssues,
  };
}

function toJiraIssuePayload(projectKey, ticket) {
  return {
    fields: {
      project: { key: projectKey },
      issuetype: { name: mapIssueType(ticket.work_item_type) },
      summary: String(ticket.title || 'Governed delivery work item').slice(0, 255),
      description: toAdf(buildDescription(ticket)),
      labels: buildLabels(ticket),
    },
  };
}

function mapIssueType(workItemType) {
  const normalized = String(workItemType || '').toLowerCase();
  if (normalized === 'bug' || normalized === 'defect') return 'Bug';
  if (normalized === 'task' || normalized === 'subtask' || normalized === 'approval' || normalized === 'risk') return 'Task';
  return 'Story';
}

function buildLabels(ticket) {
  return [
    'GovernedDelivery',
    ticket.launch_blocker ? 'LaunchBlocker' : 'Governance',
    ticket.file_movement_required ? 'FileMovement' : null,
    ticket.source_rule_id ? `Rule-${ticket.source_rule_id}` : null,
  ].filter(Boolean).map((label) => label.replace(/[^A-Za-z0-9_-]/g, '-')).slice(0, 10);
}

function buildDescription(ticket) {
  const lines = [];
  lines.push(ticket.description || 'Generated governed delivery work item.');
  lines.push('');
  lines.push(`Owner Role: ${ticket.owner_role || 'TBD'}`);
  lines.push(`Risk Rating: ${ticket.risk_rating || 'TBD'}`);
  lines.push(`Launch Blocker: ${ticket.launch_blocker ? 'Yes' : 'No'}`);
  if (ticket.source_rule_id) lines.push(`Source Rule: ${ticket.source_rule_id}`);
  lines.push('');
  lines.push('Acceptance Criteria:');
  (ticket.acceptance_criteria || []).forEach((item, index) => lines.push(`${index + 1}. ${item}`));
  lines.push('');
  lines.push('Evidence Required:');
  (ticket.evidence_required || []).forEach((item) => lines.push(`- ${item}`));
  return lines.join('\n');
}

function toAdf(text) {
  return {
    type: 'doc',
    version: 1,
    content: String(text || '').split('\n').map((line) => ({
      type: 'paragraph',
      content: line ? [{ type: 'text', text: line }] : [],
    })),
  };
}
