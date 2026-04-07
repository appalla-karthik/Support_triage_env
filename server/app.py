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
        --bg: #f4f6f7;
        --bg-mesh-a: rgba(90, 128, 148, 0.10);
        --bg-mesh-b: rgba(207, 180, 139, 0.12);
        --card: rgba(255, 255, 255, 0.94);
        --card-strong: #ffffff;
        --ink: #16303d;
        --muted: #647987;
        --accent: #234d63;
        --accent-soft: #e7eff3;
        --line: rgba(35, 77, 99, 0.10);
        --success: #2b7a63;
        --shadow: 0 20px 44px rgba(22, 48, 61, 0.08);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Aptos", "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
        background:
          radial-gradient(circle at 10% 10%, var(--bg-mesh-b) 0, transparent 24%),
          radial-gradient(circle at 88% 12%, var(--bg-mesh-a) 0, transparent 22%),
          radial-gradient(circle at 82% 88%, rgba(139, 165, 176, 0.08) 0, transparent 24%),
          var(--bg);
        color: var(--ink);
      }
      main {
        max-width: 1080px;
        margin: 28px auto;
        padding: 0 18px 24px;
      }
      .card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 28px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(12px);
        padding: 24px;
      }
      .hero {
        display: grid;
        grid-template-columns: 1.5fr 0.9fr;
        gap: 16px;
        align-items: stretch;
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 14px;
        border-radius: 999px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 0.32px;
        text-transform: uppercase;
      }
      .status-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 0 6px rgba(42, 124, 96, 0.12);
      }
      h1 {
        margin: 14px 0 10px;
        font-size: 40px;
        line-height: 1.06;
        letter-spacing: -0.8px;
      }
      p {
        color: var(--muted);
        font-size: 17px;
        line-height: 1.58;
      }
      .lead {
        max-width: 720px;
        margin: 0;
        font-size: 16px;
      }
      .chips, .links {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 18px;
      }
      .chip, a {
        border-radius: 999px;
        text-decoration: none;
      }
      .chip {
        background: #e8f1f4;
        color: var(--accent);
        padding: 10px 14px;
        font-size: 14px;
        font-weight: 700;
      }
      a {
        background: linear-gradient(135deg, #1f5a6d, #2f6f83);
        color: white;
        padding: 11px 17px;
        font-weight: 700;
        box-shadow: 0 12px 28px rgba(31, 90, 109, 0.18);
      }
      a.secondary {
        background: rgba(255, 255, 255, 0.58);
        color: var(--accent);
        border: 1px solid var(--line);
        box-shadow: none;
      }
      .stats {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
      }
      .stat {
        background: var(--card-strong);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 14px;
      }
      .stat .label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .stat .value {
        margin-top: 6px;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.8px;
      }
      .stat .note {
        margin-top: 6px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.45;
      }
      .section-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 14px;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px;
        background: rgba(255, 255, 255, 0.76);
      }
      .panel h2 {
        margin: 0 0 10px;
        font-size: 18px;
        letter-spacing: -0.3px;
      }
      .panel ul {
        margin: 0;
        padding-left: 18px;
        color: var(--muted);
        line-height: 1.55;
        font-size: 15px;
      }
      .panel li + li {
        margin-top: 6px;
      }
      .meta-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin-top: 14px;
      }
      .meta-item {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 12px 14px;
      }
      .meta-item strong {
        display: block;
        font-size: 14px;
        color: var(--muted);
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.45px;
      }
      .meta-item span {
        font-size: 15px;
        font-weight: 700;
      }
      code {
        background: #eef4f6;
        border-radius: 8px;
        padding: 2px 6px;
        color: var(--accent);
      }
      @media (max-width: 980px) {
        .hero,
        .section-grid,
        .meta-strip {
          grid-template-columns: 1fr;
        }
        .stats {
          grid-template-columns: 1fr 1fr;
        }
        h1 {
          font-size: 42px;
        }
      }
      @media (max-width: 640px) {
        main {
          padding: 0 14px 28px;
        }
        .card {
          padding: 20px;
          border-radius: 22px;
        }
        .stats {
          grid-template-columns: 1fr;
        }
        h1 {
          font-size: 34px;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <section class="card">
        <div class="hero">
          <div>
            <div class="eyebrow">
              <span class="status-dot"></span>
              OpenEnv Environment Live
            </div>
            <h1>Support Triage Environment</h1>
            <p class="lead">
              A real-world customer support simulator for agents that classify,
              prioritize, reply, escalate, and resolve tickets under deterministic
              graders with shaped rewards.
            </p>
            <div class="chips">
              <span class="chip">Customer Support Operations</span>
              <span class="chip">Easy to Hard Tasks</span>
              <span class="chip">Deterministic Graders</span>
              <span class="chip">Reward Shaping</span>
            </div>
            <div class="links">
              <a href="/metadata">Metadata</a>
              <a href="/schema">Schema</a>
              <a href="/docs" class="secondary">OpenAPI Docs</a>
              <a href="/openapi.json" class="secondary">OpenAPI JSON</a>
            </div>
          </div>
          <div class="stats">
            <article class="stat">
              <div class="label">Tasks</div>
              <div class="value">3</div>
              <div class="note">Easy, medium, and hard workflows with deterministic scoring.</div>
            </article>
            <article class="stat">
              <div class="label">HTTP Surface</div>
              <div class="value">OpenEnv</div>
              <div class="note">Typed endpoints for reset, step, state, metadata, and schema.</div>
            </article>
            <article class="stat">
              <div class="label">Primary Objective</div>
              <div class="value">Safe Triage</div>
              <div class="note">Rewards compliant replies, correct routing, and thoughtful escalation.</div>
            </article>
            <article class="stat">
              <div class="label">Deployment</div>
              <div class="value">Docker</div>
              <div class="note">Containerized for Hugging Face Spaces and OpenEnv validation.</div>
            </article>
          </div>
        </div>

        <div class="meta-strip">
          <div class="meta-item">
            <strong>Status</strong>
            <span>Running</span>
          </div>
          <div class="meta-item">
            <strong>Environment</strong>
            <span>support_triage_env</span>
          </div>
          <div class="meta-item">
            <strong>API Pattern</strong>
            <span>reset / step / state</span>
          </div>
          <div class="meta-item">
            <strong>Intended Use</strong>
            <span>Agent Evaluation & Training</span>
          </div>
        </div>

        <div class="section-grid">
          <article class="panel">
            <h2>Core Endpoints</h2>
            <ul>
              <li><code>/reset</code> starts a new episode</li>
              <li><code>/step</code> applies the next agent action</li>
              <li><code>/state</code> exposes current environment state</li>
              <li><code>/metadata</code> and <code>/schema</code> describe the environment</li>
            </ul>
          </article>
          <article class="panel">
            <h2>Included Tasks</h2>
            <ul>
              <li><strong>billing_refund_easy</strong>: duplicate-charge refund handling</li>
              <li><strong>export_outage_medium</strong>: engineering escalation for reporting outage</li>
              <li><strong>security_and_refund_hard</strong>: urgent security triage before billing work</li>
            </ul>
          </article>
          <article class="panel">
            <h2>Evaluation Focus</h2>
            <ul>
              <li>Correct category, priority, and routing</li>
              <li>Customer-safe, policy-compliant replies</li>
              <li>Partial-credit rewards across the full trajectory</li>
              <li>Penalties for unsafe or repeated actions</li>
            </ul>
          </article>
        </div>
      </section>
    </main>
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

