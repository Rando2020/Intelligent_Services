const BACKEND_API_URL = window.GOVERNED_DELIVERY_API_URL || "http://localhost:8787/api/analyze";

const demos = {
  fileMover: {
    title: "Healthcare File Mover Delivery Demo",
    intake: `We need to onboard Centene for weekly LAMP outbound files by July 1. The file will include eligibility, claims, adherence opportunities, and pharmacy outreach records. The client needs the file every week and wants it delivered through their approved file delivery process.

We have a draft file layout and the data team says the SQL is mostly done. We still need to confirm the final delivery folder or endpoint, who should receive access, and whether Legal has approved the final field list. The team believes this is similar to prior client deliveries, so they want to move quickly.`,
    platforms: ["Generic File Mover", "SFTP / MFT"],
    blockers: [
      ["Legal approval not confirmed", "Attach Legal, Compliance, contract, BAA, SOW, or permitted-use approval."],
      ["Destination not confirmed", "Attach approved destination evidence for the file mover or delivery layer."],
      ["Recipient access not confirmed", "Attach recipient allowlist and access review."],
      ["Production-equivalent test delivery not completed", "Run and attach test delivery evidence."],
      ["Operational runbook not confirmed", "Create cadence, owner, monitoring, escalation, and pause/rollback plan."]
    ],
    tickets: [
      ["Complete governed delivery review for regulated data", "Product / Data Governance / Compliance"],
      ["Validate external recipient and destination controls", "Security / Implementation / Platform Operations"],
      ["Validate file mover route, destination, and delivery evidence", "Platform Operations / QA"],
      ["Execute production-equivalent test delivery", "QA / Platform Operations"],
      ["Approve governed production launch", "Product / PM / Compliance"]
    ],
    evidence: [
      ["approved_field_list", "Data Governance / Product"],
      ["approved_destination", "Implementation / Platform Operations"],
      ["recipient_allowlist", "Security"],
      ["route_config_review", "Platform Operations"],
      ["test_delivery_log", "QA"],
      ["runbook", "Operations"]
    ]
  },
  platformStack: {
    title: "Platform Stack Governance Demo",
    intake: `We need to launch a new governed healthcare reporting workflow for a payer client by August 15. The data is currently stored in Snowflake. Analytics Engineering is transforming it through dbt models. The weekly outbound file will be delivered through SFTP or another approved managed file transfer process. A dashboard will also be published in Tableau for internal operations, and a partner API may be used later to send status updates.

The SQL and dbt models are mostly built, but we still need to confirm the final approved field list, Snowflake role access, masking or row access policies, dbt test coverage, Tableau row-level security, SFTP destination folder, recipient allowlist, and API payload requirements. Legal has not yet approved the final field list. Security has not completed the access review. QA has not completed a production-equivalent test delivery.

The team wants to move quickly because leadership already shared the August 15 target date with the client.`,
    platforms: ["Snowflake", "dbt", "SFTP / MFT", "Tableau / Power BI", "API Integration", "Generic File Mover"],
    blockers: [
      ["Legal approval missing", "Attach permitted-use approval for regulated or external delivery work."],
      ["Snowflake access controls unresolved", "Review roles, service accounts, masking policies, and row access policies."],
      ["dbt lineage and tests unresolved", "Attach model ownership, test results, lineage, and downstream exposure review."],
      ["Reporting access not validated", "Validate Tableau/Power BI row-level security, export permissions, and subscriptions."],
      ["API payload requirements not confirmed", "Review endpoint, auth, payload schema, logging, and sensitive field handling."],
      ["SFTP destination and recipient allowlist missing", "Confirm host/path, recipient permissions, route config, and delivery evidence."]
    ],
    tickets: [
      ["Review Snowflake data classification and object tags", "Data Governance / Data Engineering"],
      ["Validate Snowflake access roles and service accounts", "Security / Data Platform"],
      ["Review dbt model ownership, tests, and lineage", "Analytics Engineering / Data Engineering"],
      ["Validate reporting access and row-level security", "BI / Security / Product"],
      ["Review API endpoint, authentication, and payload contract", "Engineering / Security"],
      ["Validate SFTP/MFT host, folder path, and route configuration", "Platform Operations / Data Engineering"]
    ],
    evidence: [
      ["masking_policy_reference", "Security / Data Governance"],
      ["row_access_policy_reference", "Security / Data Governance"],
      ["dbt_test_results", "Analytics Engineering"],
      ["lineage_graph_or_reference", "Analytics Engineering"],
      ["row_level_security_test_results", "BI / Security"],
      ["payload_schema", "Engineering / Security"],
      ["recipient_allowlist", "Security"],
      ["test_delivery_log", "QA"]
    ]
  }
};

let current = demos.platformStack;
let lastBackendResult = null;
let lastExportCsv = {};

