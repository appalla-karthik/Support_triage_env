from __future__ import annotations

from openenv.core.env_server.http_server import create_app
from fastapi.responses import HTMLResponse, Response

from support_triage_env.models import SupportTriageAction, SupportTriageObservation
from support_triage_env.server.support_triage_environment import (
    SupportTriageOpenEnvEnvironment,
)


app = create_app(
    SupportTriageOpenEnvEnvironment,
    SupportTriageAction,
    SupportTriageObservation,
    env_name="support_triage_env",
    max_concurrent_envs=8,
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Support Triage Environment</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f3f6f8;
        --card: rgba(255, 255, 255, 0.97);
        --card-strong: #ffffff;
        --ink: #142f3b;
        --muted: #617887;
        --accent: #1f4c61;
        --accent-soft: #e7f0f4;
        --line: rgba(31, 76, 97, 0.11);
        --success: #2d7a61;
        --warning: #a86c2d;
        --shadow: 0 18px 46px rgba(20, 47, 59, 0.08);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
        background:
          linear-gradient(180deg, #f4f7f9 0%, #eef3f6 100%);
        color: var(--ink);
      }
      main {
        width: 100%;
        max-width: none;
        margin: 0;
        padding: 12px 12px 20px;
      }
      .shell {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 16px 40px rgba(20, 47, 59, 0.06);
        overflow: hidden;
      }
      .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 14px;
        padding: 16px 20px;
        border-bottom: 1px solid var(--line);
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 251, 252, 0.92));
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 11px;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.45px;
      }
      .status-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: var(--success);
      }
      h1 {
        margin: 10px 0 4px;
        font-size: 32px;
        line-height: 1.08;
        letter-spacing: -0.6px;
      }
      .subtitle {
        margin: 0;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
        max-width: 760px;
      }
      .status-card {
        min-width: 240px;
        padding: 12px 14px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: linear-gradient(180deg, #ffffff, #fbfdfe);
      }
      .status-card strong {
        display: block;
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.35px;
      }
      .status-card span {
        display: block;
        margin-top: 6px;
        font-size: 15px;
        font-weight: 700;
      }
      .layout {
        display: grid;
        grid-template-columns: 340px minmax(0, 1fr);
        gap: 12px;
        padding: 12px;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 14px;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(252, 253, 254, 0.86));
      }
      .panel h2 {
        margin: 0 0 10px;
        font-size: 18px;
        letter-spacing: -0.15px;
      }
      .panel p,
      .panel li,
      .helper,
      label {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
      }
      .stack > * + * {
        margin-top: 14px;
      }
      .helper {
        margin-bottom: 8px;
        font-weight: 700;
        color: var(--ink);
      }
      .muted {
        color: var(--muted);
      }
      .quick-code {
        background: #f7fafc;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 12px;
        white-space: pre-wrap;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 12px;
        line-height: 1.55;
        color: #264656;
      }
      .chip-row,
      .link-row,
      .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      .chip {
        background: var(--accent-soft);
        color: var(--accent);
        border-radius: 999px;
        padding: 7px 11px;
        font-size: 12px;
        font-weight: 700;
      }
      .playground {
        display: grid;
        gap: 12px;
      }
      .summary-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 8px;
      }
      .summary-card {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--card-strong);
        padding: 11px 13px;
      }
      .summary-card strong {
        display: block;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
      }
      .summary-card span {
        display: block;
        margin-top: 6px;
        font-size: 18px;
        font-weight: 800;
      }
      .toolbar {
        display: grid;
        grid-template-columns: 1fr 120px 160px;
        gap: 9px;
      }
      .editor-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
        gap: 12px;
        margin-top: 12px;
      }
      .note-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: #fbfdfe;
        padding: 12px;
      }
      .note-card strong {
        display: block;
        margin-bottom: 6px;
        font-size: 12px;
        letter-spacing: 0.35px;
        text-transform: uppercase;
        color: var(--muted);
      }
      .note-card ul {
        margin: 0;
        padding-left: 18px;
      }
      .note-card li + li {
        margin-top: 6px;
      }
      select,
      input,
      textarea,
      button {
        font: inherit;
      }
      select,
      input,
      textarea {
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 11px 12px;
        background: var(--card-strong);
        color: var(--ink);
      }
      textarea {
        min-height: 198px;
        resize: vertical;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 13px;
        line-height: 1.5;
      }
      button,
      .link-btn {
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 10px 14px;
        background: var(--card-strong);
        color: var(--accent);
        font-weight: 700;
        cursor: pointer;
        text-decoration: none;
        transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
      }
      button:hover,
      .link-btn:hover {
        transform: translateY(-1px);
        border-color: rgba(31, 76, 97, 0.20);
      }
      button.primary {
        border-color: transparent;
        background: linear-gradient(135deg, #1e5367, #2a6679);
        color: white;
        box-shadow: 0 10px 22px rgba(31, 83, 102, 0.12);
      }
      .pill {
        min-height: 48px;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--card-strong);
        padding: 12px 14px;
      }
      .pill strong {
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.35px;
        margin-right: 6px;
      }
      .json-grid {
        display: grid;
        grid-template-columns: 1.05fr 0.95fr;
        gap: 12px;
      }
      .json-wide {
        margin-top: 0;
      }
      .json-box {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #f5f9fb;
        overflow: hidden;
      }
      .json-box header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        border-bottom: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.82);
      }
      .json-box header strong {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.35px;
      }
      pre {
        margin: 0;
        padding: 14px;
        min-height: 280px;
        max-height: 440px;
        overflow: auto;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 12px;
        line-height: 1.55;
        color: #294757;
      }
      code {
        background: #edf4f7;
        border-radius: 8px;
        padding: 2px 6px;
        color: var(--accent);
      }
      @media (max-width: 980px) {
        .layout,
        .json-grid,
        .summary-grid,
        .editor-grid {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 720px) {
        main {
          width: 100%;
          padding: 8px 8px 16px;
        }
        .topbar,
        .layout {
          padding: 12px;
        }
        .toolbar {
          grid-template-columns: 1fr;
        }
        .status-card {
          min-width: 0;
        }
        .summary-grid {
          grid-template-columns: 1fr 1fr;
        }
        h1 {
          font-size: 28px;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <section class="shell">
        <div class="topbar">
          <div>
            <div class="eyebrow">
              <span class="status-dot"></span>
              OpenEnv Environment Live
            </div>
            <h1>Support Triage Environment</h1>
            <p class="subtitle">
              A compact playground for resetting episodes, sending actions, and inspecting
              JSON responses from the deployed customer support triage simulator.
            </p>
          </div>
          <div class="status-card">
            <strong>Current Service</strong>
            <span id="service-meta">Loading metadata...</span>
          </div>
        </div>

        <div class="layout">
          <aside class="panel stack">
            <div>
              <h2>Quick Start</h2>
              <p>Use the playground to start an episode, send actions, inspect state, and view raw JSON from the live OpenEnv server.</p>
            </div>

            <div>
              <div class="helper">Python client</div>
              <div class="quick-code">from support_triage_env import SupportTriageEnv

env = SupportTriageEnv(base_url="https://your-space-url")
await env.connect()</div>
            </div>

            <div>
              <div class="helper">Environment profile</div>
              <div class="chip-row">
                <span class="chip">3 Tasks</span>
                <span class="chip">Deterministic Graders</span>
                <span class="chip">Reward Shaping</span>
                <span class="chip">HTTP Simulation</span>
              </div>
            </div>

            <div>
              <div class="helper">Task presets</div>
              <div class="chip-row">
                <span class="chip">billing_refund_easy</span>
                <span class="chip">export_outage_medium</span>
                <span class="chip">security_and_refund_hard</span>
              </div>
            </div>

            <div>
              <div class="helper">Direct links</div>
              <div class="link-row">
                <a class="link-btn" href="/metadata" target="_blank" rel="noreferrer">Metadata</a>
                <a class="link-btn" href="/schema" target="_blank" rel="noreferrer">Schema</a>
                <a class="link-btn" href="/docs" target="_blank" rel="noreferrer">Docs</a>
                <a class="link-btn" href="/openapi.json" target="_blank" rel="noreferrer">OpenAPI JSON</a>
              </div>
            </div>

            <div>
              <div class="helper">Core endpoints</div>
              <div class="quick-code">POST /reset
POST /step
GET  /state
GET  /metadata
GET  /schema</div>
            </div>
          </aside>

          <section class="playground">
            <div class="panel">
              <h2>Playground</h2>
            <div class="summary-grid" style="margin-bottom: 12px;">
                <div class="summary-card"><strong>Task</strong><span id="task-text">billing_refund_easy</span></div>
                <div class="summary-card"><strong>Status</strong><span id="status-text">Ready</span></div>
                <div class="summary-card"><strong>Reward</strong><span id="reward-text">-</span></div>
                <div class="summary-card"><strong>Score</strong><span id="score-text">-</span></div>
                <div class="summary-card"><strong>Steps</strong><span id="steps-text">0</span></div>
              </div>
              <div class="toolbar">
                <div>
                  <label for="task">Task</label>
                  <select id="task">
                    <option value="billing_refund_easy">billing_refund_easy</option>
                    <option value="export_outage_medium">export_outage_medium</option>
                    <option value="security_and_refund_hard">security_and_refund_hard</option>
                  </select>
                </div>
                <div>
                  <label for="seed">Seed</label>
                  <input id="seed" type="number" placeholder="Optional" />
                </div>
                <div>
                  <label>&nbsp;</label>
                  <button id="fill-sample" type="button">Suggested Action</button>
                </div>
              </div>

              <div class="editor-grid">
                <div>
                  <label for="action-json">Action JSON</label>
                  <textarea id="action-json">{
  "action_type": "classify_ticket",
  "ticket_id": "TCK-0000",
  "category": "billing_refund",
  "priority": "medium",
  "team": "billing_ops"
}</textarea>
                </div>
                <div class="note-card">
                  <strong>Live Behavior</strong>
                  <ul>
                    <li><code>Reset</code> starts a fresh episode for the selected task.</li>
                    <li><code>Suggested Action</code> uses current state and real ticket IDs.</li>
                    <li><code>Step</code> updates reward, score, done flag, state, and raw response.</li>
                    <li><code>Get State</code> refreshes the internal environment snapshot.</li>
                  </ul>
                </div>
              </div>

              <div class="button-row" style="margin-top: 12px;">
                <button class="primary" id="reset-btn" type="button">Reset</button>
                <button class="primary" id="step-btn" type="button">Step</button>
                <button id="state-btn" type="button">Get State</button>
                <button id="schema-btn" type="button">Refresh Schema</button>
              </div>
              <div class="pill" style="margin-top: 12px;"><strong>Done</strong><span id="done-text">false</span></div>
            </div>

            <div class="json-grid">
              <section class="json-box">
                <header><strong>Latest Response</strong><span id="response-kind">idle</span></header>
                <pre id="response-json">{}</pre>
              </section>
              <section class="json-box">
                <header><strong>Current State</strong><span id="state-kind">idle</span></header>
                <pre id="state-json">{}</pre>
              </section>
            </div>
            <div class="json-wide">
              <section class="json-box">
                <header><strong>Schema Snapshot</strong><span id="schema-kind">loading</span></header>
                <pre id="schema-json">{}</pre>
              </section>
            </div>
          </section>
        </div>
      </section>
    </main>
    <script>
      const responseJson = document.getElementById("response-json");
      const stateJson = document.getElementById("state-json");
      const schemaJson = document.getElementById("schema-json");
      const statusText = document.getElementById("status-text");
      const rewardText = document.getElementById("reward-text");
      const scoreText = document.getElementById("score-text");
      const stepsText = document.getElementById("steps-text");
      const taskText = document.getElementById("task-text");
      const doneText = document.getElementById("done-text");
      const responseKind = document.getElementById("response-kind");
      const stateKind = document.getElementById("state-kind");
      const schemaKind = document.getElementById("schema-kind");
      const taskInput = document.getElementById("task");
      const seedInput = document.getElementById("seed");
      const actionInput = document.getElementById("action-json");
      const serviceMeta = document.getElementById("service-meta");
      let latestState = null;
      let latestObservation = null;
      let latestResult = null;

      function pretty(data) {
        return JSON.stringify(data, null, 2);
      }

      function setStatus(text) {
        statusText.textContent = text;
      }

      function updateSummary(payload, statePayload) {
        rewardText.textContent = payload && payload.reward != null ? String(payload.reward) : "-";
        doneText.textContent = payload ? String(Boolean(payload.done)) : doneText.textContent;
        const score = payload && payload.observation && payload.observation.progress
          ? payload.observation.progress.score
          : statePayload && statePayload.progress
            ? statePayload.progress.score
            : null;
        scoreText.textContent = score == null ? "-" : String(score);
        stepsText.textContent = statePayload && statePayload.step_count != null ? String(statePayload.step_count) : "0";
        taskText.textContent = taskInput.value;
      }

      async function loadMetadata() {
        const response = await fetch("/metadata");
        const payload = await response.json();
        serviceMeta.textContent = `${payload.name} v${payload.version || "?"}`;
      }

      async function loadSchema() {
        schemaKind.textContent = "schema";
        const response = await fetch("/schema");
        const payload = await response.json();
        schemaJson.textContent = pretty(payload);
      }

      function inferCategory(ticket) {
        const subject = (ticket.subject || "").toLowerCase();
        const latestMessage = (ticket.messages || [])
          .map((message) => message.content || "")
          .join(" ")
          .toLowerCase();
        const combined = `${subject} ${latestMessage}`;
        if (combined.includes("mfa") || combined.includes("2fa") || combined.includes("compromised") || combined.includes("recovery") || combined.includes("one-time code") || combined.includes("suspicious activity") || combined.includes("ceo")) {
          return {
            category: "security_account_takeover",
            priority: "urgent",
            team: "trust_safety"
          };
        }
        if (combined.includes("refund") || combined.includes("duplicate charge") || combined.includes("charged twice") || combined.includes("invoice") || combined.includes("extra charge") || combined.includes("billed twice")) {
          return {
            category: "billing_refund",
            priority: "medium",
            team: "billing_ops"
          };
        }
        if (combined.includes("export") || combined.includes("csv") || combined.includes("xlsx") || combined.includes("500 error") || combined.includes("502 error") || combined.includes("server error") || combined.includes("reporting")) {
          return {
            category: "product_bug",
            priority: "high",
            team: "engineering"
          };
        }
        return {
          category: "account_access",
          priority: "medium",
          team: "customer_support"
        };
      }

      function defaultReply(ticket, defaults) {
        if (defaults.category === "billing_refund") {
          return "I am sorry for the duplicate charge. I have started the refund for the extra payment, and you should see it within 5-7 business days.";
        }
        if (defaults.category === "product_bug") {
          return "I am sorry this is blocking your work. I have escalated this issue to engineering for investigation. Please share the affected workspace, approximate timestamp, and browser details to help us triage faster.";
        }
        if (defaults.category === "security_account_takeover") {
          return "I am sorry you are dealing with this. I have escalated this to our security team and Trust and Safety specialists. Please do not share passwords or one-time codes. Keep MFA enabled and use the secure recovery flow or password reset link to regain access.";
        }
        return "I am sorry you are having trouble accessing the account. Please use the secure password reset flow, and let us know if access is still blocked afterward.";
      }

      function defaultEscalation(ticket, defaults) {
        if (defaults.category === "security_account_takeover") {
          return `Escalating ${ticket.ticket_id} to Trust and Safety for urgent account-takeover review. Subject: ${ticket.subject}. Keep MFA enabled and use secure recovery steps only.`;
        }
        return `Escalating ${ticket.ticket_id} for specialist review. Subject: ${ticket.subject}.`;
      }

      function buildSuggestedActionFromState() {
        if (!latestState || !Array.isArray(latestState.tickets)) {
          fillSample();
          return;
        }

        const tickets = [...latestState.tickets].sort((a, b) => {
          const priorityRank = { urgent: 0, high: 1, medium: 2, low: 3 };
          const aDefaults = inferCategory(a);
          const bDefaults = inferCategory(b);
          const aDone = ["resolved", "escalated"].includes(a.current_status) ? 1 : 0;
          const bDone = ["resolved", "escalated"].includes(b.current_status) ? 1 : 0;
          if (aDone !== bDone) return aDone - bDone;
          return (priorityRank[aDefaults.priority] ?? 9) - (priorityRank[bDefaults.priority] ?? 9);
        });

        for (const ticket of tickets) {
          const defaults = inferCategory(ticket);
          if (ticket.current_category !== defaults.category || ticket.current_priority !== defaults.priority || ticket.assigned_team !== defaults.team) {
            actionInput.value = pretty({
              action_type: "classify_ticket",
              ticket_id: ticket.ticket_id,
              category: defaults.category,
              priority: defaults.priority,
              team: defaults.team
            });
            return;
          }

          if (defaults.category === "billing_refund") {
            if (!ticket.outbound_messages || ticket.outbound_messages.length === 0) {
              actionInput.value = pretty({
                action_type: "draft_reply",
                ticket_id: ticket.ticket_id,
                message: defaultReply(ticket, defaults)
              });
              return;
            }
            if (ticket.current_status !== "resolved") {
              actionInput.value = pretty({
                action_type: "resolve_ticket",
                ticket_id: ticket.ticket_id,
                resolution_code: "refund_submitted"
              });
              return;
            }
            continue;
          }

          if (defaults.category === "product_bug" || defaults.category === "security_account_takeover") {
            if (!ticket.outbound_messages || ticket.outbound_messages.length === 0) {
              actionInput.value = pretty({
                action_type: "draft_reply",
                ticket_id: ticket.ticket_id,
                message: defaultReply(ticket, defaults)
              });
              return;
            }
            if (ticket.current_status !== "escalated") {
              actionInput.value = pretty({
                action_type: "escalate_ticket",
                ticket_id: ticket.ticket_id,
                team: defaults.team,
                message: defaultEscalation(ticket, defaults)
              });
              return;
            }
            continue;
          }
        }

        actionInput.value = pretty({ action_type: "finish" });
      }

      async function refreshState() {
        const response = await fetch("/state");
        const payload = await response.json();
        latestState = payload;
        stateKind.textContent = "state";
        stateJson.textContent = pretty(payload);
        updateSummary(latestResult, payload);
        return payload;
      }

      async function doReset() {
        setStatus("Resetting episode...");
        const body = { task_id: taskInput.value };
        if (seedInput.value !== "") {
          body.seed = Number(seedInput.value);
        }
        const response = await fetch("/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const payload = await response.json();
        latestObservation = payload.observation || null;
        latestResult = payload;
        responseKind.textContent = "reset";
        responseJson.textContent = pretty(payload);
        await refreshState();
        updateSummary(payload, latestState);
        setStatus(response.ok ? "Episode reset successfully" : "Reset failed");
        buildSuggestedActionFromState();
      }

      async function doStep() {
        setStatus("Sending action...");
        let action;
        try {
          action = JSON.parse(actionInput.value);
        } catch (error) {
          setStatus("Action JSON is invalid");
          responseKind.textContent = "client-error";
          responseJson.textContent = pretty({ error: "Invalid JSON", detail: String(error) });
          return;
        }
        const response = await fetch("/step", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action }),
        });
        const payload = await response.json();
        latestObservation = payload.observation || null;
        latestResult = payload;
        responseKind.textContent = "step";
        responseJson.textContent = pretty(payload);
        await refreshState();
        updateSummary(payload, latestState);
        setStatus(response.ok ? "Action executed" : "Step request failed");
        buildSuggestedActionFromState();
      }

      async function getState() {
        setStatus("Fetching current state...");
        const payload = await refreshState();
        responseKind.textContent = "state";
        responseJson.textContent = pretty(payload);
        setStatus("State loaded");
      }

      function fillSample() {
        const samples = {
          billing_refund_easy: {
            action_type: "classify_ticket",
            ticket_id: "TCK-0000",
            category: "billing_refund",
            priority: "medium",
            team: "billing_ops"
          },
          export_outage_medium: {
            action_type: "classify_ticket",
            ticket_id: "TCK-0000",
            category: "product_bug",
            priority: "high",
            team: "engineering"
          },
          security_and_refund_hard: {
            action_type: "classify_ticket",
            ticket_id: "TCK-0000",
            category: "security_account_takeover",
            priority: "urgent",
            team: "trust_safety"
          }
        };
        actionInput.value = pretty(samples[taskInput.value]);
      }

      document.getElementById("reset-btn").addEventListener("click", doReset);
      document.getElementById("step-btn").addEventListener("click", doStep);
      document.getElementById("state-btn").addEventListener("click", getState);
      document.getElementById("schema-btn").addEventListener("click", loadSchema);
      document.getElementById("fill-sample").addEventListener("click", buildSuggestedActionFromState);
      taskInput.addEventListener("change", () => {
        taskText.textContent = taskInput.value;
        fillSample();
      });

      fillSample();
      loadMetadata().catch((error) => {
        serviceMeta.textContent = "Metadata unavailable";
        responseKind.textContent = "error";
        responseJson.textContent = pretty({ error: "Metadata fetch failed", detail: String(error) });
      });
      loadSchema().catch((error) => {
        schemaKind.textContent = "error";
        schemaJson.textContent = pretty({ error: "Schema fetch failed", detail: String(error) });
      });
      refreshState().catch(() => {});
    </script>
  </body>
</html>
"""


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
