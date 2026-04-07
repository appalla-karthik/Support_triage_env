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
        --card: #fffdf8;
        --ink: #17313a;
        --muted: #4e6a73;
        --accent: #245567;
        --line: #d9e3e7;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Segoe UI", Arial, sans-serif;
        background:
          radial-gradient(circle at top right, #dcecf1 0, transparent 26%),
          radial-gradient(circle at top left, #f3d8b0 0, transparent 24%),
          var(--bg);
        color: var(--ink);
      }
      main {
        max-width: 960px;
        margin: 48px auto;
        padding: 0 24px;
      }
      .card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: 0 18px 40px rgba(23, 49, 58, 0.08);
        padding: 32px;
      }
      h1 {
        margin: 0 0 12px;
        font-size: 40px;
        line-height: 1.05;
      }
      p {
        color: var(--muted);
        font-size: 18px;
        line-height: 1.6;
      }
      .chips, .links {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
      }
      .chip, a {
        border-radius: 999px;
        text-decoration: none;
      }
      .chip {
        background: #e7f0f4;
        color: var(--accent);
        padding: 10px 14px;
        font-size: 14px;
        font-weight: 700;
      }
      a {
        background: var(--accent);
        color: white;
        padding: 12px 18px;
        font-weight: 700;
      }
      a.secondary {
        background: transparent;
        color: var(--accent);
        border: 1px solid var(--line);
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-top: 28px;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 18px;
        background: white;
      }
      .panel h2 {
        margin: 0 0 10px;
        font-size: 18px;
      }
      .panel ul {
        margin: 0;
        padding-left: 18px;
        color: var(--muted);
        line-height: 1.6;
      }
      code {
        background: #eef4f6;
        border-radius: 8px;
        padding: 2px 6px;
        color: var(--accent);
      }
    </style>
  </head>
  <body>
    <main>
      <section class="card">
        <h1>Support Triage Environment</h1>
        <p>
          A real-world OpenEnv customer support simulator for classifying,
          prioritizing, replying to, escalating, and resolving support tickets
          under deterministic graders with shaped rewards.
        </p>
        <div class="chips">
          <span class="chip">OpenEnv Simulation</span>
          <span class="chip">3 Tasks</span>
          <span class="chip">Deterministic Graders</span>
          <span class="chip">Shaped Rewards</span>
        </div>
        <div class="links">
          <a href="/metadata">Metadata</a>
          <a href="/schema">Schema</a>
          <a href="/docs" class="secondary">OpenAPI Docs</a>
          <a href="/openapi.json" class="secondary">OpenAPI JSON</a>
        </div>
        <div class="grid">
          <article class="panel">
            <h2>Core Endpoints</h2>
            <ul>
              <li><code>/reset</code></li>
              <li><code>/step</code></li>
              <li><code>/state</code></li>
              <li><code>/metadata</code></li>
              <li><code>/schema</code></li>
            </ul>
          </article>
          <article class="panel">
            <h2>Included Tasks</h2>
            <ul>
              <li>billing_refund_easy</li>
              <li>export_outage_medium</li>
              <li>security_and_refund_hard</li>
            </ul>
          </article>
          <article class="panel">
            <h2>Expected Workflow</h2>
            <ul>
              <li>View or classify tickets</li>
              <li>Draft safe customer replies</li>
              <li>Escalate product or security issues</li>
              <li>Resolve only when appropriate</li>
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

