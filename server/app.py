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
        --card: rgba(255, 255, 255, 0.96);
        --card-strong: #ffffff;
        --ink: #142f3b;
        --muted: #617887;
        --accent: #1f4c61;
        --accent-soft: #e7f0f4;
        --line: rgba(31, 76, 97, 0.11);
        --success: #2d7a61;
        --shadow: 0 18px 46px rgba(20, 47, 59, 0.08);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
        background:
          radial-gradient(circle at 10% 10%, rgba(204, 182, 145, 0.10) 0, transparent 22%),
          radial-gradient(circle at 88% 12%, rgba(111, 151, 168, 0.08) 0, transparent 22%),
          #f4f6f8;
        color: var(--ink);
      }
      main {
        width: calc(100% - 32px);
        max-width: 1440px;
        margin: 16px auto;
        padding: 0 0 20px;
      }
      .shell {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: var(--shadow);
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
        gap: 14px;
        padding: 14px;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 16px;
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
        gap: 14px;
      }
      .toolbar {
        display: grid;
        grid-template-columns: 1fr 120px 140px;
        gap: 9px;
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
        min-height: 168px;
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
      .status-line {
        display: grid;
        grid-template-columns: 1fr 0.8fr 0.7fr;
        gap: 9px;
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
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }
      .json-box {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #f7fafb;
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
        min-height: 260px;
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
        .status-line {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 720px) {
        main {
          width: calc(100% - 20px);
          padding: 0 0 18px;
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
              <p>Connect from Python or use the browser-side playground to inspect reset, step, state, metadata, and schema responses.</p>
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
          </aside>

          <section class="playground">
            <div class="panel">
              <h2>Playground</h2>
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
                  <button id="fill-sample" type="button">Sample Action</button>
                </div>
              </div>

              <div style="margin-top: 12px;">
                <label for="action-json">Action JSON</label>
                <textarea id="action-json">{
  "action_type": "classify_ticket",
  "ticket_id": "TCK-0000",
  "category": "billing_refund",
  "priority": "medium",
  "team": "billing_ops"
}</textarea>
              </div>

              <div class="button-row" style="margin-top: 12px;">
                <button class="primary" id="reset-btn" type="button">Reset</button>
                <button class="primary" id="step-btn" type="button">Step</button>
                <button id="state-btn" type="button">Get State</button>
                <button id="schema-btn" type="button">Refresh Schema</button>
              </div>

              <div class="status-line" style="margin-top: 12px;">
                <div class="pill"><strong>Status</strong><span id="status-text">Ready</span></div>
                <div class="pill"><strong>Reward</strong><span id="reward-text">-</span></div>
                <div class="pill"><strong>Done</strong><span id="done-text">false</span></div>
              </div>
            </div>

            <div class="json-grid">
              <section class="json-box">
                <header><strong>Latest Response</strong><span id="response-kind">idle</span></header>
                <pre id="response-json">{}</pre>
              </section>
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
      const schemaJson = document.getElementById("schema-json");
      const statusText = document.getElementById("status-text");
      const rewardText = document.getElementById("reward-text");
      const doneText = document.getElementById("done-text");
      const responseKind = document.getElementById("response-kind");
      const schemaKind = document.getElementById("schema-kind");
      const taskInput = document.getElementById("task");
      const seedInput = document.getElementById("seed");
      const actionInput = document.getElementById("action-json");
      const serviceMeta = document.getElementById("service-meta");

      function pretty(data) {
        return JSON.stringify(data, null, 2);
      }

      function setStatus(text) {
        statusText.textContent = text;
      }

      function setStepInfo(payload) {
        rewardText.textContent = payload.reward == null ? "-" : String(payload.reward);
        doneText.textContent = String(Boolean(payload.done));
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
        responseKind.textContent = "reset";
        responseJson.textContent = pretty(payload);
        setStepInfo(payload);
        setStatus(response.ok ? "Episode reset successfully" : "Reset failed");
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
        responseKind.textContent = "step";
        responseJson.textContent = pretty(payload);
        setStepInfo(payload);
        setStatus(response.ok ? "Action executed" : "Step request failed");
      }

      async function getState() {
        setStatus("Fetching current state...");
        const response = await fetch("/state");
        const payload = await response.json();
        responseKind.textContent = "state";
        responseJson.textContent = pretty(payload);
        setStatus(response.ok ? "State loaded" : "State request failed");
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
      document.getElementById("fill-sample").addEventListener("click", fillSample);
      taskInput.addEventListener("change", fillSample);

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
