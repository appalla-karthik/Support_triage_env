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
        --bg: #f5f1e8;
        --bg-soft: #fcfaf5;
        --card: rgba(255, 252, 247, 0.96);
        --card-strong: #ffffff;
        --ink: #1b2e2a;
        --muted: #62706a;
        --accent: #295f56;
        --accent-deep: #173f39;
        --accent-soft: #e4efe9;
        --line: rgba(41, 95, 86, 0.14);
        --success: #2f7a5d;
        --warning: #a46a2a;
        --warm: #f0e1c8;
        --shadow: 0 24px 60px rgba(37, 55, 49, 0.08);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
        background:
          radial-gradient(circle at top left, rgba(240, 225, 200, 0.65), transparent 28%),
          radial-gradient(circle at top right, rgba(228, 239, 233, 0.9), transparent 24%),
          linear-gradient(180deg, #f8f4ec 0%, #f4efe6 100%);
        color: var(--ink);
      }
      main {
        width: 100%;
        max-width: none;
        margin: 0;
        padding: 14px 14px 24px;
      }
      .shell {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: var(--shadow);
        overflow: hidden;
        backdrop-filter: blur(14px);
      }
      .topbar {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.9fr);
        gap: 18px;
        padding: 24px;
        border-bottom: 1px solid var(--line);
        background:
          linear-gradient(180deg, rgba(255, 252, 247, 0.98), rgba(248, 244, 236, 0.94));
      }
      .hero-copy {
        display: grid;
        gap: 14px;
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        width: fit-content;
        padding: 8px 12px;
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
        margin: 0;
        font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
        font-size: 46px;
        line-height: 0.98;
        letter-spacing: -1px;
      }
      .subtitle {
        margin: 0;
        color: var(--muted);
        font-size: 16px;
        line-height: 1.7;
        max-width: 780px;
      }
      .hero-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
      }
      .mini-card {
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 14px;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(249, 246, 240, 0.92));
      }
      .mini-card strong {
        display: block;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.35px;
      }
      .mini-card span {
        display: block;
        margin-top: 8px;
        font-size: 20px;
        font-weight: 800;
        color: var(--accent-deep);
      }
      .mini-card p {
        margin: 8px 0 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
      }
      .status-card {
        min-width: 240px;
        padding: 18px;
        border: 1px solid var(--line);
        border-radius: 20px;
        background:
          linear-gradient(160deg, rgba(41, 95, 86, 0.96), rgba(23, 63, 57, 0.96));
        color: #f7f7f2;
        display: grid;
        gap: 14px;
      }
      .status-card strong {
        display: block;
        color: rgba(247, 247, 242, 0.72);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.35px;
      }
      .status-card span {
        display: block;
        margin-top: 0;
        font-size: 15px;
        font-weight: 700;
      }
      .status-card p {
        margin: 0;
        color: rgba(247, 247, 242, 0.84);
        font-size: 13px;
        line-height: 1.6;
      }
      .status-list {
        margin: 0;
        padding-left: 18px;
        color: rgba(247, 247, 242, 0.84);
        font-size: 13px;
        line-height: 1.6;
      }
      .layout {
        display: grid;
        grid-template-columns: 320px minmax(0, 1fr);
        align-items: start;
        gap: 14px;
        padding: 14px;
      }
      .sidebar {
        position: sticky;
        top: 14px;
        align-self: start;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 18px;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.93), rgba(251, 248, 242, 0.88));
      }
      .panel h2 {
        margin: 0 0 12px;
        font-size: 20px;
        letter-spacing: -0.2px;
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
      .section-kicker {
        display: inline-block;
        margin-bottom: 8px;
        color: var(--accent);
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.45px;
        text-transform: uppercase;
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
      .how-list,
      .judge-list {
        margin: 0;
        padding-left: 18px;
      }
      .how-list li,
      .judge-list li {
        color: var(--muted);
        line-height: 1.65;
      }
      .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--line), transparent);
      }
      .playground {
        display: grid;
        gap: 14px;
      }
      .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
      }
      .summary-card {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--card-strong);
        padding: 13px 14px;
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
        font-size: 16px;
        font-weight: 800;
        line-height: 1.25;
        overflow-wrap: anywhere;
        word-break: break-word;
        min-height: 2.5em;
      }
      .summary-card .metric-value {
        min-height: auto;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
      }
      .summary-card .task-value {
        max-width: 100%;
      }
      .toolbar {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 120px 160px;
        gap: 10px;
      }
      .editor-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
        gap: 14px;
        margin-top: 14px;
      }
      .note-card {
        border: 1px solid var(--line);
        border-radius: 16px;
        background: linear-gradient(180deg, #fcf9f3, #f7f2e8);
        padding: 14px;
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
        max-height: 360px;
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
        background: linear-gradient(135deg, #295f56, #173f39);
        color: white;
        box-shadow: 0 10px 22px rgba(23, 63, 57, 0.18);
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
        gap: 14px;
      }
      .json-wide {
        margin-top: 0;
      }
      .json-box {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #f5f9fb;
        overflow: hidden;
        min-width: 0;
      }
      .json-box header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        border-bottom: 1px solid var(--line);
        background: rgba(255, 252, 247, 0.92);
      }
      .json-box header strong {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.35px;
      }
      pre {
        margin: 0;
        padding: 14px;
        min-height: 220px;
        max-height: 420px;
        overflow: auto;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 12px;
        line-height: 1.55;
        color: #294757;
      }
      #schema-json {
        min-height: 180px;
        max-height: 320px;
      }
      .status-inline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
      }
      code {
        background: #edf4f7;
        border-radius: 8px;
        padding: 2px 6px;
        color: var(--accent);
      }
      @media (max-width: 1180px) {
        .topbar {
          grid-template-columns: 1fr;
        }
        .hero-grid {
          grid-template-columns: 1fr;
        }
        .layout {
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: static;
        }
        .toolbar,
        .editor-grid,
        .json-grid {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 980px) {
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
        .topbar {
          flex-direction: column;
          align-items: flex-start;
        }
        .toolbar {
          grid-template-columns: 1fr;
        }
        .status-card {
          min-width: 0;
          width: 100%;
        }
        h1 {
          font-size: 34px;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <section class="shell">
        <div class="topbar">
          <div class="hero-copy">
            <div class="eyebrow">
              <span class="status-dot"></span>
              OpenEnv Environment Live
            </div>
            <h1>Support Triage Environment</h1>
            <p class="subtitle">
              A real customer-support workflow for OpenEnv evaluation. Review the queue,
              classify issues, write safe replies, route tickets to the right team, and
              finish each task with strong partial-credit signals the judge can inspect.
            </p>
            <div class="hero-grid">
              <div class="mini-card">
                <strong>What This Tests</strong>
                <span>Reasoning + Ops</span>
                <p>Ticket routing, safe customer communication, escalation judgment, and queue prioritization.</p>
              </div>
              <div class="mini-card">
                <strong>Judge Flow</strong>
                <span>Reset -> Step</span>
                <p>Start an episode, inspect the generated task, then advance actions and watch score and state evolve.</p>
              </div>
              <div class="mini-card">
                <strong>Built For Review</strong>
                <span>Typed + Visible</span>
                <p>The UI exposes schema, live state, and latest response so behavior is easy to audit quickly.</p>
              </div>
            </div>
          </div>
          <div class="status-card">
            <strong>Current Service</strong>
            <span id="service-meta">Loading metadata...</span>
            <p>The live build should let a judge understand the environment, run one episode, and inspect raw outputs without guessing where to click.</p>
            <ul class="status-list">
              <li>Use <code>Reset</code> to generate a fresh task.</li>
              <li>Use <code>Suggested Action</code> for the next valid move.</li>
              <li>Use <code>Step</code> to see reward, score, state, and done flag update.</li>
            </ul>
          </div>
        </div>

        <div class="layout">
          <aside class="panel stack sidebar">
            <div>
              <span class="section-kicker">Overview</span>
              <h2>Quick Start</h2>
              <p>Use the controls on the right to run a full episode. Everything a reviewer needs is visible on one page: task summary, live state, latest response, and the OpenEnv schema.</p>
            </div>

            <div class="divider"></div>

            <div>
              <span class="section-kicker">How To Test</span>
              <ol class="how-list">
                <li>Choose a task and click <code>Reset</code>.</li>
                <li>Read the task summary cards and inspect the generated state.</li>
                <li>Click <code>Suggested Action</code> to populate the next valid move.</li>
                <li>Click <code>Step</code> repeatedly until <code>Done</code> becomes <code>true</code>.</li>
                <li>Inspect <code>Latest Response</code>, <code>Current State</code>, and <code>Schema Snapshot</code>.</li>
              </ol>
            </div>

            <div>
              <span class="section-kicker">Judge Checklist</span>
              <ul class="judge-list">
                <li><code>/reset</code> returns a live task with typed observation payloads.</li>
                <li><code>/step</code> updates reward, score, done flag, and state consistently.</li>
                <li><code>/schema</code> documents the action surface for direct evaluation.</li>
                <li>The task list covers easy, medium, and hard support-triage scenarios.</li>
              </ul>
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
              <span class="section-kicker">Interactive Runner</span>
              <h2>Playground</h2>
              <div class="summary-grid" style="margin-bottom: 12px;">
                <div class="summary-card"><strong>Task</strong><span class="task-value" id="task-text">billing_refund_easy</span></div>
                <div class="summary-card"><strong>Status</strong><span id="status-text">Ready</span></div>
                <div class="summary-card"><strong>Reward</strong><span class="metric-value" id="reward-text">0.00</span></div>
                <div class="summary-card"><strong>Score</strong><span class="metric-value" id="score-text">0.01</span></div>
                <div class="summary-card"><strong>Steps</strong><span class="metric-value" id="steps-text">0</span></div>
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
                    <li><code>Refresh Schema</code> shows the exact OpenEnv surface the judge can validate.</li>
                  </ul>
                </div>
              </div>

              <div class="button-row" style="margin-top: 12px;">
                <button class="primary" id="reset-btn" type="button">Reset</button>
                <button class="primary" id="step-btn" type="button">Step</button>
                <button id="state-btn" type="button">Get State</button>
                <button id="schema-btn" type="button">Refresh Schema</button>
              </div>
              <div class="pill" style="margin-top: 12px;">
                <span class="status-inline"><strong>Done</strong><span id="done-text">false</span></span>
              </div>
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

      function findNestedObject(value, predicate, seen = new WeakSet()) {
        if (!value || typeof value !== "object") {
          return null;
        }
        if (seen.has(value)) {
          return null;
        }
        seen.add(value);
        if (predicate(value)) {
          return value;
        }
        if (Array.isArray(value)) {
          for (const item of value) {
            const match = findNestedObject(item, predicate, seen);
            if (match) {
              return match;
            }
          }
          return null;
        }
        for (const nested of Object.values(value)) {
          const match = findNestedObject(nested, predicate, seen);
          if (match) {
            return match;
          }
        }
        return null;
      }

      function extractObservationPayload(payload) {
        if (!payload || typeof payload !== "object") {
          return null;
        }
        const nestedObservation = findNestedObject(
          payload,
          (candidate) =>
            !!candidate &&
            typeof candidate === "object" &&
            candidate.task &&
            Array.isArray(candidate.queue)
        );
        if (nestedObservation) {
          return nestedObservation;
        }
        return payload.observation && typeof payload.observation === "object"
          ? payload.observation
          : payload;
      }

      function extractStatePayload(payload) {
        if (!payload || typeof payload !== "object") {
          return null;
        }
        if (payload.state && typeof payload.state === "object") {
          return payload.state;
        }
        if (Array.isArray(payload.tickets)) {
          return payload;
        }
        const nestedState = findNestedObject(
          payload,
          (candidate) =>
            !!candidate &&
            typeof candidate === "object" &&
            Array.isArray(candidate.tickets)
        );
        if (nestedState) {
          return nestedState;
        }
        return null;
      }

      function buildStateFromObservation(observationPayload) {
        if (!observationPayload || !Array.isArray(observationPayload.queue)) {
          return null;
        }
        return {
          tickets: observationPayload.queue.map((ticket) => ({
            ...ticket,
            messages: [],
            outbound_messages: [],
            internal_notes: [],
            requested_information: [],
          })),
          progress: observationPayload.progress || null,
          step_count: 0,
        };
      }

      function getWorkingTickets() {
        if (latestState && Array.isArray(latestState.tickets) && latestState.tickets.length > 0) {
          return latestState.tickets;
        }
        const observationState = buildStateFromObservation(latestObservation);
        if (observationState && Array.isArray(observationState.tickets) && observationState.tickets.length > 0) {
          return observationState.tickets;
        }
        return [];
      }

      function setStatus(text) {
        statusText.textContent = text;
      }

      function updateSummary(payload, statePayload) {
        const observationPayload = extractObservationPayload(payload);
        const reward = payload && payload.reward != null
          ? Number(payload.reward)
          : observationPayload && observationPayload.reward != null
            ? Number(observationPayload.reward)
            : 0;
        rewardText.textContent = Number.isFinite(reward) ? reward.toFixed(2) : "0.00";
        doneText.textContent = payload ? String(Boolean(payload.done)) : doneText.textContent;
        const score = observationPayload && observationPayload.progress
          ? observationPayload.progress.score
          : statePayload && statePayload.progress
            ? statePayload.progress.score
            : null;
        const parsedScore = score == null ? null : Number(score);
        scoreText.textContent = parsedScore != null && Number.isFinite(parsedScore) ? parsedScore.toFixed(2) : "0.01";
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
        const workingTickets = getWorkingTickets();
        if (!workingTickets.length) {
          setStatus("Reset first so the UI can load real ticket IDs.");
          fillSample();
          return;
        }

        const tickets = [...workingTickets].sort((a, b) => {
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
        setStatus("Suggested next action generated.");
      }

      async function refreshState() {
        const response = await fetch("/state");
        const payload = await response.json();
        latestState = extractStatePayload(payload);
        stateKind.textContent = "state";
        stateJson.textContent = pretty(payload);
        updateSummary(latestResult, latestState);
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
        latestObservation = extractObservationPayload(payload);
        latestState =
          extractStatePayload(payload) ||
          buildStateFromObservation(latestObservation) ||
          latestState;
        latestResult = payload;
        responseKind.textContent = "reset";
        responseJson.textContent = pretty(payload);
        try {
          await refreshState();
        } catch (error) {
          stateKind.textContent = "state-error";
          stateJson.textContent = pretty({ error: "State fetch failed", detail: String(error) });
        }
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
          body: JSON.stringify(action),
        });
        const payload = await response.json();
        latestObservation = extractObservationPayload(payload);
        latestState =
          extractStatePayload(payload) ||
          buildStateFromObservation(latestObservation) ||
          latestState;
        latestResult = payload;
        responseKind.textContent = "step";
        responseJson.textContent = pretty(payload);
        try {
          await refreshState();
        } catch (error) {
          stateKind.textContent = "state-error";
          stateJson.textContent = pretty({ error: "State fetch failed", detail: String(error) });
        }
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