const intake = document.getElementById("intake");
const score = document.getElementById("score");
const heroScore = document.getElementById("hero-score");
const launchPosition = document.getElementById("launch-position");
const heroStatus = document.getElementById("hero-status");
const scoreSummary = document.getElementById("score-summary");
const detectedPlatforms = document.getElementById("detected-platforms");
const blockerCount = document.getElementById("blocker-count");
const ticketCount = document.getElementById("ticket-count");
const evidenceCount = document.getElementById("evidence-count");
const blockers = document.getElementById("blockers");
const tickets = document.getElementById("tickets");
const evidence = document.getElementById("evidence");

function setDemo(demo) {
  current = demo;
  intake.value = demo.intake;
  analyze();
}

function detectPlatformsFromText(text) {
  const lowered = text.toLowerCase();
  const detected = [];
  const checks = [
    ["Snowflake", ["snowflake", "snowpipe", "warehouse", "schema", "copy into"]],
    ["dbt", ["dbt", "model", "lineage", "exposure"]],
    ["SFTP / MFT", ["sftp", "mft", "managed file transfer", "moveit", "folder path"]],
    ["Tableau / Power BI", ["tableau", "power bi", "dashboard", "row-level security", "rls"]],
    ["API Integration", ["api", "endpoint", "payload", "webhook", "oauth", "token"]],
    ["Generic File Mover", ["file", "outbound", "delivery", "recipient", "route", "upload"]]
  ];
  checks.forEach(([name, terms]) => {
    if (terms.some(term => lowered.includes(term))) detected.push(name);
  });
  return [...new Set(detected)];
}

function buildFallback(text) {
  const platforms = detectPlatformsFromText(text);
  const hasExternal = /client|external|recipient|outbound|deliver|sftp|api/i.test(text);
  const hasSensitive = /claims|eligibility|patient|member|phi|pii|healthcare|pharmacy|adherence/i.test(text);
  const missing = /not confirmed|still need|not yet|missing|unknown/i.test(text);

  const blockers = [];
  if (hasSensitive) blockers.push(["Sensitive data review required", "Confirm approved fields, classification, and permitted use."]);
  if (hasExternal) blockers.push(["External delivery controls required", "Confirm destination, recipient, access, and delivery evidence."]);
  if (missing) blockers.push(["Missing approvals or controls", "Resolve unknown approvals, owners, access, QA, and evidence before launch."]);
  if (platforms.includes("Snowflake")) blockers.push(["Snowflake controls required", "Review role access, masking, row access, lineage, stages, and unload/export controls."]);
  if (platforms.includes("Tableau / Power BI")) blockers.push(["Reporting access controls required", "Validate row-level security, export permissions, subscriptions, and refresh logic."]);

  const tickets = platforms.map(platform => [`Review ${platform} governance controls`, "Platform Owner / Security / Data Governance"]);
  if (hasExternal) tickets.push(["Validate external recipient and delivery controls", "Security / Platform Operations"]);
  if (hasSensitive) tickets.push(["Review regulated data fields and minimization controls", "Data Governance / Product"]);
  tickets.push(["Approve governed production launch", "Product / PM / Compliance"]);

  const evidence = [
    ["approved_field_list", "Data Governance"],
    ["access_review", "Security"],
    ["qa_validation", "QA"],
    ["launch_decision", "Product / PM / Compliance"]
  ];
  if (hasExternal) evidence.push(["approved_destination", "Platform Operations"], ["recipient_allowlist", "Security"], ["test_delivery_log", "QA"]);

  return { platforms, blockers, tickets, evidence, source: "local fallback" };
}

async function analyze() {
  const text = intake.value.trim();
  if (!text) {
    renderLocalResult({ platforms: [], blockers: [], tickets: [], evidence: [], source: "empty" });
    return;
  }

  score.textContent = "Analyzing...";
  heroScore.textContent = "Analyzing...";
  launchPosition.textContent = "Calling backend";
  heroStatus.textContent = "Calling backend";
  scoreSummary.textContent = `Using backend API: ${BACKEND_API_URL}`;

  try {
    const result = await callBackend(text);
    renderBackendResult(result);
  } catch (error) {
    const fallback = text === current.intake.trim() ? { ...current, source: "local fallback" } : buildFallback(text);
    renderLocalResult(fallback, `Backend unavailable, using local fallback. ${error.message || error}`);
  }
}

async function callBackend(text) {
  const response = await fetch(BACKEND_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: current.title || "Governed Delivery Free Trial Intake",
      intake: text
    })
  });

  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.message || "Backend analysis failed");
  }
  return body;
}

