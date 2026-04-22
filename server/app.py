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
        --shadow: 0 16px 40px rgba(20, 22, 25, 0.06);
        --shadow-soft: 0 6px 20px rgba(20, 22, 25, 0.04);
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
        background: rgba(255, 255, 255, 0.84);
        border: 1px solid rgba(255, 255, 255, 0.65);
        border-radius: 28px;
        box-shadow: var(--shadow);
        overflow: hidden;
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
        box-shadow: 0 0 0 3px rgba(47, 111, 85, 0.1);
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
        box-shadow: 0 12px 30px rgba(21, 24, 31, 0.14);
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
        box-shadow: 0 4px 14px rgba(20, 22, 25, 0.035);
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
        box-shadow: none;
      }
      select:focus,
      input:focus,
      textarea:focus {
        outline: none;
        border-color: rgba(35, 45, 59, 0.28);
        box-shadow: 0 0 0 3px rgba(35, 45, 59, 0.05);
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
        box-shadow: 0 3px 10px rgba(20, 22, 25, 0.035);
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
        box-shadow: 0 10px 22px rgba(24, 28, 35, 0.14);
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
      .banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin: 14px 0 0;
        padding: 12px 14px;
        border-radius: 18px;
        border: 1px solid rgba(153, 103, 48, 0.22);
        background: rgba(154, 103, 48, 0.08);
        color: #3d2b13;
      }
      .banner strong {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.45px;
        color: rgba(61, 43, 19, 0.78);
      }
      .banner span {
        font-size: 13px;
        line-height: 1.55;
        color: rgba(61, 43, 19, 0.92);
      }
      .banner .hint {
        margin-left: auto;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.25px;
        color: rgba(61, 43, 19, 0.72);
        white-space: nowrap;
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
        box-shadow: 0 4px 14px rgba(20, 22, 25, 0.035);
        contain: layout paint;
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
      .conversation-panel {
        position: relative;
        margin: 0 0 16px;
        padding: 24px 24px 22px;
        background:
          radial-gradient(circle at top left, rgba(108, 130, 160, 0.22), transparent 28%),
          radial-gradient(circle at right center, rgba(66, 82, 108, 0.18), transparent 32%),
          linear-gradient(180deg, #1f2733 0%, #171e29 100%);
        border: 1px solid rgba(23, 30, 41, 0.26);
        color: #f6f5f1;
        overflow: hidden;
        box-shadow: 0 18px 38px rgba(18, 24, 33, 0.14);
      }
      .conversation-panel::before {
        content: "";
        position: absolute;
        inset: 0 auto auto 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.02), rgba(151, 182, 220, 0.34), rgba(255, 255, 255, 0.02));
      }
      .conversation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
      }
      .conversation-controls {
        display: grid;
        gap: 10px;
        justify-items: end;
        min-width: 260px;
      }
      .conversation-control-row {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: flex-end;
      }
      .conversation-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.45px;
        text-transform: uppercase;
        color: rgba(200, 213, 228, 0.78);
      }
      .conversation-select {
        appearance: none;
        border-radius: 999px;
        padding: 9px 34px 9px 14px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        background: rgba(255, 255, 255, 0.06);
        color: rgba(246, 245, 241, 0.92);
        color-scheme: dark;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.15px;
        cursor: pointer;
        max-width: 340px;
      }
      .conversation-select:disabled {
        /* Keep our styling even when disabled (some browsers wash selects to white/grey). */
        opacity: 1;
        background: rgba(0, 0, 0, 0.18);
        color: rgba(246, 245, 241, 0.72);
        -webkit-text-fill-color: rgba(246, 245, 241, 0.72);
        cursor: not-allowed;
      }
      .conversation-select option {
        background: #121825;
        color: rgba(246, 245, 241, 0.92);
      }
      .conversation-select-wrap {
        position: relative;
        display: inline-flex;
        align-items: center;
      }
      .conversation-select-wrap::after {
        /* CSS triangle to avoid unicode/encoding issues in some terminals/editors. */
        content: "";
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid rgba(246, 245, 241, 0.7);
        pointer-events: none;
      }
      .follow-toggle {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.05);
        color: rgba(246, 245, 241, 0.88);
        font-size: 12px;
        font-weight: 600;
        user-select: none;
      }
      .follow-toggle input {
        accent-color: #cfe0f4;
      }
      .conversation-header .section-kicker {
        color: rgba(200, 213, 228, 0.74);
      }
      .conversation-chip {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 999px;
        padding: 9px 14px;
        background: rgba(255, 255, 255, 0.06);
        color: rgba(246, 245, 241, 0.9);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.2px;
      }
      .conversation-stream {
        display: grid;
        gap: 14px;
      }
      .message-row {
        display: grid;
        grid-template-columns: 48px minmax(0, 1fr);
        gap: 16px;
        align-items: start;
      }
      .message-row.agent {
        grid-template-columns: minmax(0, 1fr) 48px;
      }
      .message-row.agent .message-stack {
        display: grid;
        justify-items: end;
      }
      .message-row.agent .message-meta {
        justify-content: flex-end;
      }
      .message-row.agent .chat-bubble {
        background:
          linear-gradient(180deg, rgba(244, 247, 251, 0.98), rgba(233, 239, 246, 0.98));
        border-color: rgba(143, 162, 186, 0.34);
        box-shadow:
          0 14px 30px rgba(8, 12, 20, 0.1),
          inset 0 1px 0 rgba(255, 255, 255, 0.86);
      }
      .message-row.agent .chat-bubble p {
        color: #233043;
      }
      .message-row.agent .message-avatar {
        background: linear-gradient(180deg, rgba(133, 158, 189, 0.26), rgba(102, 122, 149, 0.18));
        color: #eaf1f8;
      }
      .message-row.agent .message-role {
        color: rgba(220, 229, 239, 0.82);
      }
      .message-row.agent .message-ticket {
        color: rgba(177, 193, 212, 0.88);
      }
      .message-avatar {
        width: 48px;
        height: 48px;
        border-radius: 16px;
        display: grid;
        place-items: center;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.04));
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #f6f5f1;
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 0.4px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
      }
      .message-meta {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
      }
      .message-role {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.55px;
        text-transform: uppercase;
        color: rgba(223, 231, 241, 0.92);
      }
      .message-ticket {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        color: rgba(166, 184, 204, 0.9);
      }
      .chat-bubble {
        width: fit-content;
        max-width: min(920px, 100%);
        padding: 18px 20px;
        border-radius: 20px;
        border: 1px solid rgba(114, 142, 178, 0.26);
        background:
          linear-gradient(180deg, rgba(30, 43, 64, 0.96), rgba(24, 35, 54, 0.9));
        box-shadow:
          0 14px 30px rgba(8, 12, 20, 0.16),
          inset 0 1px 0 rgba(255, 255, 255, 0.05);
      }
      .chat-bubble p {
        margin: 0;
        color: #f6f5f1;
        font-size: 16px;
        line-height: 1.72;
        letter-spacing: -0.1px;
      }
      .chat-bubble.empty {
        border-style: dashed;
        border-color: rgba(255, 255, 255, 0.14);
        background: rgba(255, 255, 255, 0.04);
        color: rgba(246, 245, 241, 0.72);
      }
      .chat-bubble.empty p {
        color: rgba(246, 245, 241, 0.72);
      }
      .conversation-caption {
        margin: 0 0 4px;
        color: rgba(200, 213, 228, 0.72);
        font-size: 13px;
        line-height: 1.7;
        max-width: 760px;
      }
      .activity-panel {
        margin-top: 18px;
        padding-top: 18px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
      }
      .activity-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
      }
      .activity-head strong {
        color: rgba(243, 246, 250, 0.94);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .activity-head span {
        color: rgba(187, 201, 218, 0.84);
        font-size: 12px;
      }
      .activity-list {
        display: grid;
        gap: 10px;
        max-height: 420px;
        overflow: auto;
        padding-right: 6px;
        overscroll-behavior: contain;
      }
      .activity-item {
        display: grid;
        grid-template-columns: 78px minmax(0, 1fr);
        gap: 12px;
        align-items: start;
        padding: 12px 14px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.06);
      }
      .activity-step {
        color: rgba(156, 190, 229, 0.92);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.45px;
        text-transform: uppercase;
      }
      .activity-body strong {
        display: block;
        color: #f5f7fa;
        font-size: 14px;
        line-height: 1.45;
      }
      .activity-body p {
        margin: 6px 0 0;
        color: rgba(204, 216, 231, 0.82);
        font-size: 13px;
        line-height: 1.65;
      }
      .activity-item.done {
        background: rgba(57, 110, 84, 0.18);
        border-color: rgba(89, 164, 125, 0.26);
      }
      .activity-item.reply {
        background: rgba(84, 108, 145, 0.16);
        border-color: rgba(114, 142, 178, 0.24);
      }
      .activity-empty {
        padding: 14px 16px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px dashed rgba(255, 255, 255, 0.12);
        color: rgba(204, 216, 231, 0.78);
        font-size: 13px;
        line-height: 1.7;
      }
      pre {
        margin: 0;
        padding: 16px;
        min-height: 200px;
        max-height: 360px;
        overflow: auto;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        font-family: Consolas, "SFMono-Regular", monospace;
        font-size: 12px;
        line-height: 1.65;
        color: #2d3440;
        contain: content;
        overscroll-behavior: contain;
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
            <section class="panel conversation-panel">
              <div class="conversation-header">
                <div>
                  <span class="section-kicker">Customer Message</span>
                  <h2 style="margin: 8px 0 8px; color: #f6f5f1;">Conversation Surface</h2>
                  <p class="conversation-caption">Keep the customer voice visible while you inspect state, rewards, and tool results. The panel follows the focused ticket and keeps the latest inbound message front and center.</p>
                </div>
                <div class="conversation-controls">
                  <div class="conversation-control-row">
                    <span class="conversation-label">Viewing</span>
                    <span class="conversation-chip" id="conversation-ticket">No focused ticket</span>
                  </div>
                  <div class="conversation-control-row">
                    <label class="follow-toggle" title="When enabled, the conversation panel follows the ticket touched by the most recent action.">
                      <input id="follow-focus" type="checkbox" checked />
                      Follow focused ticket
                    </label>
                    <span class="conversation-select-wrap" title="Pin the conversation panel to a specific ticket. Disable 'Follow focused ticket' to lock this selection.">
                      <select class="conversation-select" id="conversation-ticket-select" disabled>
                        <option value="">No tickets</option>
                      </select>
                    </span>
                  </div>
                </div>
              </div>
              <div class="conversation-stream">
                <article class="message-row">
                  <div class="message-avatar" aria-hidden="true">CS</div>
                  <div>
                    <div class="message-meta">
                      <span class="message-role" id="customer-role">Customer</span>
                      <span class="message-ticket" id="customer-meta">Waiting for a queue reset</span>
                    </div>
                    <div class="chat-bubble empty" id="customer-bubble">
                      <p id="customer-message">The latest customer message will appear here once an episode is loaded.</p>
                    </div>
                  </div>
                </article>
                <article class="message-row agent">
                  <div class="message-stack">
                    <div class="message-meta">
                      <span class="message-ticket" id="agent-meta">Reply will appear after draft or request actions</span>
                      <span class="message-role" id="agent-role">Agent Reply</span>
                    </div>
                    <div class="chat-bubble empty" id="agent-bubble">
                      <p id="agent-message">The environment will show the latest outbound reply here once the agent drafts a response.</p>
                    </div>
                  </div>
                  <div class="message-avatar" aria-hidden="true">AI</div>
                </article>
              </div>
              <div class="activity-panel">
                <div class="activity-head">
                  <strong>Step Narrative</strong>
                  <span id="activity-summary">Reset the environment to begin.</span>
                </div>
                <div class="activity-list" id="activity-list">
                  <div class="activity-empty">Step-by-step explanation will appear here. You will see what happened on reset, what each action changed, when a reply was drafted, and what `done = true` means for the episode.</div>
                </div>
              </div>
            </section>

            <div class="panel runner-panel">
              <div class="runner-head">
                <div class="runner-copy">
                  <span class="section-kicker">Interactive Runner</span>
                  <h2>Operations Desk</h2>
                  <p>Run the environment from a clean control surface, inspect queue-level metrics, and iterate on actions without leaving the page.</p>
                </div>
                <div class="runner-badge">Single-session review console</div>
              </div>
              <div class="banner" id="reset-required-banner" hidden>
                <div>
                  <strong>Task Changed</strong>
                  <span>Press <code>Reset</code> to start a new episode before stepping.</span>
                </div>
                <div class="hint">Reset required</div>
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
                    <option value="escalation_rejection_recovery">escalation_rejection_recovery</option>
                    <option value="refund_reopen_review">refund_reopen_review</option>
                    <option value="mixed_queue_command_center">mixed_queue_command_center</option>
                    <option value="followup_reprioritization_queue">followup_reprioritization_queue</option>
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
                <span class="chip">10 task families</span>
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
                <span class="chip">escalation_rejection_recovery</span>
                <span class="chip">refund_reopen_review</span>
                <span class="chip">mixed_queue_command_center</span>
                <span class="chip">followup_reprioritization_queue</span>
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
      const customerRole = document.getElementById("customer-role");
      const customerMeta = document.getElementById("customer-meta");
      const customerBubble = document.getElementById("customer-bubble");
      const customerMessage = document.getElementById("customer-message");
      const conversationTicket = document.getElementById("conversation-ticket");
      const agentRole = document.getElementById("agent-role");
      const agentMeta = document.getElementById("agent-meta");
      const agentBubble = document.getElementById("agent-bubble");
      const agentMessage = document.getElementById("agent-message");
      const activitySummary = document.getElementById("activity-summary");
      const activityList = document.getElementById("activity-list");
      const followFocusToggle = document.getElementById("follow-focus");
      const conversationTicketSelect = document.getElementById("conversation-ticket-select");
      const resetRequiredBanner = document.getElementById("reset-required-banner");
      const stepBtn = document.getElementById("step-btn");
      const suggestedBtn = document.getElementById("fill-sample");
        const jsonCache = new WeakMap();
        let latestState = null;
        let latestObservation = null;
        let latestResult = null;
        let activityEntries = [];
        let resetRequired = false;
        let episodeDone = false;
        let activeEpisodeTaskId = "";
        let followFocusedTicket = true;
        let pinnedTicketId = "";

        function pretty(data) {
          return JSON.stringify(data, null, 2);
        }

        function setFormattedContent(element, data) {
          const text = pretty(data);
          if (jsonCache.get(element) !== text) {
            element.textContent = text;
            jsonCache.set(element, text);
          }
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
            messages: ticket.latest_customer_message
              ? [{ role: "customer", content: ticket.latest_customer_message }]
              : [],
            outbound_messages: [],
            internal_notes: [],
            requested_information: [],
            tags: ticket.tags || [],
          })),
          progress: observationPayload.progress || null,
          step_count: 0,
          action_history: [],
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

      function findFocusedTicket(observationPayload, statePayload) {
        const observationFocused = observationPayload && observationPayload.focused_ticket;
        if (observationFocused && typeof observationFocused === "object") {
          return observationFocused;
        }

        const focusedTicketId = statePayload && statePayload.focused_ticket_id;
        const workingTickets = statePayload && Array.isArray(statePayload.tickets)
          ? statePayload.tickets
          : observationPayload && Array.isArray(observationPayload.queue)
            ? observationPayload.queue
            : [];
        if (focusedTicketId) {
          const focused = workingTickets.find((ticket) => ticket.ticket_id === focusedTicketId);
          if (focused) {
            return focused;
          }
        }
        return workingTickets.length ? workingTickets[0] : null;
      }

      function getWorkingTicketsFromPayloads(observationPayload, statePayload) {
        if (statePayload && Array.isArray(statePayload.tickets) && statePayload.tickets.length) {
          return statePayload.tickets;
        }
        if (observationPayload && Array.isArray(observationPayload.queue) && observationPayload.queue.length) {
          return observationPayload.queue;
        }
        return [];
      }

      function findTicketById(tickets, ticketId) {
        if (!ticketId) {
          return null;
        }
        return tickets.find((ticket) => ticket && ticket.ticket_id === ticketId) || null;
      }

      function updateConversationSelector(tickets, focusedTicketId) {
        if (!conversationTicketSelect) {
          return;
        }
        const optionsSignature = tickets.map((ticket) => ticket.ticket_id).join("|");
        const currentSignature = conversationTicketSelect.getAttribute("data-signature") || "";
        if (optionsSignature !== currentSignature) {
          conversationTicketSelect.setAttribute("data-signature", optionsSignature);
          conversationTicketSelect.innerHTML = tickets.length
            ? tickets.map((ticket) => {
                const label = ticket.subject ? `${ticket.ticket_id} - ${ticket.subject}` : ticket.ticket_id;
                return `<option value="${ticket.ticket_id}">${label}</option>`;
              }).join("")
            : '<option value="">No tickets</option>';
        }

        const hasTickets = tickets.length > 0;
        conversationTicketSelect.disabled = !hasTickets || followFocusedTicket;
        if (followFocusedTicket) {
          pinnedTicketId = focusedTicketId || (hasTickets ? tickets[0].ticket_id : "");
        }
        if (pinnedTicketId && conversationTicketSelect.value !== pinnedTicketId) {
          conversationTicketSelect.value = pinnedTicketId;
        }
      }

      function latestCustomerMessage(ticket) {
        if (!ticket || !Array.isArray(ticket.messages)) {
          return ticket && typeof ticket.latest_customer_message === "string"
            ? ticket.latest_customer_message
            : "";
        }
        for (let index = ticket.messages.length - 1; index >= 0; index -= 1) {
          const message = ticket.messages[index];
          if (message && message.role === "customer" && message.content) {
            return message.content;
          }
        }
        return typeof ticket.latest_customer_message === "string" ? ticket.latest_customer_message : "";
      }

      function latestAgentMessage(ticket) {
        if (!ticket) {
          return "";
        }
        if (Array.isArray(ticket.messages)) {
          for (let index = ticket.messages.length - 1; index >= 0; index -= 1) {
            const message = ticket.messages[index];
            if (message && message.role === "agent" && message.content) {
              return message.content;
            }
          }
        }
        if (Array.isArray(ticket.outbound_messages) && ticket.outbound_messages.length > 0) {
          const latest = ticket.outbound_messages[ticket.outbound_messages.length - 1];
          return typeof latest === "string" ? latest : "";
        }
        return "";
      }

      function actionLabel(actionType) {
        if (!actionType) {
          return "Action";
        }
        return actionType.replaceAll("_", " ");
      }

      function describeCompletion(observationPayload, statePayload) {
        const progress = observationPayload && observationPayload.progress
          ? observationPayload.progress
          : statePayload && statePayload.progress
            ? statePayload.progress
            : null;
        const score = progress && progress.score != null ? Number(progress.score) : null;
        if (score != null && Number.isFinite(score)) {
          return `Episode complete. Final score is ${score.toFixed(2)} and no more actions are required unless you want to inspect the final state.`;
        }
        return "Episode complete. The environment considers the workflow finished, so further actions are not needed.";
      }

      function currentTicketStatus(ticket) {
        return ticket && ticket.current_status ? String(ticket.current_status).replaceAll("_", " ") : "updated";
      }

      function normalizeActionType(value) {
        if (!value) {
          return "";
        }
        if (typeof value === "string") {
          return value;
        }
        if (typeof value === "object") {
          if (typeof value.value === "string") return value.value;
          if (typeof value._value_ === "string") return value._value_;
          if (typeof value.name === "string") return value.name;
        }
        return String(value);
      }

      function wasRepeatedAction(statePayload, action) {
        const history = statePayload && Array.isArray(statePayload.action_history)
          ? statePayload.action_history
          : [];
        if (history.length < 2 || !action) {
          return false;
        }
        const latest = history[history.length - 1];
        const previous = history[history.length - 2];
        return latest && previous &&
          latest.action_type === previous.action_type &&
          latest.ticket_id === previous.ticket_id &&
          latest.action_type === action.action_type &&
          latest.ticket_id === action.ticket_id;
      }

      function pushActivityEntry(entry) {
        activityEntries = [entry, ...activityEntries];
        if (activityEntries.length > 200) {
          activityEntries.length = 200;
        }
      }

      function renderActivityFeed() {
        activitySummary.textContent = activityEntries.length
          ? `${activityEntries[0].stepLabel} captured. Latest environment transition is shown first.`
          : "Reset the environment to begin.";

        if (!activityEntries.length) {
          activityList.innerHTML = '<div class="activity-empty">Step-by-step explanation will appear here. You will see what happened on reset, what each action changed, when a reply was drafted, and what `done = true` means for the episode.</div>';
          return;
        }

        activityList.innerHTML = activityEntries.map((entry) => `
          <article class="activity-item ${entry.kind}">
            <div class="activity-step">${entry.stepLabel}</div>
            <div class="activity-body">
              <strong>${entry.title}</strong>
              <p>${entry.detail}</p>
            </div>
          </article>
        `).join("");
      }

      function recordResetActivity(observationPayload, statePayload) {
        const queueSize = observationPayload && Array.isArray(observationPayload.queue)
          ? observationPayload.queue.length
          : statePayload && Array.isArray(statePayload.tickets)
            ? statePayload.tickets.length
            : 0;
        const taskId = observationPayload && observationPayload.task && observationPayload.task.task_id
          ? observationPayload.task.task_id
          : taskInput.value;
        activityEntries = [{
          stepLabel: "Reset",
          title: `Loaded ${taskId} with ${queueSize} ticket${queueSize === 1 ? "" : "s"}`,
          detail: observationPayload && observationPayload.last_action_result
            ? observationPayload.last_action_result
            : "A new episode started. Review the customer message, inspect the state, then choose the next action.",
          kind: "reset",
        }];
        renderActivityFeed();
      }

      function recordStepActivity(action, payload, observationPayload, statePayload) {
        const infoState = payload && payload.info && payload.info.state ? payload.info.state : null;
        const historyFromInfo = infoState && Array.isArray(infoState.action_history) ? infoState.action_history : null;
        const historyFromState = statePayload && Array.isArray(statePayload.action_history) ? statePayload.action_history : null;
        const lastHistoryEntry = historyFromInfo && historyFromInfo.length
          ? historyFromInfo[historyFromInfo.length - 1]
          : historyFromState && historyFromState.length
            ? historyFromState[historyFromState.length - 1]
            : null;
        const stepCount = lastHistoryEntry && typeof lastHistoryEntry.step_number === "number"
          ? lastHistoryEntry.step_number
          : statePayload && typeof statePayload.step_count === "number" && statePayload.step_count > 0
            ? statePayload.step_count
            : activityEntries.filter((entry) => entry.stepLabel.startsWith("Step")).length + 1;
        const reward = payload && payload.reward != null && Number.isFinite(Number(payload.reward))
          ? Number(payload.reward).toFixed(2)
          : "0.00";
        const lastResult = observationPayload && observationPayload.last_action_result
          ? observationPayload.last_action_result
          : "The environment processed the action.";
        const focusedTicket = findFocusedTicket(observationPayload, statePayload);
        const agentText = latestAgentMessage(focusedTicket);
        const isReplyAction = action && (action.action_type === "draft_reply" || action.action_type === "request_info");
        const isDone = Boolean(payload && payload.done);
        const repeatedAction = wasRepeatedAction(statePayload, action);
        const actionName = actionLabel(action && action.action_type);
        const ticketLabel = action && action.ticket_id ? action.ticket_id : (focusedTicket && focusedTicket.ticket_id ? focusedTicket.ticket_id : "current ticket");

        let title = `${actionName} executed`;
        let detail = `Action sent: ${actionName} on ${ticketLabel}. ${lastResult} Current status: ${currentTicketStatus(focusedTicket)}. Reward: ${reward}.`;
        let kind = "step";

        if (isReplyAction && agentText) {
          title = "Reply drafted for the customer";
          detail = `Action sent: ${actionName} on ${ticketLabel}. ${lastResult} The outbound message now appears in the Agent Reply bubble. Current status: ${currentTicketStatus(focusedTicket)}. Reward: ${reward}.`;
          kind = "reply";
        }
        if (repeatedAction) {
          title = "Duplicate action submitted";
          detail = `You sent ${actionName} again for ${ticketLabel}. ${lastResult} This usually means the same action was stepped twice, so the environment recorded another similar transition. Current status: ${currentTicketStatus(focusedTicket)}. Reward: ${reward}.`;
          kind = "step";
        }
        if (isDone) {
          title = "Episode finished";
          detail = describeCompletion(observationPayload, statePayload);
          kind = "done";
        }

        pushActivityEntry({
          stepLabel: `Step ${stepCount}`,
          title,
          detail,
          kind,
        });
        renderActivityFeed();
      }

      function renderConversationPanel(observationPayload, statePayload) {
        const tickets = getWorkingTicketsFromPayloads(observationPayload, statePayload);
        const focusedTicket = findFocusedTicket(observationPayload, statePayload);
        const focusedTicketId = focusedTicket && focusedTicket.ticket_id ? focusedTicket.ticket_id : "";
        updateConversationSelector(tickets, focusedTicketId);

        const ticket = followFocusedTicket
          ? focusedTicket
          : findTicketById(tickets, pinnedTicketId) || focusedTicket;
        if (!ticket) {
          customerRole.textContent = "Customer";
          customerMeta.textContent = "Waiting for a queue reset";
          conversationTicket.textContent = "No focused ticket";
          customerMessage.textContent = "The latest customer message will appear here once an episode is loaded.";
          customerBubble.classList.add("empty");
          agentRole.textContent = "Agent Reply";
          agentMeta.textContent = "Reply will appear after draft or request actions";
          agentMessage.textContent = "The environment will show the latest outbound reply here once the agent drafts a response.";
          agentBubble.classList.add("empty");
          renderActivityFeed();
          return;
        }

        const customerName = ticket.customer_name || "Customer";
        const tier = ticket.customer_tier || "standard";
        const customerText = latestCustomerMessage(ticket);
        const agentText = latestAgentMessage(ticket);
        const message = customerText || "No customer message available for this ticket yet.";
        const ticketLabel = ticket.ticket_id || "Ticket pending";

        customerRole.textContent = customerName;
        customerMeta.textContent = `${ticketLabel} | ${tier}`;
        conversationTicket.textContent = followFocusedTicket ? ticketLabel : `${ticketLabel} (locked)`;
        customerMessage.textContent = message;
        customerBubble.classList.toggle("empty", !customerText);
        agentRole.textContent = "Agent Reply";
        agentMeta.textContent = agentText
          ? `${ticketLabel} | latest outbound message`
          : "Reply will appear after draft or request actions";
        agentMessage.textContent = agentText || "The environment will show the latest outbound reply here once the agent drafts a response.";
        agentBubble.classList.toggle("empty", !agentText);
        renderActivityFeed();
      }

      function setStatus(text) {
        statusText.textContent = text;
      }

      function setResetRequired(value) {
        resetRequired = Boolean(value);
        if (stepBtn) stepBtn.disabled = resetRequired || episodeDone;
        if (suggestedBtn) suggestedBtn.disabled = resetRequired || episodeDone;
        if (resetRequiredBanner) resetRequiredBanner.hidden = !resetRequired;
      }

      function setEpisodeDone(value) {
        episodeDone = Boolean(value);
        if (stepBtn) stepBtn.disabled = resetRequired || episodeDone;
        if (suggestedBtn) suggestedBtn.disabled = resetRequired || episodeDone;
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

        function buildTicketSnapshot(ticket) {
          return {
            ticket_id: ticket.ticket_id,
            subject: ticket.subject,
            status: ticket.current_status,
            category: ticket.current_category,
            priority: ticket.current_priority,
            team: ticket.assigned_team,
            sla_hours_remaining: ticket.sla_hours_remaining,
            customer_sentiment: ticket.customer_sentiment,
            tags: ticket.tags || [],
            outbound_messages: Array.isArray(ticket.outbound_messages) ? ticket.outbound_messages.length : 0,
            internal_notes: Array.isArray(ticket.internal_notes) ? ticket.internal_notes.length : 0,
            requested_information: Array.isArray(ticket.requested_information) ? ticket.requested_information.length : 0,
          };
        }

        function buildAccountSnapshot(account) {
          return {
            account_id: account.account_id,
            customer_name: account.customer_name,
            customer_tier: account.customer_tier,
            plan_name: account.plan_name,
            lifecycle_stage: account.lifecycle_stage,
            security_flags: account.security_flags || [],
            open_ticket_ids: account.open_ticket_ids || [],
          };
        }

        function buildIncidentSnapshot(incident) {
          return {
            incident_id: incident.incident_id,
            ticket_id: incident.ticket_id,
            title: incident.title,
            severity: incident.severity,
            owning_team: incident.owning_team,
            status: incident.status,
          };
        }

        function buildActionSnapshot(entry) {
          return {
            step_number: entry.step_number,
            action_type: entry.action_type,
            ticket_id: entry.ticket_id,
            app: entry.app,
            target_id: entry.target_id,
            summary: entry.summary,
          };
        }

        function buildStateInspector(statePayload) {
          if (!statePayload || typeof statePayload !== "object") {
            return {};
          }
          return {
            episode_id: statePayload.episode_id || null,
            task_id: statePayload.task_id || null,
            difficulty: statePayload.difficulty || null,
            objective: statePayload.objective || "",
            step_count: statePayload.step_count || 0,
            max_steps: statePayload.max_steps || 0,
            focused_ticket_id: statePayload.focused_ticket_id || null,
            cumulative_reward: statePayload.cumulative_reward || 0,
            final_score: statePayload.final_score || 0.01,
            done: Boolean(statePayload.done),
            progress: statePayload.progress || null,
            queue: Array.isArray(statePayload.tickets)
              ? statePayload.tickets.map(buildTicketSnapshot)
              : [],
            customer_accounts: Array.isArray(statePayload.customer_accounts)
              ? statePayload.customer_accounts.map(buildAccountSnapshot)
              : [],
            incidents: Array.isArray(statePayload.incidents)
              ? statePayload.incidents.map(buildIncidentSnapshot)
              : [],
            pending_events: statePayload.pending_events || [],
            recent_events: statePayload.recent_events || [],
            last_action: Array.isArray(statePayload.action_history) && statePayload.action_history.length
              ? buildActionSnapshot(statePayload.action_history[statePayload.action_history.length - 1])
              : null,
          };
        }

        function buildResponseInspector(payload) {
          if (!payload || typeof payload !== "object") {
            return payload;
          }
          const observationPayload = extractObservationPayload(payload);
          const compact = {
            reward: payload.reward,
            done: payload.done,
            info: payload.info,
            observation: observationPayload
              ? {
                  task: observationPayload.task,
                  objective: observationPayload.objective,
                  progress: observationPayload.progress || null,
                  queue_size: Array.isArray(observationPayload.queue) ? observationPayload.queue.length : 0,
                  accessible_apps: observationPayload.accessible_apps || [],
                  recent_events: observationPayload.recent_events || [],
                  last_tool_result: observationPayload.last_tool_result || null,
                }
              : null,
          };
          return Object.fromEntries(
            Object.entries(compact).filter(([, value]) => value !== undefined && value !== null)
          );
        }

        function renderStatePanel(statePayload) {
          stateKind.textContent = "state";
          setFormattedContent(stateJson, buildStateInspector(statePayload));
        }

        function renderResponsePanel(payload, kind) {
          responseKind.textContent = kind;
          setFormattedContent(responseJson, buildResponseInspector(payload));
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
          setFormattedContent(appsJson, appSnapshots);
          setFormattedContent(worldJson, worldSummary);
          setFormattedContent(toolJson, lastToolResult);
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
        if (payload && Object.prototype.hasOwnProperty.call(payload, "done")) {
          setEpisodeDone(Boolean(payload.done));
        }
        const score = observationPayload && observationPayload.progress
          ? observationPayload.progress.score
          : statePayload && statePayload.progress
            ? statePayload.progress.score
            : null;
        const parsedScore = score == null ? null : Number(score);
        scoreText.textContent = parsedScore != null && Number.isFinite(parsedScore) ? parsedScore.toFixed(2) : "0.01";
        stepsText.textContent = statePayload && statePayload.step_count != null ? String(statePayload.step_count) : "0";
        taskText.textContent = taskInput.value;
        renderConversationPanel(observationPayload, statePayload);
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
          setFormattedContent(schemaJson, payload);
        }

      function inferCategory(ticket) {
        const subject = (ticket.subject || "").toLowerCase();
        // Infer intent from customer content only (agent replies can contain words like "incident"
        // which would otherwise cause the heuristic to drift on later steps).
        const customerMessage = (ticket.messages || [])
          .filter((message) => message && message.role === "customer")
          .map((message) => message.content || "")
          .join(" ");
        const latestMessage = `${customerMessage} ${ticket.latest_customer_message || ""}`.trim().toLowerCase();
        const tagText = ((ticket.tags || []).join(" ")).toLowerCase();
        const combined = `${subject} ${latestMessage} ${tagText}`;
        if (combined.includes("mfa") || combined.includes("2fa") || combined.includes("compromised") || combined.includes("recovery") || combined.includes("one-time code") || combined.includes("suspicious activity") || combined.includes("ceo")) {
          return {
            category: combined.includes("trust and safety") || tagText.includes("executive") || tagText.includes("trust")
              ? "security_escalation"
              : "security_account_takeover",
            priority: "urgent",
            team: "trust_safety"
          };
        }
        if (combined.includes("refund") || combined.includes("duplicate charge") || combined.includes("charged twice") || combined.includes("invoice") || combined.includes("extra charge") || combined.includes("billed twice")) {
          return {
            category: combined.includes("approval") || combined.includes("month-end") || tagText.includes("reopen-risk") || tagText.includes("policy-review") || tagText.includes("vip")
              ? "billing_approval"
              : "billing_refund",
            priority: combined.includes("enterprise") || combined.includes("month-end") || combined.includes("vip") || combined.includes("approval")
              ? "high"
              : "medium",
            team: "billing_ops"
          };
        }
        if (combined.includes("export") || combined.includes("csv") || combined.includes("xlsx") || combined.includes("500 error") || combined.includes("502 error") || combined.includes("server error") || combined.includes("reporting")) {
          const isEscalationRecovery = tagText.includes("escalation-review") || combined.includes("keeps bouncing") || combined.includes("bouncing") || combined.includes("rejected escalation");
          const isIncidentCoordinationRequest =
            combined.includes("coordinate an incident") ||
            combined.includes("incident coordination") ||
            tagText.includes("escalation-review");
          return {
            // Default to product_bug unless the customer explicitly asks for incident coordination or
            // the scenario is the escalation recovery workflow.
            category: combined.includes("bridge") || isIncidentCoordinationRequest
              ? "incident_coordination"
              : "product_bug",
            // Some scenarios (escalation packet recovery) intentionally require urgent incident coordination.
            priority: isEscalationRecovery ? "urgent" : "high",
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
        if (defaults.category === "billing_approval") {
          return "I am sorry for the billing disruption. I reviewed the account context and started the refund approval workflow with billing. We will keep you updated as the review completes, and approved refunds typically land within 5-7 business days.";
        }
        if (defaults.category === "incident_coordination") {
          return "I am sorry this is blocking your work, and I agree this is urgent. I have created an incident and escalated this issue to engineering for investigation. Please share (or confirm) the affected workspace, the approximate timestamp, and the browser details so we can reproduce the export error quickly.";
        }
        if (defaults.category === "product_bug") {
          return "I am sorry this is blocking your work, and I agree this is urgent. I have opened an incident and escalated this issue to engineering for investigation. Please share (or confirm) the affected workspace, the approximate timestamp, and the browser details so we can reproduce the export error quickly.";
        }
        if (defaults.category === "security_account_takeover" || defaults.category === "security_escalation") {
          return "I am sorry you are dealing with this. I have escalated this to our security team and Trust and Safety specialists. Please do not share passwords or one-time codes. Keep MFA enabled and use the secure recovery flow or password reset link to regain access.";
        }
        return "I am sorry you are having trouble accessing the account. Please use the secure password reset flow, and let us know if access is still blocked afterward.";
      }

      function extractReproPacket(ticket) {
        const raw = `${ticket && ticket.subject ? ticket.subject : ""} ${latestCustomerMessage(ticket)}`.trim();
        const workspaceFromField = ticket && ticket.workspace_id ? String(ticket.workspace_id) : "";
        const workspaceMatch = raw.match(/\\bworkspace\\s+([a-z0-9-]+)/i);
        const workspace = workspaceFromField || (workspaceMatch ? workspaceMatch[1] : "");
        const errorMatch = raw.match(/\\b(500 error|502 error|server error)\\b/i);
        const browserMatch = raw.match(/\\b(Chrome\\s*\\d+|Edge\\s*\\d+|Firefox\\s*ESR)\\b/i);
        const timeMatch = raw.match(/\\b(\\d{1,2}:\\d{2}\\s*UTC)\\b/i);
        return {
          workspace,
          error_code: errorMatch ? errorMatch[1] : "",
          browser: browserMatch ? browserMatch[1] : "",
          time_reference: timeMatch ? timeMatch[1] : "",
        };
      }

      function defaultEscalation(ticket, defaults) {
        if (defaults.category === "security_account_takeover" || defaults.category === "security_escalation") {
          return `Escalating ${ticket.ticket_id} to Trust and Safety for urgent account-takeover review. Subject: ${ticket.subject}. Keep MFA enabled and use secure recovery steps only.`;
        }
        if (defaults.team === "engineering" && (defaults.category === "incident_coordination" || defaults.category === "product_bug")) {
          const packet = extractReproPacket(ticket);
          const fields = [];
          if (packet.workspace) fields.push(`workspace ${packet.workspace}`);
          if (packet.error_code) fields.push(packet.error_code);
          if (packet.browser) fields.push(packet.browser);
          if (packet.time_reference) fields.push(packet.time_reference);
          const packetText = fields.length ? ` Repro packet: ${fields.join(", ")}.` : "";
          return `Escalating ${ticket.ticket_id} to engineering for incident coordination. Subject: ${ticket.subject}.${packetText} Please investigate the export outage and advise next steps.`;
        }
        return `Escalating ${ticket.ticket_id} for specialist review. Subject: ${ticket.subject}. Include workspace, impact summary, browser, and timestamp in the incident context.`;
      }

      function hasActionBeenTaken(actionType, ticketId) {
        const history = latestState && Array.isArray(latestState.action_history)
          ? latestState.action_history
          : [];
        return history.some((entry) =>
          normalizeActionType(entry.action_type) === actionType && entry.ticket_id === ticketId
        );
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

        if (taskId === "escalation_rejection_recovery") {
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
              message: "escalation packet review policy"
            };
          }
          if (!hasActionBeenTaken("create_incident", ticket.ticket_id)) {
            return {
              action_type: "create_incident",
              ticket_id: ticket.ticket_id,
              app: "incident_tracker",
              team: "engineering",
              severity: "high",
              message: `Escalation recovery incident for ${ticket.ticket_id}: ${ticket.subject}`
            };
          }
        }

        if (taskId === "refund_reopen_review") {
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
              message: "enterprise refund approval thresholds"
            };
          }
        }

        if (taskId === "mixed_queue_command_center") {
          if ((ticket.tags || []).includes("reopen-risk")) {
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
                message: "enterprise refund approval thresholds"
              };
            }
          }
          if ((ticket.tags || []).includes("incident") || (ticket.tags || []).includes("incident-follow-up")) {
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
                message: `Mixed queue incident for ${ticket.ticket_id}: ${ticket.subject}`
              };
            }
          }
          if ((ticket.tags || []).includes("trust") || (ticket.tags || []).includes("executive")) {
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
                message: "Mixed queue trust escalation note captured."
              };
            }
          }
        }

        if (taskId === "followup_reprioritization_queue") {
          if ((ticket.tags || []).includes("responds-fast") && !hasActionBeenTaken("request_info", ticket.ticket_id)) {
            return {
              action_type: "request_info",
              ticket_id: ticket.ticket_id,
              message: "Please share the workspace, browser, and approximate timestamp so we can investigate the outage."
            };
          }
          if ((ticket.tags || []).includes("responds-fast") && !hasActionBeenTaken("create_incident", ticket.ticket_id) && hasActionBeenTaken("request_info", ticket.ticket_id)) {
            if (!hasActionBeenTaken("search_policy", ticket.ticket_id)) {
              return {
                action_type: "search_policy",
                ticket_id: ticket.ticket_id,
                app: "policy_hub",
                message: "product outage escalation checklist"
              };
            }
            return {
              action_type: "create_incident",
              ticket_id: ticket.ticket_id,
              app: "incident_tracker",
              team: "engineering",
              severity: "high",
              message: `Follow-up outage incident for ${ticket.ticket_id}: ${ticket.subject}`
            };
          }
        }

        return null;
      }

      function workflowRank(taskId, ticket, defaults) {
        if (taskId !== "mixed_queue_command_center") {
          return 0;
        }
        // Enforce the intended mixed-queue prioritization:
        // security -> outage -> refund -> routine access.
        const category = defaults && defaults.category ? defaults.category : "";
        if (category === "security_account_takeover" || category === "security_escalation") return 0;
        if (category === "product_bug" || category === "incident_coordination") return 1;
        if (category === "billing_refund" || category === "billing_approval") return 2;
        return 3;
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
          const aWorkflow = workflowRank(taskInput.value, a, aDefaults);
          const bWorkflow = workflowRank(taskInput.value, b, bDefaults);
          if (aWorkflow !== bWorkflow) return aWorkflow - bWorkflow;
          const aDone = ["resolved", "escalated"].includes(a.current_status) ? 1 : 0;
          const bDone = ["resolved", "escalated"].includes(b.current_status) ? 1 : 0;
          if (aDone !== bDone) return aDone - bDone;
          return (priorityRank[aDefaults.priority] ?? 9) - (priorityRank[bDefaults.priority] ?? 9);
        });

        const activeTickets = tickets.filter((ticket) => !["resolved", "escalated"].includes(ticket.current_status));
        if (!activeTickets.length) {
          actionInput.value = pretty({ action_type: "finish" });
          setStatus("Queue complete. Send finish to close the episode.");
          return;
        }

        for (const ticket of tickets) {
          if (["resolved", "escalated"].includes(ticket.current_status)) {
            continue;
          }
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

          if (defaults.category === "billing_refund" || defaults.category === "billing_approval") {
            const hasReply =
              (ticket.outbound_messages && ticket.outbound_messages.length > 0) ||
              hasActionBeenTaken("draft_reply", ticket.ticket_id) ||
              hasActionBeenTaken("request_info", ticket.ticket_id);
            if (!hasReply) {
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

          if (defaults.category === "product_bug" || defaults.category === "incident_coordination" || defaults.category === "security_account_takeover" || defaults.category === "security_escalation") {
            const hasReply =
              (ticket.outbound_messages && ticket.outbound_messages.length > 0) ||
              hasActionBeenTaken("draft_reply", ticket.ticket_id) ||
              hasActionBeenTaken("request_info", ticket.ticket_id);
            if (!hasReply) {
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

      async function suggestNextAction() {
        if (episodeDone) {
          setStatus("Episode finished. Press Reset to start a new episode.");
          return;
        }
        // Suggest from local shadow-state; /state is minimal in OpenEnv HTTP server.
        // If we have no tickets yet, try hydrating once.
        if (!latestState || !Array.isArray(latestState.tickets) || latestState.tickets.length === 0) {
          try {
            await refreshState();
          } catch {
            // ignore
          }
        }
        buildSuggestedActionFromState();
      }

        async function refreshState() {
          const response = await fetch("/state");
          const payload = await response.json();
          const parsedState = extractStatePayload(payload);
          // OpenEnv `/state` can be minimal (episode_id + step_count only). Don't wipe the
          // richer shadow state built from `/reset` + `/step` observations.
          if (parsedState) {
            if (parsedState.tickets && Array.isArray(parsedState.tickets)) {
              latestState = parsedState;
            } else if (latestState && typeof latestState === "object") {
              latestState = { ...latestState, ...parsedState };
            } else {
              latestState = parsedState;
            }
          }
          renderStatePanel(latestState || payload);
          updateSummary(latestResult, latestState);
          return payload;
        }

      async function doReset() {
        setStatus("Resetting episode...");
        setEpisodeDone(false);
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
        if (response.ok) {
          setResetRequired(false);
          activeEpisodeTaskId = taskInput.value;
          followFocusedTicket = true;
          pinnedTicketId = "";
          if (followFocusToggle) {
            followFocusToggle.checked = true;
          }
        }
        latestObservation = extractObservationPayload(payload);
          latestState = buildStateFromObservation(latestObservation) || latestState;
          if (latestState) {
            latestState.step_count = 0;
            latestState.action_history = [];
            if (latestObservation && latestObservation.focused_ticket && latestObservation.focused_ticket.ticket_id) {
              latestState.focused_ticket_id = latestObservation.focused_ticket.ticket_id;
              latestState.tickets = (latestState.tickets || []).map((ticket) =>
                ticket.ticket_id === latestObservation.focused_ticket.ticket_id ? latestObservation.focused_ticket : ticket
              );
            }
          }
          latestResult = payload;
          renderResponsePanel(payload, "reset");
          renderStatePanel(latestState);
          updateSummary(payload, latestState);
          recordResetActivity(latestObservation, latestState);
          setStatus(response.ok ? "Episode reset successfully" : "Reset failed");
          await suggestNextAction();
        }

      async function doStep() {
        if (resetRequired) {
          setStatus("Task changed. Press Reset before stepping.");
          return;
        }
        if (episodeDone) {
          setStatus("Episode finished. Press Reset to start a new episode.");
          return;
        }
        setStatus("Sending action...");
        let action;
        try {
          action = JSON.parse(actionInput.value);
          } catch (error) {
            setStatus("Action JSON is invalid");
            responseKind.textContent = "client-error";
            setFormattedContent(responseJson, { error: "Invalid JSON", detail: String(error) });
            return;
          }
        const response = await fetch("/step", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action }),
        });
        const payload = await response.json();
          latestObservation = extractObservationPayload(payload);
          const priorState = latestState;
          latestState = buildStateFromObservation(latestObservation) || latestState;
          if (latestState) {
            const priorHistory = priorState && Array.isArray(priorState.action_history) ? priorState.action_history : [];
            // buildStateFromObservation may initialize an empty array each time; preserve history unless
            // the new state already contains meaningful action history.
            if (Array.isArray(latestState.action_history) && latestState.action_history.length > 0) {
              // keep as-is
            } else {
              latestState.action_history = [...priorHistory];
            }
            const priorSteps = priorState && typeof priorState.step_count === "number" ? priorState.step_count : 0;
            latestState.step_count = priorSteps + 1;

            if (latestObservation && latestObservation.focused_ticket && latestObservation.focused_ticket.ticket_id) {
              latestState.focused_ticket_id = latestObservation.focused_ticket.ticket_id;
              latestState.tickets = (latestState.tickets || []).map((ticket) =>
                ticket.ticket_id === latestObservation.focused_ticket.ticket_id ? latestObservation.focused_ticket : ticket
              );
            }

            latestState.action_history.push({
              step_number: latestState.step_count,
              action_type: action.action_type,
              ticket_id: action.ticket_id || null,
              app: action.app || null,
              target_id: action.target_id || null,
              summary: latestObservation && latestObservation.last_action_result ? latestObservation.last_action_result : "",
            });
          }
          latestResult = payload;
          renderResponsePanel(payload, "step");
          renderStatePanel(latestState);
          updateSummary(payload, latestState);
          recordStepActivity(action, payload, latestObservation, latestState);
          if (payload && payload.done) {
            setStatus("Episode finished. Press Reset to start a new episode.");
            return;
          }
          setStatus(response.ok ? "Action executed" : "Step request failed");
          await suggestNextAction();
        }

        async function getState() {
          setStatus("Fetching current state...");
          const payload = await refreshState();
          renderResponsePanel(payload, "state");
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
          },
          escalation_rejection_recovery: {
            action_type: "create_incident",
            ticket_id: "TCK-0000",
            app: "incident_tracker",
            team: "engineering",
            severity: "high",
            message: "Escalation recovery incident with full repro context."
          },
          refund_reopen_review: {
            action_type: "check_billing_status",
            ticket_id: "TCK-0000",
            app: "billing_system"
          },
          mixed_queue_command_center: {
            action_type: "lookup_account",
            ticket_id: "TCK-0000",
            app: "crm_workspace"
          },
          followup_reprioritization_queue: {
            action_type: "request_info",
            ticket_id: "TCK-0000",
            message: "Please share the workspace, browser, and approximate timestamp so we can investigate the outage."
          }
        };
        actionInput.value = pretty(samples[taskInput.value]);
      }

      document.getElementById("reset-btn").addEventListener("click", doReset);
      document.getElementById("step-btn").addEventListener("click", doStep);
      document.getElementById("state-btn").addEventListener("click", getState);
      document.getElementById("schema-btn").addEventListener("click", loadSchema);
      document.getElementById("fill-sample").addEventListener("click", suggestNextAction);
      taskInput.addEventListener("change", () => {
        taskText.textContent = taskInput.value;
        // Only enforce "reset required" once the user has started an episode in this session.
        // Otherwise the banner can appear the first time someone selects a task, which feels noisy.
        if (activeEpisodeTaskId) {
          if (taskInput.value === activeEpisodeTaskId) {
            setResetRequired(false);
            setStatus("Returned to current episode task.");
          } else {
            setResetRequired(true);
            setStatus("Task changed. Press Reset to start a new episode.");
          }
        }
        fillSample();
      });
      if (followFocusToggle) {
        followFocusToggle.addEventListener("change", () => {
          followFocusedTicket = Boolean(followFocusToggle.checked);
          if (conversationTicketSelect) {
            conversationTicketSelect.disabled = followFocusedTicket;
          }
          updateSummary(latestResult, latestState);
        });
      }
      if (conversationTicketSelect) {
        conversationTicketSelect.addEventListener("change", () => {
          pinnedTicketId = conversationTicketSelect.value || "";
          updateSummary(latestResult, latestState);
        });
      }

      fillSample();
        loadMetadata().catch((error) => {
          serviceMeta.textContent = "Metadata unavailable";
          responseKind.textContent = "error";
          setFormattedContent(responseJson, { error: "Metadata fetch failed", detail: String(error) });
        });
        loadSchema().catch((error) => {
          schemaKind.textContent = "error";
          setFormattedContent(schemaJson, { error: "Schema fetch failed", detail: String(error) });
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
