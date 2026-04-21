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
    <title>TriageOS Enterprise Workflow Environment</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f4f1eb;
        --bg-soft: #fbf8f3;
        --panel: rgba(255, 255, 255, 0.88);
        --panel-strong: #ffffff;
        --panel-muted: #f7f3ee;
        --ink: #191816;
        --muted: #67635d;
        --muted-strong: #504c47;
        --accent: #232d3b;
        --accent-soft: #eef1f5;
        --line: rgba(25, 24, 22, 0.09);
        --line-strong: rgba(25, 24, 22, 0.15);
        --success: #2f6f55;
        --warning: #9a6730;
        --shadow: 0 24px 70px rgba(20, 22, 25, 0.08);
        --shadow-soft: 0 12px 34px rgba(20, 22, 25, 0.05);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(218, 208, 192, 0.34), transparent 28%),
          radial-gradient(circle at top right, rgba(224, 229, 236, 0.52), transparent 24%),
          linear-gradient(180deg, #f7f4ef 0%, #f0ece6 100%);
        color: var(--ink);
      }
      main {
        max-width: 1600px;
        margin: 0 auto;
        padding: 20px 20px 28px;
      }
      .shell {
        position: relative;
        background: rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.65);
        border-radius: 28px;
        box-shadow: var(--shadow);
        overflow: hidden;
        backdrop-filter: blur(18px);
      }
      .shell::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(35, 45, 59, 0.18), transparent);
      }
      .topbar {
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.9fr);
        gap: 24px;
        padding: 28px 28px 24px;
        border-bottom: 1px solid var(--line);
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(249, 246, 240, 0.56));
      }
      .hero-copy {
        display: grid;
        gap: 18px;
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        width: fit-content;
        padding: 7px 12px;
        border-radius: 999px;
        border: 1px solid rgba(35, 45, 59, 0.08);
        background: rgba(255, 255, 255, 0.68);
        color: var(--accent);
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 0 4px rgba(47, 111, 85, 0.12);
      }
      h1 {
        margin: 0;
        font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
        font-size: 62px;
        line-height: 0.92;
        letter-spacing: -1.2px;
        max-width: none;
      }
      .headline {
        display: grid;
        gap: 8px;
      }
      .headline-mark,
      .headline-sub {
        display: block;
      }
      .headline-sub {
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif;
        font-size: 23px;
        font-weight: 600;
        letter-spacing: -0.35px;
        color: var(--muted-strong);
        margin-top: 8px;
      }
      .subtitle {
        margin: 0;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.8;
        max-width: 820px;
      }
      .hero-note {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 2px;
      }
      .hero-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
      }
      .mini-card {
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(247, 244, 239, 0.82));
        box-shadow: var(--shadow-soft);
      }
      .mini-card strong {
        display: block;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.45px;
      }
      .mini-card span {
        display: block;
        margin-top: 10px;
        font-size: 19px;
        font-weight: 700;
        color: var(--ink);
      }
      .mini-card p {
        margin: 10px 0 0;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.65;
      }
      .status-card {
        min-width: 280px;
        padding: 22px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        background:
          linear-gradient(180deg, rgba(28, 33, 40, 0.96), rgba(22, 26, 33, 0.96));
        color: #f7f5f0;
        display: grid;
        gap: 16px;
        box-shadow: 0 18px 50px rgba(21, 24, 31, 0.18);
        align-content: space-between;
      }
      .status-card strong {
        display: block;
        color: rgba(247, 245, 240, 0.56);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.45px;
      }
      .status-card span {
        display: block;
        margin-top: 0;
        font-size: 17px;
        font-weight: 600;
        line-height: 1.4;
      }
      .status-card p {
        margin: 0;
        color: rgba(247, 245, 240, 0.78);
        font-size: 13px;
        line-height: 1.7;
      }
      .status-list {
        margin: 0;
        padding-left: 18px;
        color: rgba(247, 245, 240, 0.76);
        font-size: 13px;
        line-height: 1.7;
      }
      .layout {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) 340px;
        align-items: start;
        gap: 18px;
        padding: 18px;
      }
      .sidebar {
        display: grid;
        gap: 16px;
        position: sticky;
        top: 18px;
        align-self: start;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 22px;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(249, 246, 241, 0.86));
        box-shadow: var(--shadow-soft);
      }
      .overview-card {
        padding: 20px;
      }
      .panel h2 {
        margin: 0 0 12px;
        font-size: 22px;
        letter-spacing: -0.35px;
      }
      .panel p,
      .panel li,
      .helper,
      label {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.65;
      }
      .stack > * + * {
        margin-top: 16px;
      }
      .section-kicker {
        display: inline-block;
        margin-bottom: 8px;
        color: var(--accent);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.55px;
        text-transform: uppercase;
      }
      .helper {
        margin-bottom: 10px;
        font-weight: 700;
        color: var(--ink);
      }
      .muted {
        color: var(--muted);
      }
      .quick-code {
        background: #f7f5f2;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px;
        white-space: pre-wrap;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 12px;
        line-height: 1.65;
        color: #2f3640;
      }
      .chip-row,
      .link-row,
      .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }
      .chip {
        background: rgba(238, 241, 245, 0.92);
        color: var(--muted-strong);
        border: 1px solid rgba(35, 45, 59, 0.08);
        border-radius: 999px;
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 600;
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
        background: linear-gradient(90deg, transparent, rgba(25, 24, 22, 0.12), transparent);
      }
      .playground {
        display: grid;
        gap: 18px;
      }
      .runner-panel {
        display: grid;
        gap: 18px;
      }
      .runner-head {
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 16px;
      }
      .runner-copy {
        display: grid;
        gap: 8px;
      }
      .runner-copy p {
        margin: 0;
        max-width: 720px;
      }
      .runner-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 12px;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.88);
        color: var(--muted-strong);
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
      }
      .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
        gap: 12px;
      }
      .summary-card {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.92);
        padding: 16px;
        box-shadow: 0 8px 24px rgba(20, 22, 25, 0.04);
      }
      .summary-card strong {
        display: block;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .summary-card span {
        display: block;
        margin-top: 8px;
        font-size: 16px;
        font-weight: 700;
        line-height: 1.35;
        overflow-wrap: anywhere;
        word-break: break-word;
        min-height: 2.5em;
        color: var(--ink);
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
        grid-template-columns: minmax(0, 1fr) 120px 180px;
        gap: 12px;
      }
      .control-grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 130px 190px;
        gap: 12px;
      }
      .control-card {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.82);
        padding: 14px;
      }
      .control-card .helper {
        margin-bottom: 6px;
      }
      .editor-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.8fr);
        gap: 16px;
        margin-top: 16px;
      }
      .note-card {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: linear-gradient(180deg, #faf7f3, #f5f1eb);
        padding: 16px;
      }
      .note-card strong {
        display: block;
        margin-bottom: 8px;
        font-size: 12px;
        letter-spacing: 0.45px;
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
        border: 1px solid rgba(25, 24, 22, 0.12);
        border-radius: 14px;
        padding: 12px 14px;
        background: rgba(255, 255, 255, 0.92);
        color: var(--ink);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
      }
      select:focus,
      input:focus,
      textarea:focus {
        outline: none;
        border-color: rgba(35, 45, 59, 0.28);
        box-shadow: 0 0 0 4px rgba(35, 45, 59, 0.06);
      }
      textarea {
        min-height: 214px;
        max-height: 360px;
        resize: vertical;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 13px;
        line-height: 1.6;
        background: #faf8f5;
      }
      button,
      .link-btn {
        border: 1px solid rgba(25, 24, 22, 0.12);
        border-radius: 14px;
        padding: 11px 15px;
        background: rgba(255, 255, 255, 0.94);
        color: var(--accent);
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease, background 120ms ease;
        box-shadow: 0 6px 18px rgba(20, 22, 25, 0.04);
      }
      button:hover,
      .link-btn:hover {
        transform: translateY(-1px);
        border-color: rgba(35, 45, 59, 0.2);
        background: rgba(255, 255, 255, 1);
      }
      button.primary {
        border-color: transparent;
        background: linear-gradient(180deg, #272d35, #1c2128);
        color: white;
        box-shadow: 0 14px 28px rgba(24, 28, 35, 0.18);
      }
      .pill {
        min-height: 54px;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.9);
        padding: 14px 16px;
      }
      .pill strong {
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.45px;
        margin-right: 6px;
      }
      .button-row.action-row {
        justify-content: flex-start;
        gap: 12px;
      }
      .button-row.action-row button {
        min-width: 124px;
      }
      .service-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .service-metric {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.04);
        padding: 12px 14px;
      }
      .service-metric strong {
        display: block;
        color: rgba(247, 245, 240, 0.5);
        font-size: 11px;
        letter-spacing: 0.45px;
        text-transform: uppercase;
      }
      .service-metric span {
        display: block;
        margin-top: 6px;
        font-size: 15px;
        font-weight: 600;
        line-height: 1.4;
      }
      .link-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .compact-list {
        margin: 0;
        padding-left: 18px;
      }
      .compact-list li + li {
        margin-top: 8px;
      }
      .sidebar .quick-code {
        font-size: 11.5px;
      }
      .json-box header span {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
      }
      .json-grid {
        display: grid;
        grid-template-columns: 1.05fr 0.95fr;
        gap: 16px;
      }
      .json-wide {
        margin-top: 0;
      }
      .json-box {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(251, 249, 246, 0.94);
        overflow: hidden;
        min-width: 0;
        box-shadow: 0 10px 28px rgba(20, 22, 25, 0.04);
      }
      .json-box header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 14px;
        border-bottom: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.8);
      }
      .json-box header strong {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.45px;
      }
      pre {
        margin: 0;
        padding: 16px;
        min-height: 220px;
        max-height: 420px;
        overflow: auto;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 12px;
        line-height: 1.65;
        color: #2d3440;
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
        background: #f1f1ee;
        border-radius: 8px;
        padding: 2px 6px;
        color: var(--accent);
      }
      @media (max-width: 1320px) {
        .layout {
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: static;
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }
      @media (max-width: 1180px) {
        .topbar {
          grid-template-columns: 1fr;
        }
        .hero-grid {
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: static;
          grid-template-columns: 1fr;
        }
        .layout {
          grid-template-columns: 1fr;
        }
        .toolbar,
        .control-grid,
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
          padding: 10px 10px 18px;
        }
        .topbar,
        .layout {
          padding: 14px;
        }
        .topbar {
          gap: 16px;
        }
        .toolbar {
          grid-template-columns: 1fr;
        }
        .status-card {
          min-width: 0;
          width: 100%;
        }
        .runner-head {
          align-items: start;
          flex-direction: column;
        }
        h1 {
          font-size: 36px;
        }
        .headline-sub {
          font-size: 18px;
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
              OpenEnv Console
            </div>
            <div class="headline">
              <h1>
                <span class="headline-mark">TriageOS</span>
                <span class="headline-sub">Enterprise Workflow Console</span>
              </h1>
            </div>
            <p class="subtitle">
              A production-style review surface for enterprise support workflows. Move from
              queue intake to CRM, billing, incident, trust, and policy systems, then inspect
              how each action changes reward, SLA pressure, and downstream operational risk.
            </p>
            <div class="hero-note">
              <span class="chip">Theme 3.1 World Modeling</span>
              <span class="chip">Multi-App Enterprise Workflow</span>
              <span class="chip">Queue-Level Reward Logic</span>
            </div>
            <div class="hero-grid">
              <div class="mini-card">
                <strong>Operating Model</strong>
                <span>Queue -> systems -> outcomes</span>
                <p>Measure routing judgment, escalation quality, and system-aware workflow reasoning in a partially observable enterprise setting.</p>
              </div>
              <div class="mini-card">
                <strong>Review Flow</strong>
                <span>Reset, inspect, execute</span>
                <p>Start a seeded episode, inspect the working state, and step through the workflow while the environment updates in real time.</p>
              </div>
              <div class="mini-card">
                <strong>Audit Surface</strong>
                <span>Typed, visible, reviewable</span>
                <p>Every run keeps raw responses, app snapshots, tool lookups, and schema context visible for direct technical review.</p>
              </div>
            </div>
          </div>
          <div class="status-card">
            <div>
              <strong>Service Status</strong>
              <span id="service-meta">Loading metadata...</span>
              <p>This console is built for review sessions: one environment, one queue, clear state transitions, and traceable reward movement.</p>
            </div>
            <div class="service-grid">
              <div class="service-metric">
                <strong>Mode</strong>
                <span>OpenEnv Runtime</span>
              </div>
              <div class="service-metric">
                <strong>Surface</strong>
                <span>Typed HTTP APIs</span>
              </div>
              <div class="service-metric">
                <strong>Focus</strong>
                <span>Enterprise Workflows</span>
              </div>
              <div class="service-metric">
                <strong>Review</strong>
                <span>Reward + State Trace</span>
              </div>
            </div>
            <ul class="status-list">
              <li><code>Reset</code> loads a fresh seeded scenario.</li>
              <li><code>Suggested Action</code> proposes the next workflow move.</li>
              <li><code>Step</code> updates score, queue health, and world state.</li>
            </ul>
          </div>
        </div>

        <div class="layout">
          <section class="playground">
            <div class="panel runner-panel">
              <div class="runner-head">
                <div class="runner-copy">
                  <span class="section-kicker">Interactive Runner</span>
                  <h2>Operations Desk</h2>
                  <p>Run the environment from a clean control surface, inspect queue-level metrics, and iterate on actions without leaving the page.</p>
                </div>
                <div class="runner-badge">Single-session review console</div>
              </div>
              <div class="summary-grid" style="margin-bottom: 12px;">
                <div class="summary-card"><strong>Task</strong><span class="task-value" id="task-text">billing_refund_easy</span></div>
                <div class="summary-card"><strong>Status</strong><span id="status-text">Ready</span></div>
                <div class="summary-card"><strong>Reward</strong><span class="metric-value" id="reward-text">0.00</span></div>
                <div class="summary-card"><strong>Score</strong><span class="metric-value" id="score-text">0.01</span></div>
                <div class="summary-card"><strong>Steps</strong><span class="metric-value" id="steps-text">0</span></div>
                <div class="summary-card"><strong>Apps</strong><span class="metric-value" id="apps-text">0</span></div>
                <div class="summary-card"><strong>Queue Health</strong><span id="queue-health-text">No queue loaded</span></div>
              </div>
              <div class="control-grid">
                <div class="control-card">
                  <div class="helper">Task Family</div>
                  <select id="task">
                    <option value="billing_refund_easy">billing_refund_easy</option>
                    <option value="export_outage_medium">export_outage_medium</option>
                    <option value="security_and_refund_hard">security_and_refund_hard</option>
                    <option value="enterprise_refund_investigation">enterprise_refund_investigation</option>
                    <option value="incident_coordination_outage">incident_coordination_outage</option>
                    <option value="executive_security_escalation">executive_security_escalation</option>
                  </select>
                </div>
                <div class="control-card">
                  <div class="helper">Seed</div>
                  <input id="seed" type="number" placeholder="Optional" />
                </div>
                <div class="control-card">
                  <div class="helper">Assist</div>
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
                  <strong>Session Notes</strong>
                  <ul>
                    <li><code>Reset</code> starts a fresh seeded episode for the selected task.</li>
                    <li><code>Suggested Action</code> uses real ticket IDs and task-specific workflows.</li>
                    <li><code>Step</code> applies the action and refreshes the environment trace.</li>
                    <li><code>Get State</code> rehydrates the internal environment snapshot.</li>
                    <li><code>App Snapshots</code> and <code>World Summary</code> expose the enterprise context clearly.</li>
                    <li><code>Refresh Schema</code> keeps the OpenEnv contract visible during review.</li>
                  </ul>
                </div>
              </div>

              <div class="button-row action-row" style="margin-top: 12px;">
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
                <header><strong>Response Trace</strong><span id="response-kind">idle</span></header>
                <pre id="response-json">{}</pre>
              </section>
              <section class="json-box">
                <header><strong>Environment State</strong><span id="state-kind">idle</span></header>
                <pre id="state-json">{}</pre>
              </section>
            </div>
            <div class="json-grid" style="margin-top: 14px;">
              <section class="json-box">
                <header><strong>System Snapshots</strong><span id="apps-kind">idle</span></header>
                <pre id="apps-json">[]</pre>
              </section>
              <section class="json-box">
                <header><strong>World Summary</strong><span id="world-kind">idle</span></header>
                <pre id="world-json">[]</pre>
              </section>
            </div>
            <div class="json-grid" style="margin-top: 14px;">
              <section class="json-box">
                <header><strong>Latest Tool Lookup</strong><span id="tool-kind">idle</span></header>
                <pre id="tool-json">{}</pre>
              </section>
              <section class="json-box">
                <header><strong>Schema Surface</strong><span id="schema-kind">loading</span></header>
                <pre id="schema-json">{}</pre>
              </section>
            </div>
          </section>
          <aside class="sidebar">
            <div class="panel overview-card">
              <span class="section-kicker">Run Guide</span>
              <h2>Review Sequence</h2>
              <ol class="compact-list">
                <li>Select a task family and press <code>Reset</code>.</li>
                <li>Read the metric strip and inspect the fresh queue state.</li>
                <li>Use <code>Suggested Action</code> or edit the action JSON directly.</li>
                <li>Advance the workflow with <code>Step</code> until <code>Done</code> is true.</li>
                <li>Inspect the response trace, system snapshots, and world summary.</li>
              </ol>
            </div>

            <div class="panel overview-card">
              <span class="section-kicker">Environment Profile</span>
              <h2>What This Console Covers</h2>
              <div class="chip-row">
                <span class="chip">6 task families</span>
                <span class="chip">Multi-app workflow</span>
                <span class="chip">Deterministic graders</span>
                <span class="chip">Queue-level penalties</span>
                <span class="chip">HTTP simulation</span>
              </div>
              <div class="divider" style="margin: 16px 0;"></div>
              <div class="helper">Task presets</div>
              <div class="chip-row">
                <span class="chip">billing_refund_easy</span>
                <span class="chip">export_outage_medium</span>
                <span class="chip">security_and_refund_hard</span>
                <span class="chip">enterprise_refund_investigation</span>
                <span class="chip">incident_coordination_outage</span>
                <span class="chip">executive_security_escalation</span>
              </div>
            </div>

            <div class="panel overview-card">
              <span class="section-kicker">Developer Access</span>
              <h2>Links And Endpoints</h2>
              <div class="link-grid">
                <a class="link-btn" href="/metadata" target="_blank" rel="noreferrer">Metadata</a>
                <a class="link-btn" href="/schema" target="_blank" rel="noreferrer">Schema</a>
                <a class="link-btn" href="/docs" target="_blank" rel="noreferrer">Docs</a>
                <a class="link-btn" href="/openapi.json" target="_blank" rel="noreferrer">OpenAPI JSON</a>
              </div>
              <div class="divider" style="margin: 16px 0;"></div>
              <div class="helper">Python client</div>
              <div class="quick-code">from support_triage_env import SupportTriageEnv

env = SupportTriageEnv(base_url="https://your-space-url")
await env.connect()</div>
              <div class="helper" style="margin-top: 14px;">Core endpoints</div>
              <div class="quick-code">POST /reset
POST /step
GET  /state
GET  /metadata
GET  /schema</div>
            </div>
          </aside>
        </div>
      </section>
    </main>
    <script>
      const responseJson = document.getElementById("response-json");
      const stateJson = document.getElementById("state-json");
      const appsJson = document.getElementById("apps-json");
      const worldJson = document.getElementById("world-json");
      const toolJson = document.getElementById("tool-json");
      const schemaJson = document.getElementById("schema-json");
      const statusText = document.getElementById("status-text");
      const rewardText = document.getElementById("reward-text");
      const scoreText = document.getElementById("score-text");
      const stepsText = document.getElementById("steps-text");
      const appsText = document.getElementById("apps-text");
      const queueHealthText = document.getElementById("queue-health-text");
      const taskText = document.getElementById("task-text");
      const doneText = document.getElementById("done-text");
      const responseKind = document.getElementById("response-kind");
      const stateKind = document.getElementById("state-kind");
      const appsKind = document.getElementById("apps-kind");
      const worldKind = document.getElementById("world-kind");
      const toolKind = document.getElementById("tool-kind");
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
        if (typeof payload.step_count === "number" || typeof payload.episode_id === "string") {
          return payload;
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

      function summarizeQueueHealth(statePayload) {
        const tickets = statePayload && Array.isArray(statePayload.tickets)
          ? statePayload.tickets
          : [];
        if (!tickets.length) {
          return "No queue loaded";
        }
        const active = tickets.filter((ticket) => !["resolved", "escalated"].includes(ticket.current_status)).length;
        const nearBreach = tickets.filter((ticket) =>
          !["resolved", "escalated"].includes(ticket.current_status) &&
          typeof ticket.sla_hours_remaining === "number" &&
          ticket.sla_hours_remaining <= 2
        ).length;
        const security = tickets.filter((ticket) => {
          const text = `${ticket.subject || ""} ${(ticket.tags || []).join(" ")}`.toLowerCase();
          return text.includes("security") || text.includes("executive") || text.includes("mfa");
        }).length;
        return `${active} active / ${nearBreach} near SLA / ${security} security`;
      }

      function renderWorldPanels(observationPayload, statePayload) {
        const appSnapshots = observationPayload && Array.isArray(observationPayload.app_snapshots)
          ? observationPayload.app_snapshots
          : [];
        const worldSummary = observationPayload && Array.isArray(observationPayload.world_summary)
          ? observationPayload.world_summary
          : statePayload && Array.isArray(statePayload.world_summary)
            ? statePayload.world_summary
            : [];
        const lastToolResult = observationPayload && observationPayload.last_tool_result
          ? observationPayload.last_tool_result
          : statePayload && statePayload.last_tool_result
            ? statePayload.last_tool_result
            : {};
        const accessibleApps = observationPayload && Array.isArray(observationPayload.accessible_apps)
          ? observationPayload.accessible_apps
          : statePayload && Array.isArray(statePayload.accessible_apps)
            ? statePayload.accessible_apps
            : [];

        appsText.textContent = String(accessibleApps.length);
        queueHealthText.textContent = summarizeQueueHealth(statePayload || buildStateFromObservation(observationPayload));
        appsKind.textContent = "apps";
        worldKind.textContent = "world";
        toolKind.textContent = "tool";
        appsJson.textContent = pretty(appSnapshots);
        worldJson.textContent = pretty(worldSummary);
        toolJson.textContent = pretty(lastToolResult);
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
        renderWorldPanels(observationPayload, statePayload);
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
        const combined = `${subject} ${latestMessage} ${((ticket.tags || []).join(" ")).toLowerCase()}`;
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
            priority: combined.includes("enterprise") || combined.includes("month-end") || combined.includes("vip")
              ? "high"
              : "medium",
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
          return "I am sorry this is blocking your work. I have opened an incident and escalated this issue to engineering for investigation. Please share the affected workspace, approximate timestamp, and browser details to help us triage faster.";
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
        return `Escalating ${ticket.ticket_id} for specialist review. Subject: ${ticket.subject}. Include workspace, impact summary, browser, and timestamp in the incident context.`;
      }

      function hasActionBeenTaken(actionType, ticketId) {
        const history = latestState && Array.isArray(latestState.action_history)
          ? latestState.action_history
          : [];
        return history.some((entry) => entry.action_type === actionType && entry.ticket_id === ticketId);
      }

      function buildTaskSpecificAction(taskId, ticket, defaults) {
        if (taskId === "enterprise_refund_investigation") {
          if (!hasActionBeenTaken("lookup_account", ticket.ticket_id)) {
            return {
              action_type: "lookup_account",
              ticket_id: ticket.ticket_id,
              app: "crm_workspace"
            };
          }
          if (!hasActionBeenTaken("check_billing_status", ticket.ticket_id)) {
            return {
              action_type: "check_billing_status",
              ticket_id: ticket.ticket_id,
              app: "billing_system"
            };
          }
          if (!hasActionBeenTaken("search_policy", ticket.ticket_id)) {
            return {
              action_type: "search_policy",
              ticket_id: ticket.ticket_id,
              app: "policy_hub",
              message: "duplicate charge refund workflow"
            };
          }
        }

        if (taskId === "incident_coordination_outage") {
          if (!hasActionBeenTaken("lookup_account", ticket.ticket_id)) {
            return {
              action_type: "lookup_account",
              ticket_id: ticket.ticket_id,
              app: "crm_workspace"
            };
          }
          if (!hasActionBeenTaken("search_policy", ticket.ticket_id)) {
            return {
              action_type: "search_policy",
              ticket_id: ticket.ticket_id,
              app: "policy_hub",
              message: "product outage escalation checklist"
            };
          }
          if (!hasActionBeenTaken("create_incident", ticket.ticket_id)) {
            return {
              action_type: "create_incident",
              ticket_id: ticket.ticket_id,
              app: "incident_tracker",
              team: "engineering",
              severity: "high",
              message: `Workspace outage incident for ${ticket.ticket_id}: ${ticket.subject}`
            };
          }
        }

        if (taskId === "executive_security_escalation") {
          if (!hasActionBeenTaken("lookup_account", ticket.ticket_id)) {
            return {
              action_type: "lookup_account",
              ticket_id: ticket.ticket_id,
              app: "crm_workspace"
            };
          }
          if (!hasActionBeenTaken("search_policy", ticket.ticket_id)) {
            return {
              action_type: "search_policy",
              ticket_id: ticket.ticket_id,
              app: "policy_hub",
              message: "account takeover response policy"
            };
          }
          if (!hasActionBeenTaken("add_internal_note", ticket.ticket_id)) {
            return {
              action_type: "add_internal_note",
              ticket_id: ticket.ticket_id,
              app: "trust_safety_console",
              message: "Executive account with takeover indicators. Keep MFA enabled and route to trust immediately."
            };
          }
        }

        return null;
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
          const taskSpecificAction = buildTaskSpecificAction(taskInput.value, ticket, defaults);
          if (taskSpecificAction) {
            actionInput.value = pretty(taskSpecificAction);
            return;
          }
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
        const parsedState = extractStatePayload(payload);
        latestState = parsedState
          ? { ...(latestState || {}), ...parsedState }
          : latestState;
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
          body: JSON.stringify({ action }),
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
          },
          enterprise_refund_investigation: {
            action_type: "lookup_account",
            ticket_id: "TCK-0000",
            app: "crm_workspace"
          },
          incident_coordination_outage: {
            action_type: "create_incident",
            ticket_id: "TCK-0000",
            app: "incident_tracker",
            team: "engineering",
            severity: "high",
            message: "Workspace outage incident for enterprise reporting."
          },
          executive_security_escalation: {
            action_type: "add_internal_note",
            ticket_id: "TCK-0000",
            app: "trust_safety_console",
            message: "Executive account with takeover indicators. Escalate to trust immediately."
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