function renderBackendResult(result) {
  lastBackendResult = result;
  lastExportCsv = {
    jira: result.exports?.jira_csv || "",
    ado: result.exports?.ado_csv || "",
    rally: result.exports?.rally_csv || "",
    asana: result.exports?.asana_csv || ""
  };

  const summary = result.summary || {};
  const scoreValue = `${summary.overall_score ?? "N/A"} / 100`;
  const launch = formatValue(summary.launch_position || "unknown");
  const launchBlockers = result.scorecard?.launch_blockers || [];
  const generatedTickets = result.tickets || [];
  const evidenceItems = result.evidence_packet?.evidence_items || [];
  const profiles = result.platform_profile_report?.detected_profiles || [];

  score.textContent = scoreValue;
  heroScore.textContent = scoreValue;
  launchPosition.textContent = launch;
  heroStatus.textContent = launch;
  heroStatus.classList.toggle("blocked", launchBlockers.length > 0);
  scoreSummary.textContent = `Backend result. Matched rules: ${summary.matched_rule_count || 0}. Detected platforms: ${summary.detected_platform_count || 0}. Generated tickets: ${summary.ticket_count || generatedTickets.length}.`;

  renderChips(profiles.map(profile => `${profile.name} (${profile.suggested_current_level || "L0"})`));
  renderList(blockers, launchBlockers.map(item => [item.blocker, item.required_resolution || item.owner_role || "Resolution required"]));
  renderList(tickets, generatedTickets.slice(0, 18).map(item => [item.title, item.owner_role || item.work_item_type || "TBD"]));
  renderList(evidence, evidenceItems.slice(0, 18).map(item => [item.required_artifact, item.owner_role || item.evidence_area || "Evidence owner TBD"]));

  blockerCount.textContent = launchBlockers.length;
  ticketCount.textContent = generatedTickets.length;
  evidenceCount.textContent = evidenceItems.length;
}

function renderLocalResult(fallback, note = "Local fallback preview. Start backend API for real package generation.") {
  lastBackendResult = null;
  lastExportCsv = {};
  const scoreValue = fallback.blockers.length >= 5 ? "62 / 100" : fallback.blockers.length >= 3 ? "70 / 100" : "82 / 100";
  const launch = fallback.blockers.length ? "Not launchable" : "Launchable with controls";

  score.textContent = scoreValue;
  heroScore.textContent = scoreValue;
  launchPosition.textContent = launch;
  heroStatus.textContent = launch;
  heroStatus.classList.toggle("blocked", fallback.blockers.length > 0);
  scoreSummary.textContent = note;

  renderChips(fallback.platforms || []);
  renderList(blockers, fallback.blockers || []);
  renderList(tickets, fallback.tickets || []);
  renderList(evidence, fallback.evidence || []);

  blockerCount.textContent = (fallback.blockers || []).length;
  ticketCount.textContent = (fallback.tickets || []).length;
  evidenceCount.textContent = (fallback.evidence || []).length;
}

function renderChips(items) {
  detectedPlatforms.innerHTML = "";
  if (!items.length) {
    detectedPlatforms.innerHTML = '<span class="chip">No specific platform detected</span>';
    return;
  }
  items.forEach(item => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    detectedPlatforms.appendChild(chip);
  });
}

function renderList(node, rows) {
  node.innerHTML = "";
  rows.forEach(([title, body]) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${escapeHtml(title)}</strong>${escapeHtml(body)}`;
    node.appendChild(li);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatValue(value) {
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, letter => letter.toUpperCase());
}

function downloadCsv(platform) {
  const backendCsv = lastExportCsv[platform];
  const csv = backendCsv || buildFallbackCsv();
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${platform}_governed_delivery_export.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function buildFallbackCsv() {
  const rows = [
    ["Work Item Type", "Title", "Owner Role", "Risk Rating", "Legal Review Required", "Security Review Required", "Data Governance Required", "File Movement Required", "Launch Blocker"],
    ...Array.from(tickets.children).map(li => {
      const title = li.querySelector("strong")?.textContent || "Governed delivery work item";
      const owner = li.textContent.replace(title, "").trim();
      return ["Story", title, owner, "L4", "Yes", "Yes", "Yes", "Yes", "Yes"];
    })
  ];
  return rows.map(row => row.map(cell => `"${String(cell).replaceAll('"', '""')}"`).join(",")).join("\n");
}

document.getElementById("load-file-mover").addEventListener("click", () => setDemo(demos.fileMover));
document.getElementById("load-platform-stack").addEventListener("click", () => setDemo(demos.platformStack));
document.getElementById("analyze").addEventListener("click", analyze);
document.getElementById("clear").addEventListener("click", () => {
  intake.value = "";
  analyze();
});
document.querySelectorAll(".export").forEach(button => {
  button.addEventListener("click", () => downloadCsv(button.dataset.platform));
});

setDemo(demos.platformStack);
