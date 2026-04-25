from __future__ import annotations

from pathlib import Path

from openenv.core.env_server.http_server import create_app
from fastapi.staticfiles import StaticFiles
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

PROJECT_DOCS_BUILD_DIR = Path(__file__).resolve().parent.parent / "documentation-customer_support" / "build"

if PROJECT_DOCS_BUILD_DIR.exists():
    app.mount(
        "/project-docs",
        StaticFiles(directory=str(PROJECT_DOCS_BUILD_DIR), html=True),
        name="project-docs",
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
    <link rel="icon" href="data:," />
    <style>
      :root {
        color-scheme: dark;
        --bg: #090b10;
        --bg-soft: #111725;
        --panel: rgba(16, 21, 32, 0.94);
        --panel-strong: #161d2c;
        --panel-muted: #1a2334;
        --ink: #f4f7fb;
        --muted: #94a2b8;
        --muted-strong: #d6deea;
        --accent: #7d8cff;
        --accent-soft: rgba(125, 140, 255, 0.14);
        --line: rgba(162, 180, 212, 0.12);
        --line-strong: rgba(162, 180, 212, 0.2);
        --success: #31d0aa;
        --warning: #ffb648;
        --shadow: 0 28px 80px rgba(0, 0, 0, 0.52);
        --shadow-soft: 0 12px 30px rgba(0, 0, 0, 0.3);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(125, 140, 255, 0.14), transparent 28%),
          radial-gradient(circle at bottom right, rgba(56, 214, 255, 0.1), transparent 26%),
          linear-gradient(180deg, #090b10 0%, #0e1219 100%);
        color: var(--ink);
        transition: background 180ms ease, color 180ms ease;
      }
      main {
        max-width: 1680px;
        margin: 0 auto;
        padding: 24px 24px 30px;
      }
      .dashboard-shell {
        display: grid;
        grid-template-columns: 82px minmax(0, 1fr);
        gap: 18px;
        align-items: start;
      }
      body.sidebar-expanded .dashboard-shell {
        grid-template-columns: 220px minmax(0, 1fr);
      }
      .nav-rail {
        position: sticky;
        top: 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 14px;
        min-height: calc(100vh - 48px);
        padding: 18px 12px;
        border-radius: 28px;
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(8, 10, 16, 0.98), rgba(13, 17, 26, 0.96));
        box-shadow: var(--shadow-soft);
        transition: width 180ms ease, padding 180ms ease, border-color 180ms ease, background 180ms ease;
      }
      body.sidebar-expanded .nav-rail {
        align-items: stretch;
        padding: 18px 14px;
      }
      .rail-top {
        display: grid;
        gap: 12px;
        justify-items: center;
      }
      body.sidebar-expanded .rail-top {
        justify-items: stretch;
      }
      .rail-brand,
      .rail-link,
      .rail-toggle,
      .rail-avatar {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: grid;
        place-items: center;
      }
      body.sidebar-expanded .rail-brand,
      body.sidebar-expanded .rail-link,
      body.sidebar-expanded .rail-toggle,
      body.sidebar-expanded .rail-avatar {
        width: 100%;
      }
      .rail-brand {
        background: radial-gradient(circle at 30% 30%, #9aa7ff, #6474ff 60%, #3944d0 100%);
        color: white;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.08em;
        box-shadow: 0 10px 24px rgba(100, 116, 255, 0.35);
      }
      .rail-toggle {
        border: 1px solid transparent;
        background: rgba(255, 255, 255, 0.03);
        color: var(--muted-strong);
        cursor: pointer;
        transition: transform 120ms ease, background 120ms ease, border-color 120ms ease, color 120ms ease;
      }
      .rail-toggle:hover {
        transform: translateY(-1px);
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(125, 140, 255, 0.24);
        color: #ffffff;
      }
      .rail-toggle .rail-code,
      .rail-toggle .rail-glyph {
        font-size: 0;
      }
      .rail-toggle .rail-code::before,
      .rail-toggle .rail-glyph::before {
        content: "|||";
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.02em;
      }
      .rail-link {
        border: 1px solid transparent;
        background: rgba(255, 255, 255, 0.03);
        color: var(--muted-strong);
        text-decoration: none;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.06em;
        transition: transform 120ms ease, background 120ms ease, border-color 120ms ease, color 120ms ease;
      }
      .rail-link:hover {
        transform: translateY(-1px);
      }
      .rail-link.active,
      .rail-link:hover {
        background: linear-gradient(180deg, rgba(125, 140, 255, 0.2), rgba(56, 214, 255, 0.12));
        border-color: rgba(125, 140, 255, 0.26);
        color: #ffffff;
      }
      body.sidebar-expanded .rail-link,
      body.sidebar-expanded .rail-toggle,
      body.sidebar-expanded .rail-avatar,
      body.sidebar-expanded .rail-brand {
        grid-template-columns: 28px minmax(0, 1fr);
        justify-items: start;
        padding: 0 14px;
      }
      .rail-code,
      .rail-label,
      .rail-brand-text {
        line-height: 1;
      }
      .rail-label,
      .rail-brand-text,
      .rail-glyph {
        display: none;
      }
      body.sidebar-expanded .rail-label,
      body.sidebar-expanded .rail-brand-text,
      body.sidebar-expanded .rail-glyph {
        display: inline;
      }
      body.sidebar-expanded .rail-code.compact-only {
        display: none;
      }
      .rail-glyph {
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.04em;
      }
      .rail-label,
      .rail-brand-text {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.04em;
        white-space: nowrap;
      }
      .rail-spacer {
        flex: 1;
      }
      .rail-avatar {
        background: linear-gradient(180deg, rgba(255, 95, 115, 0.24), rgba(125, 140, 255, 0.16));
        color: white;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.08);
      }
      .shell {
        position: relative;
        background: linear-gradient(180deg, rgba(9, 12, 18, 0.98), rgba(13, 17, 26, 0.98));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 30px;
        box-shadow: var(--shadow);
        overflow: hidden;
      }
      .shell::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(125, 140, 255, 0.2), transparent);
      }
      .topbar {
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.9fr);
        gap: 24px;
        padding: 28px 28px 24px;
        border-bottom: 1px solid var(--line);
        background:
          radial-gradient(circle at top right, rgba(125, 140, 255, 0.12), transparent 28%),
          linear-gradient(180deg, rgba(14, 18, 27, 0.98), rgba(9, 12, 18, 0.96));
      }
      .hero-copy {
        display: grid;
        gap: 18px;
      }
      .brand-row {
        display: grid;
        grid-template-columns: 220px minmax(0, 1fr);
        gap: 18px;
        align-items: center;
      }
      .brand-lockup {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        color: #ffffff;
        font-size: 15px;
        font-weight: 700;
      }
      .brand-lockup span:last-child {
        color: inherit;
      }
      .brand-mark {
        width: 28px;
        height: 28px;
        border-radius: 10px;
        display: grid;
        place-items: center;
        background: linear-gradient(180deg, #7d8cff, #9d52ff);
        box-shadow: 0 8px 16px rgba(125, 140, 255, 0.22);
        font-size: 11px;
      }
      .search-shell {
        display: flex;
        align-items: center;
        gap: 10px;
        min-height: 48px;
        padding: 0 14px;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.04);
        color: var(--muted);
        min-width: 0;
      }
      .search-label {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--muted);
      }
      .search-shell input {
        border: 0;
        background: transparent;
        padding: 0;
        box-shadow: none;
        color: var(--ink);
      }
      .search-shell input:focus {
        box-shadow: none;
      }
      .hero-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: nowrap;
      }
      .header-actions {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        flex-wrap: nowrap;
        justify-content: flex-end;
        flex-shrink: 0;
      }
      .theme-toggle {
        min-width: 132px;
        width: auto;
        white-space: nowrap;
      }
      .header-icon {
        min-width: 46px;
        height: 46px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.04);
        color: var(--muted-strong);
        padding: 0 14px;
        font-size: 13px;
        font-weight: 600;
      }
      .profile-pill {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        padding: 8px 12px;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.04);
        min-height: 54px;
        flex-shrink: 0;
      }
      .profile-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background: linear-gradient(180deg, #ffb648, #ff6a6f);
        color: #fff;
        font-weight: 700;
      }
      .profile-copy strong {
        display: block;
        font-size: 14px;
        color: #fff;
      }
      .profile-copy span {
        display: block;
        font-size: 12px;
        color: var(--muted);
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        width: fit-content;
        padding: 7px 12px;
        border-radius: 999px;
        border: 1px solid rgba(125, 140, 255, 0.16);
        background: rgba(125, 140, 255, 0.1);
        color: #dbe3ff;
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
        box-shadow: 0 0 0 4px rgba(49, 208, 170, 0.14);
      }
      h1 {
        margin: 0;
        font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
        font-size: 54px;
        line-height: 0.92;
        letter-spacing: -1.6px;
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
        font-size: 20px;
        font-weight: 600;
        letter-spacing: -0.35px;
        color: var(--muted);
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
        grid-template-columns: repeat(4, minmax(0, 1fr));
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
        grid-template-columns: minmax(280px, 320px) minmax(0, 1fr);
        align-items: start;
        gap: 18px;
        padding: 18px;
      }
      .playground {
        min-width: 0;
        grid-column: 2;
      }
      .sidebar {
        display: grid;
        gap: 16px;
        position: sticky;
        top: 18px;
        align-self: start;
        width: 100%;
        min-width: 0;
        grid-column: 1;
        grid-row: 1;
      }
      .menu-list {
        display: grid;
        gap: 8px;
        margin-top: 6px;
      }
      .menu-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        width: 100%;
        padding: 12px 14px;
        border-radius: 14px;
        border: 1px solid transparent;
        background: rgba(255, 255, 255, 0.03);
        color: var(--muted-strong);
        font-weight: 600;
        cursor: pointer;
        text-align: left;
      }
      .menu-item.active {
        background: linear-gradient(180deg, rgba(157, 82, 255, 0.8), rgba(106, 91, 255, 0.8));
        color: #fff;
        box-shadow: 0 14px 26px rgba(125, 83, 255, 0.24);
      }
      .menu-icon {
        opacity: 0.9;
      }
      .support-card {
        display: grid;
        gap: 12px;
      }
      body[data-theme="light"] {
        --bg: #eef3ff;
        --bg-soft: #f7f9ff;
        --panel: rgba(255, 255, 255, 0.92);
        --panel-strong: #ffffff;
        --panel-muted: #eef2ff;
        --ink: #1d2433;
        --muted: #63708a;
        --muted-strong: #2a3550;
        --accent: #6f59ff;
        --accent-soft: rgba(111, 89, 255, 0.12);
        --line: rgba(73, 95, 135, 0.14);
        --line-strong: rgba(73, 95, 135, 0.22);
        --success: #21b990;
        --warning: #e59f32;
        --shadow: 0 28px 80px rgba(50, 63, 96, 0.16);
        --shadow-soft: 0 12px 30px rgba(50, 63, 96, 0.12);
      }
      body[data-theme="light"] {
        background:
          radial-gradient(circle at top left, rgba(111, 89, 255, 0.12), transparent 26%),
          radial-gradient(circle at bottom right, rgba(56, 214, 255, 0.12), transparent 24%),
          linear-gradient(180deg, #f7f9ff 0%, #edf2ff 100%);
      }
      body[data-theme="light"] .nav-rail,
      body[data-theme="light"] .shell,
      body[data-theme="light"] .topbar,
      body[data-theme="light"] .panel,
      body[data-theme="light"] .summary-card,
      body[data-theme="light"] .control-card,
      body[data-theme="light"] .note-card,
      body[data-theme="light"] .json-box,
      body[data-theme="light"] .mini-card,
      body[data-theme="light"] .status-card,
      body[data-theme="light"] .pill,
      body[data-theme="light"] .quick-code,
      body[data-theme="light"] .search-shell,
      body[data-theme="light"] .profile-pill,
      body[data-theme="light"] .header-icon,
      body[data-theme="light"] .menu-item,
      body[data-theme="light"] .follow-toggle,
      body[data-theme="light"] .conversation-select,
      body[data-theme="light"] .conversation-chip,
      body[data-theme="light"] .chat-bubble,
      body[data-theme="light"] .activity-entry,
      body[data-theme="light"] .activity-empty,
      body[data-theme="light"] .service-metric {
        background: rgba(255, 255, 255, 0.82);
        color: var(--ink);
      }
      body[data-theme="light"] .search-shell input,
      body[data-theme="light"] .search-label,
      body[data-theme="light"] .header-icon,
      body[data-theme="light"] .theme-toggle,
      body[data-theme="light"] .summary-card span,
      body[data-theme="light"] .mini-card span,
      body[data-theme="light"] .panel h2,
      body[data-theme="light"] .panel h3,
      body[data-theme="light"] .json-box header strong,
      body[data-theme="light"] pre,
      body[data-theme="light"] .quick-code,
      body[data-theme="light"] .conversation-chip,
      body[data-theme="light"] .chat-bubble p,
      body[data-theme="light"] .headline-mark,
      body[data-theme="light"] .section-kicker,
      body[data-theme="light"] .conversation-label,
      body[data-theme="light"] .message-role,
      body[data-theme="light"] .activity-head strong,
      body[data-theme="light"] .activity-body strong,
      body[data-theme="light"] .activity-step,
      body[data-theme="light"] .message-meta,
      body[data-theme="light"] .message-role,
      body[data-theme="light"] .message-ticket,
      body[data-theme="light"] .follow-toggle,
      body[data-theme="light"] .conversation-caption {
        color: #1d2433;
      }
      body[data-theme="light"] #conversation-ticket,
      body[data-theme="light"] #customer-meta,
      body[data-theme="light"] #agent-meta,
      body[data-theme="light"] #agent-role,
      body[data-theme="light"] #customer-role {
        color: #33415c;
      }
      body[data-theme="light"] textarea {
        background: #1b1f27;
        color: #e6edff;
        border-color: rgba(73, 95, 135, 0.22);
      }
      body[data-theme="light"] select {
        color-scheme: light;
        background:
          linear-gradient(45deg, transparent 50%, rgba(68, 80, 106, 0.8) 50%),
          linear-gradient(135deg, rgba(68, 80, 106, 0.8) 50%, transparent 50%),
          linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(243, 247, 255, 0.98));
        background-position:
          calc(100% - 18px) calc(50% - 3px),
          calc(100% - 12px) calc(50% - 3px),
          0 0;
        background-size: 6px 6px, 6px 6px, 100% 100%;
        background-repeat: no-repeat;
        border-color: rgba(73, 95, 135, 0.18);
        color: #1d2433;
      }
      body[data-theme="light"] select option {
        background: #ffffff;
        color: #1d2433;
      }
      body[data-theme="light"] textarea::placeholder {
        color: #93a0ba;
      }
      body[data-theme="light"] .status-card strong,
      body[data-theme="light"] .status-card p,
      body[data-theme="light"] .status-list,
      body[data-theme="light"] .service-metric strong,
      body[data-theme="light"] .service-metric span,
      body[data-theme="light"] .activity-head span,
      body[data-theme="light"] .activity-body p,
      body[data-theme="light"] .activity-empty,
      body[data-theme="light"] .chat-bubble.empty p,
      body[data-theme="light"] .conversation-select:disabled {
        color: #4a5a78;
      }
      body[data-theme="light"] .message-row.agent .message-role,
      body[data-theme="light"] .message-row.agent .message-ticket,
      body[data-theme="light"] .message-row .message-ticket,
      body[data-theme="light"] .message-row .message-role {
        color: #51637f;
      }
      body[data-theme="light"] .conversation-select:disabled {
        -webkit-text-fill-color: #4a5a78;
        border-color: rgba(73, 95, 135, 0.18);
        background:
          linear-gradient(45deg, transparent 50%, rgba(68, 80, 106, 0.6) 50%),
          linear-gradient(135deg, rgba(68, 80, 106, 0.6) 50%, transparent 50%),
          linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(243, 247, 255, 0.96));
        background-position:
          calc(100% - 18px) calc(50% - 3px),
          calc(100% - 12px) calc(50% - 3px),
          0 0;
        background-size: 6px 6px, 6px 6px, 100% 100%;
        background-repeat: no-repeat;
      }
      body[data-theme="light"] .conversation-panel {
        background:
          radial-gradient(circle at top left, rgba(111, 89, 255, 0.12), transparent 28%),
          radial-gradient(circle at right center, rgba(56, 214, 255, 0.1), transparent 32%),
          linear-gradient(180deg, #ffffff 0%, #edf2ff 100%);
      }
      body[data-theme="light"] .rail-link {
        background: rgba(111, 89, 255, 0.08);
        border-color: rgba(111, 89, 255, 0.14);
        color: #44506a;
      }
      body[data-theme="light"] .rail-toggle {
        background: rgba(111, 89, 255, 0.08);
        border-color: rgba(111, 89, 255, 0.14);
        color: #44506a;
      }
      body[data-theme="light"] .rail-link.active,
      body[data-theme="light"] .rail-link:hover {
        background: linear-gradient(180deg, rgba(111, 89, 255, 0.92), rgba(135, 93, 255, 0.88));
        border-color: rgba(111, 89, 255, 0.32);
        color: #ffffff;
      }
      body[data-theme="light"] .rail-toggle:hover {
        background: rgba(111, 89, 255, 0.16);
        border-color: rgba(111, 89, 255, 0.24);
        color: #263248;
      }
      body[data-theme="light"] .brand-lockup,
      body[data-theme="light"] .profile-copy strong,
      body[data-theme="light"] .rail-link.active,
      body[data-theme="light"] .menu-item.active,
      body[data-theme="light"] .brand-mark,
      body[data-theme="light"] .message-avatar {
        color: #ffffff;
      }
      body[data-theme="light"] .subtitle,
      body[data-theme="light"] .headline-sub,
      body[data-theme="light"] .panel p,
      body[data-theme="light"] .panel li,
      body[data-theme="light"] label,
      body[data-theme="light"] .helper,
      body[data-theme="light"] .status-list,
      body[data-theme="light"] .message-ticket,
      body[data-theme="light"] .profile-copy span {
        color: var(--muted);
      }
      body[data-theme="light"] .profile-pill,
      body[data-theme="light"] .search-shell,
      body[data-theme="light"] .header-icon,
      body[data-theme="light"] .theme-toggle {
        border-color: rgba(73, 95, 135, 0.18);
      }
      body[data-theme="light"] .menu-item {
        background: rgba(255, 255, 255, 0.88);
        color: #263248;
      }
      body[data-theme="light"] .menu-item.active {
        background: linear-gradient(180deg, rgba(111, 89, 255, 0.94), rgba(135, 93, 255, 0.9));
        color: #ffffff;
      }
      body[data-theme="light"] .eyebrow {
        color: #6f59ff;
        background: rgba(111, 89, 255, 0.08);
      }
      body[data-theme="light"] .conversation-panel h2 {
        color: #1d2433 !important;
      }
      body[data-theme="light"] .brand-lockup,
      body[data-theme="light"] .brand-lockup span:last-child,
      body[data-theme="light"] .rail-brand-text {
        color: #1d2433;
      }
      body[data-theme="light"] .runner-badge {
        background: rgba(111, 89, 255, 0.1);
        border-color: rgba(111, 89, 255, 0.18);
        color: #44506a;
      }
      body[data-theme="light"] .message-avatar {
        background: linear-gradient(180deg, rgba(111, 89, 255, 0.12), rgba(86, 214, 255, 0.08));
        border-color: rgba(111, 89, 255, 0.16);
        color: #3b4c67;
      }
      body[data-theme="light"] .message-row.agent .message-avatar {
        background: linear-gradient(180deg, rgba(133, 158, 189, 0.22), rgba(102, 122, 149, 0.16));
        border-color: rgba(102, 122, 149, 0.18);
        color: #3b4c67;
      }
      .support-box {
        border-radius: 18px;
        padding: 18px;
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(125, 140, 255, 0.18), rgba(157, 82, 255, 0.14));
      }
      .support-box h3 {
        margin: 0 0 8px;
        font-size: 18px;
      }
      .support-box p {
        margin: 0 0 14px;
      }
      .support-box .link-btn {
        width: 100%;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 22px;
        background: linear-gradient(180deg, rgba(16, 21, 32, 0.98), rgba(11, 14, 22, 0.98));
        box-shadow: var(--shadow-soft);
        min-width: 0;
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
        overflow: hidden;
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
        min-height: 40px;
        padding: 10px 16px;
        border-radius: 999px;
        border: 1px solid rgba(125, 140, 255, 0.14);
        background: rgba(125, 140, 255, 0.08);
        color: #dce5ff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.03em;
        white-space: nowrap;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
      }
      .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
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
        grid-template-columns: minmax(0, 1.2fr) 140px 180px;
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
        grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.85fr);
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
      select {
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        padding-right: 42px;
        color-scheme: dark;
        background:
          linear-gradient(45deg, transparent 50%, rgba(219, 231, 255, 0.82) 50%),
          linear-gradient(135deg, rgba(219, 231, 255, 0.82) 50%, transparent 50%),
          linear-gradient(180deg, rgba(16, 21, 32, 0.96), rgba(11, 14, 22, 0.98));
        background-position:
          calc(100% - 18px) calc(50% - 3px),
          calc(100% - 12px) calc(50% - 3px),
          0 0;
        background-size: 6px 6px, 6px 6px, 100% 100%;
        background-repeat: no-repeat;
        border-color: rgba(162, 180, 212, 0.16);
        color: #eef4ff;
      }
      select option {
        background: #121825;
        color: #eef4ff;
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
        color: #dbe7ff;
        caret-color: #ffffff;
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
        grid-template-columns: repeat(2, minmax(0, 1fr));
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
        min-width: 0;
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
        overflow-wrap: anywhere;
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
        background: rgba(125, 140, 255, 0.12);
        border-radius: 8px;
        padding: 2px 6px;
        color: #c5d0ff;
      }
      .panel,
      .summary-card,
      .control-card,
      .note-card,
      .json-box,
      .mini-card,
      .status-card,
      .conversation-panel,
      .pill,
      .quick-code {
        backdrop-filter: blur(12px);
      }
      .panel,
      .summary-card,
      .control-card,
      .note-card,
      .json-box,
      .mini-card,
      .pill {
        background: linear-gradient(180deg, rgba(16, 21, 32, 0.98), rgba(11, 14, 22, 0.98));
      }
      .panel,
      .summary-card,
      .control-card,
      .note-card,
      .json-box,
      .mini-card,
      .service-metric,
      .pill,
      .quick-code {
        border-color: var(--line);
      }
      .status-card {
        background: linear-gradient(180deg, rgba(16, 21, 32, 0.98), rgba(11, 14, 22, 0.98));
      }
      .mini-card strong,
      .summary-card strong,
      .helper,
      .note-card strong,
      .panel p,
      .panel li,
      label,
      .status-list,
      .subtitle,
      .headline-sub,
      .conversation-caption,
      .activity-head span,
      .message-ticket {
        color: var(--muted);
      }
      .mini-card span,
      .summary-card span,
      .panel h2,
      .status-card span,
      .activity-head strong,
      .message-role,
      .conversation-chip,
      .runner-badge,
      .quick-code,
      pre {
        color: var(--ink);
      }
      .chip {
        background: rgba(125, 140, 255, 0.1);
        color: #dfe5ff;
        border: 1px solid rgba(125, 140, 255, 0.16);
      }
      .quick-code,
      .json-box,
      .json-box header,
      .control-card,
      .note-card,
      .summary-card,
      .pill,
      select,
      input,
      textarea,
      button,
      .link-btn,
      .follow-toggle,
      .conversation-select,
      .conversation-chip,
      .chat-bubble,
      .activity-entry,
      .activity-empty {
        background-color: rgba(255, 255, 255, 0.04);
      }
      select,
      input,
      textarea {
        border-color: rgba(162, 180, 212, 0.14);
        color: var(--ink);
      }
      textarea {
        background: rgba(7, 10, 16, 0.92);
      }
      button,
      .link-btn {
        border-color: rgba(162, 180, 212, 0.12);
        color: var(--muted-strong);
      }
      button:hover,
      .link-btn:hover {
        border-color: rgba(125, 140, 255, 0.3);
        background: rgba(125, 140, 255, 0.12);
      }
      button.primary {
        background: linear-gradient(180deg, #6d7cff, #5262f1);
        box-shadow: 0 14px 26px rgba(82, 98, 241, 0.32);
        color: white;
      }
      .banner {
        border-color: rgba(255, 182, 72, 0.2);
        background: rgba(255, 182, 72, 0.08);
        color: #ffd89f;
      }
      .banner strong,
      .banner .hint,
      .banner span {
        color: inherit;
      }
      .service-metric {
        background: rgba(255, 255, 255, 0.03);
      }
      .conversation-panel {
        background:
          radial-gradient(circle at top left, rgba(125, 140, 255, 0.16), transparent 28%),
          radial-gradient(circle at right center, rgba(56, 214, 255, 0.12), transparent 32%),
          linear-gradient(180deg, #111726 0%, #0b1019 100%);
        border-color: rgba(162, 180, 212, 0.12);
      }
      .message-avatar {
        background: linear-gradient(180deg, rgba(125, 140, 255, 0.32), rgba(56, 214, 255, 0.12));
        border: 1px solid rgba(125, 140, 255, 0.22);
        color: white;
      }
      .activity-entry {
        border-color: rgba(162, 180, 212, 0.12);
      }
      .link-grid .link-btn {
        text-align: center;
      }
      @media (max-width: 1320px) {
        .dashboard-shell {
          grid-template-columns: 1fr;
        }
        body.sidebar-expanded .dashboard-shell {
          grid-template-columns: 1fr;
        }
        .nav-rail {
          position: static;
          min-height: auto;
          flex-direction: row;
          justify-content: center;
          flex-wrap: wrap;
        }
        body.sidebar-expanded .nav-rail {
          align-items: center;
        }
        body.sidebar-expanded .rail-top {
          grid-auto-flow: column;
          align-items: center;
          justify-items: center;
        }
        body.sidebar-expanded .rail-link,
        body.sidebar-expanded .rail-toggle,
        body.sidebar-expanded .rail-avatar,
        body.sidebar-expanded .rail-brand {
          width: auto;
          min-width: 44px;
        }
        body.sidebar-expanded .rail-label,
        body.sidebar-expanded .rail-brand-text,
        body.sidebar-expanded .rail-glyph {
          display: none;
        }
        body.sidebar-expanded .rail-code.compact-only {
          display: inline;
        }
        .layout {
          grid-template-columns: 1fr;
        }
        .sidebar {
          position: static;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          grid-column: auto;
          grid-row: auto;
        }
        .playground {
          grid-column: auto;
        }
      }
      @media (max-width: 1180px) {
        .topbar {
          grid-template-columns: 1fr;
        }
        .brand-row {
          grid-template-columns: 1fr;
        }
        .hero-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
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
        .hero-grid {
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
        .hero-header,
        .header-actions {
          flex-wrap: wrap;
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
      <div class="dashboard-shell">
        <aside class="nav-rail" aria-label="Dashboard navigation">
          <div class="rail-top">
            <div class="rail-brand">
              <span class="rail-code compact-only">TS</span>
              <span class="rail-glyph">TS</span>
              <span class="rail-brand-text">TriageOS</span>
            </div>
            <button class="rail-toggle" id="rail-toggle" type="button" aria-expanded="false" aria-label="Toggle sidebar">
              <span class="rail-code compact-only">≡</span>
              <span class="rail-glyph">≡</span>
              <span class="rail-label">Toggle Menu</span>
            </button>
            <a class="rail-link active" href="#top" title="Dashboard">
              <span class="rail-code compact-only">DB</span>
              <span class="rail-glyph">DB</span>
              <span class="rail-label">Dashboard</span>
            </a>
            <a class="rail-link" href="#tickets" title="Operations">
              <span class="rail-code compact-only">OP</span>
              <span class="rail-glyph">OP</span>
              <span class="rail-label">Operations</span>
            </a>
            <a class="rail-link" href="#analytics" title="Inspectors">
              <span class="rail-code compact-only">IN</span>
              <span class="rail-glyph">IN</span>
              <span class="rail-label">Inspectors</span>
            </a>
            <a class="rail-link" href="/api" title="API Docs">
              <span class="rail-code compact-only">API</span>
              <span class="rail-glyph">AP</span>
              <span class="rail-label">API Docs</span>
            </a>
          </div>
          <div class="rail-spacer"></div>
          <div class="rail-avatar">
            <span class="rail-code compact-only">AI</span>
            <span class="rail-glyph">AI</span>
            <span class="rail-label">Agent Intel</span>
          </div>
        </aside>
      <section class="shell" id="top">
        <div class="topbar">
          <div class="hero-copy">
            <div class="hero-header">
              <div class="brand-row">
                <div class="brand-lockup">
                  <span class="brand-mark" aria-hidden="true"></span>
                  <span>TriageOS</span>
                </div>
                <label class="search-shell">
                  <span class="search-label">Search</span>
                  <input type="search" placeholder="Workflows, tickets, tools" />
                </label>
              </div>
              <div class="header-actions">
                <button class="header-icon theme-toggle" id="theme-toggle" type="button">Light Mode</button>
                <span class="profile-pill">
                  <span class="profile-avatar">LC</span>
                  <span class="profile-copy">
                    <strong>Lily Carter</strong>
                    <span id="service-meta">Loading metadata...</span>
                  </span>
                </span>
              </div>
            </div>
            <div class="eyebrow">
              <span class="status-dot"></span>
              Support Dashboard
            </div>
            <div class="headline">
              <h1>
                <span class="headline-mark">Dashboard</span>
                <span class="headline-sub">Enterprise support triage control center</span>
              </h1>
            </div>
            <div class="hero-grid">
              <div class="mini-card">
                <strong>Total Reward</strong>
                <span id="reward-text">0.00</span>
                <p>Live environment reward across the active episode.</p>
              </div>
              <div class="mini-card">
                <strong>Active Score</strong>
                <span id="score-text">0.01</span>
                <p>Model score and quality trend for the current queue.</p>
              </div>
              <div class="mini-card">
                <strong>Queue Health</strong>
                <span id="queue-health-text">No queue loaded</span>
                <p>Operational pressure across tickets, SLAs, and escalations.</p>
              </div>
              <div class="mini-card">
                <strong>Step Count</strong>
                <span id="steps-text">0</span>
                <p>Progress toward finish for the current workflow run.</p>
              </div>
            </div>
          </div>
          <div class="status-card">
            <div>
              <strong>Agent Workspace</strong>
              <span>Support operations overview</span>
              <p>Run one environment, inspect queue state, and step actions with a polished executive dashboard view.</p>
            </div>
            <div class="service-grid">
              <div class="service-metric">
                <strong>Mode</strong>
                <span id="task-text">billing_refund_easy</span>
              </div>
              <div class="service-metric">
                <strong>Assigned Team</strong>
                <span id="team-text">Unassigned</span>
              </div>
              <div class="service-metric">
                <strong>Status</strong>
                <span id="status-text">Ready</span>
              </div>
              <div class="service-metric">
                <strong>Apps</strong>
                <span id="apps-text">0</span>
              </div>
              <div class="service-metric">
                <strong>Done</strong>
                <span id="done-text">false</span>
              </div>
            </div>
            <ul class="status-list">
              <li><code>Reset</code> loads a fresh seeded scenario.</li>
              <li><code>Suggested Action</code> keeps the next move ready.</li>
              <li><code>Step</code> updates state, world summary, and tool results.</li>
            </ul>
          </div>
        </div>

        <div class="layout">
          <section class="playground">
            <section class="panel conversation-panel" id="messages">
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

            <div class="panel runner-panel" id="tickets">
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
                <div class="summary-card"><strong>Task Family</strong><span class="task-value">Live workflow controls</span></div>
                <div class="summary-card"><strong>Action State</strong><span>Ready for reset and manual JSON edits</span></div>
                <div class="summary-card"><strong>Session Type</strong><span>Single environment review console</span></div>
                <div class="summary-card"><strong>Output</strong><span>Trace, world summary, tools, schema</span></div>
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
                  <div class="button-row action-row" style="margin: 0 0 12px;">
                    <button class="primary" id="reset-btn" type="button">Reset</button>
                    <button class="primary" id="step-btn" type="button">Step</button>
                    <button id="state-btn" type="button">Get State</button>
                    <button id="schema-btn" type="button">Refresh Schema</button>
                  </div>
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

              <div class="pill" style="margin-top: 12px;">
                <span class="status-inline"><strong>Console</strong><span>Runner ready for manual actions</span></span>
              </div>
            </div>

            <div class="json-grid" id="analytics">
              <section class="json-box">
                <header><strong>Response Trace</strong><span id="response-kind">idle</span></header>
                <pre id="response-json">{}</pre>
              </section>
              <section class="json-box">
                <header><strong>Environment State</strong><span id="state-kind">idle</span></header>
                <pre id="state-json">{}</pre>
              </section>
            </div>
            <div class="json-grid" style="margin-top: 14px;" id="incidents">
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
              <span class="section-kicker">Menu</span>
              <h2>Navigation</h2>
              <div class="menu-list">
                <button class="menu-item active" type="button" data-target="top"><span><span class="menu-icon">DB</span> Dashboard</span><span>›</span></button>
                <button class="menu-item" type="button" data-target="tickets"><span><span class="menu-icon">TK</span> Tickets</span><span>12</span></button>
                <button class="menu-item" type="button" data-target="analytics"><span><span class="menu-icon">AN</span> Analytics</span><span>›</span></button>
                <button class="menu-item" type="button" data-target="incidents"><span><span class="menu-icon">IC</span> Incidents</span><span>›</span></button>
                <button class="menu-item" type="button" data-target="messages"><span><span class="menu-icon">MS</span> Messages</span><span>›</span></button>
                <button class="menu-item" type="button" data-target="settings"><span><span class="menu-icon">ST</span> Settings</span><span>›</span></button>
              </div>
            </div>

            <div class="panel overview-card support-card" id="settings">
              <span class="section-kicker">Subscription</span>
              <div class="support-box">
                <h3>Support Pro Workspace</h3>
                <p>Run all dashboards, OpenEnv tools, and incident surfaces from one premium enterprise console.</p>
                <a class="link-btn" href="#runner">Open runner</a>
              </div>
            </div>

            <div class="panel overview-card">
              <span class="section-kicker">Quick Access</span>
              <h2>Links And Endpoints</h2>
              <div class="link-grid">
                <a class="link-btn" href="/metadata" target="_blank" rel="noreferrer">Metadata</a>
                <a class="link-btn" href="/schema" target="_blank" rel="noreferrer">Schema</a>
                <a class="link-btn" href="/project-docs" target="_blank" rel="noreferrer">Docs</a>
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
      </div>
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
      const teamText = document.getElementById("team-text");
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
      const themeToggle = document.getElementById("theme-toggle");
      const railToggle = document.getElementById("rail-toggle");
      const menuButtons = Array.from(document.querySelectorAll(".menu-item[data-target]"));
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
        const reward = statePayload && statePayload.cumulative_reward != null
          ? Number(statePayload.cumulative_reward)
          : payload && payload.reward != null
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
        const focusedTicketId = statePayload && statePayload.focused_ticket_id ? statePayload.focused_ticket_id : null;
        const tickets = statePayload && Array.isArray(statePayload.tickets) ? statePayload.tickets : [];
        const focusedTicket = focusedTicketId
          ? tickets.find((ticket) => ticket.ticket_id === focusedTicketId)
          : tickets.length
            ? tickets[0]
            : null;
        const assignedTeam = focusedTicket && focusedTicket.assigned_team ? focusedTicket.assigned_team : null;
        teamText.textContent = assignedTeam ? String(assignedTeam).replaceAll("_", " ") : "Unassigned";
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

      const storedTheme = window.localStorage.getItem("triage-theme");
      const initialTheme = storedTheme === "light" ? "light" : "dark";
      document.body.setAttribute("data-theme", initialTheme);
      const storedSidebarState = window.localStorage.getItem("triage-sidebar-expanded");
      const initialSidebarExpanded = storedSidebarState === "true";
      document.body.classList.toggle("sidebar-expanded", initialSidebarExpanded);
      if (themeToggle) {
        themeToggle.textContent = initialTheme === "light" ? "Dark Mode" : "Light Mode";
        themeToggle.addEventListener("click", () => {
          const nextTheme = document.body.getAttribute("data-theme") === "light" ? "dark" : "light";
          document.body.setAttribute("data-theme", nextTheme);
          window.localStorage.setItem("triage-theme", nextTheme);
          themeToggle.textContent = nextTheme === "light" ? "Dark Mode" : "Light Mode";
        });
      }
      if (railToggle) {
        railToggle.setAttribute("aria-expanded", String(initialSidebarExpanded));
        railToggle.addEventListener("click", () => {
          const isExpanded = document.body.classList.toggle("sidebar-expanded");
          railToggle.setAttribute("aria-expanded", String(isExpanded));
          window.localStorage.setItem("triage-sidebar-expanded", String(isExpanded));
        });
      }

      menuButtons.forEach((button) => {
        button.addEventListener("click", () => {
          const targetId = button.getAttribute("data-target");
          const target = targetId ? document.getElementById(targetId) : null;
          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
          menuButtons.forEach((item) => item.classList.remove("active"));
          button.classList.add("active");
        });
      });

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


@app.get("/project-docs", response_class=HTMLResponse, include_in_schema=False)
async def project_docs() -> HTMLResponse:
    return HTMLResponse(
        '<!DOCTYPE html><html><head><title>Docs Build Required</title></head><body style="font-family:Segoe UI,sans-serif;padding:40px;"><h1>Project docs are not built yet.</h1><p>Build the local <code>documentation-customer_support</code> site to serve exact docs here.</p></body></html>'
    )


def _render_docs_home() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Support Triage Env Docs</title>
    <link rel="icon" href="data:," />
    <style>
      :root {
        color-scheme: light;
        --ifm-color-primary: #0d5c91;
        --ifm-color-primary-dark: #0b537f;
        --ifm-color-primary-darker: #0a4e78;
        --ifm-color-primary-darkest: #083f61;
        --ifm-color-primary-light: #0f65a3;
        --ifm-color-primary-lighter: #126cab;
        --ifm-color-primary-lightest: #1a7fc8;
        --ifm-background-color: #fffdf9;
        --ifm-navbar-background-color: rgba(255, 252, 247, 0.92);
        --ifm-footer-background-color: #f5efe5;
        --ink: #173049;
        --muted: #5d7188;
        --line: rgba(11, 59, 93, 0.1);
        --shadow: 0 24px 60px rgba(20, 44, 68, 0.1);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Segoe UI", "Aptos", sans-serif;
        color: var(--ink);
        background: var(--ifm-background-color);
      }
      .navbar {
        position: sticky;
        top: 0;
        z-index: 20;
        backdrop-filter: blur(12px);
        background: var(--ifm-navbar-background-color);
        border-bottom: 1px solid rgba(11, 59, 93, 0.08);
      }
      .navbar-inner {
        max-width: 1200px;
        margin: 0 auto;
        padding: 14px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }
      .navbar-brand {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        color: var(--ink);
        text-decoration: none;
        font-weight: 700;
      }
      .brand-mark {
        width: 34px;
        height: 34px;
        border-radius: 12px;
        background: linear-gradient(180deg, #0f65a3, #1a7fc8);
        box-shadow: 0 10px 24px rgba(13, 92, 145, 0.18);
      }
      .navbar-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }
      .navbar-nav a,
      .button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        padding: 0 16px;
        border-radius: 999px;
        border: 1px solid var(--line);
        text-decoration: none;
        color: var(--ink);
        background: rgba(255, 255, 255, 0.76);
        font-weight: 600;
      }
      .button--primary {
        border-color: transparent;
        background: linear-gradient(180deg, #0f65a3, #0d5c91);
        color: #fff;
        box-shadow: 0 14px 30px rgba(13, 92, 145, 0.22);
      }
      .button--secondary {
        color: var(--ifm-color-primary);
      }
      main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 30px 24px 56px;
      }
      .heroBanner {
        padding: 30px 0 10px;
      }
      .heroShell {
        display: grid;
        grid-template-columns: 1.05fr 0.95fr;
        gap: 18px;
        align-items: stretch;
      }
      .heroCopy,
      .heroPanel,
      .ribbon,
      .featureCard,
      .calloutBox {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.8);
        box-shadow: var(--shadow);
      }
      .heroCopy {
        padding: 30px;
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(13, 92, 145, 0.14);
        background: rgba(13, 92, 145, 0.06);
        color: var(--ifm-color-primary);
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      h1, h2, h3 {
        font-family: "Georgia", "Iowan Old Style", serif;
        letter-spacing: -0.02em;
      }
      .heroTitle {
        margin: 16px 0 10px;
        font-size: 54px;
        line-height: 0.98;
      }
      .heroSubtitle,
      .metricCard p,
      .metricTile span:last-child,
      .ribbon p,
      .featureCard p,
      .calloutBox p {
        color: var(--muted);
        line-height: 1.8;
      }
      .buttonRow {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 22px;
      }
      .heroPanel {
        padding: 22px;
        display: grid;
        gap: 14px;
      }
      .metricCard {
        padding: 18px;
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(13, 92, 145, 0.08), rgba(26, 127, 200, 0.05));
      }
      .metricCard span,
      .metricTile span:first-child,
      .sectionIntro p,
      .calloutLabel {
        display: block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--ifm-color-primary);
      }
      .metricCard strong {
        display: block;
        margin-top: 10px;
        font-size: 24px;
        line-height: 1.25;
      }
      .metricGrid,
      .featureGrid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }
      .metricTile,
      .featureCard {
        padding: 18px;
        border-radius: 20px;
      }
      .metricTile {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(11, 59, 93, 0.08);
      }
      .metricTile strong {
        display: block;
        margin-top: 8px;
        font-size: 17px;
      }
      .ribbonRow {
        margin-top: 18px;
      }
      .ribbon {
        padding: 18px 22px;
      }
      .ribbon span {
        display: block;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--ifm-color-primary);
      }
      .sectionIntro {
        margin: 28px 0 16px;
      }
      .sectionIntro h2 {
        margin: 10px 0 0;
        font-size: 38px;
      }
      .featureCard h3 {
        margin: 10px 0 8px;
        font-size: 26px;
      }
      .calloutSection {
        margin-top: 28px;
      }
      .calloutBox {
        padding: 24px;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 16px;
        align-items: center;
      }
      .calloutTitle {
        margin: 0;
        font-size: 34px;
      }
      .calloutActions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }
      .footer {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px 40px;
        color: var(--muted);
      }
      @media (max-width: 980px) {
        .heroShell,
        .metricGrid,
        .featureGrid,
        .calloutBox {
          grid-template-columns: 1fr;
        }
        .heroTitle {
          font-size: 42px;
        }
        .sectionIntro h2,
        .calloutTitle {
          font-size: 30px;
        }
      }
    </style>
  </head>
  <body>
    <header class="navbar">
      <div class="navbar-inner">
        <a class="navbar-brand" href="/project-docs">
          <span class="brand-mark" aria-hidden="true"></span>
          <span>Support Triage Env</span>
        </a>
        <nav class="navbar-nav">
          <a href="/project-docs/intro">Overview</a>
          <a href="/project-docs/hackathon-fit">Theme Fit</a>
          <a href="/project-docs/problem-statement">Problem Statement</a>
          <a href="/project-docs/pivot-strategy">Pivot Strategy</a>
          <a href="/">Dashboard</a>
        </nav>
      </div>
    </header>
    <main>
      <header class="heroBanner">
        <div class="heroShell">
          <div class="heroCopy">
            <div class="eyebrow">OpenEnv project docs</div>
            <h1 class="heroTitle">Support Triage Env Docs</h1>
            <p class="heroSubtitle">Detailed project documentation, evaluation logic, and hackathon positioning</p>
            <div class="buttonRow">
              <a class="button button--primary" href="/project-docs/intro">Start with the project overview</a>
              <a class="button button--secondary" href="/project-docs/hackathon-fit">See the best Round 2 theme fit</a>
            </div>
          </div>
          <div class="heroPanel">
            <div class="metricCard">
              <span>Primary fit</span>
              <strong>Theme 3.1: World Modeling</strong>
              <p>Professional workflow simulation with dynamic state, policy constraints, and real task sequencing.</p>
            </div>
            <div class="metricGrid">
              <div class="metricTile">
                <span>Current tasks</span>
                <strong>3+</strong>
                <span>Seeded families with deterministic grading and queue-state updates.</span>
              </div>
              <div class="metricTile">
                <span>Core loop</span>
                <strong>Reset - Step - State</strong>
                <span>OpenEnv-friendly execution flow for baselines and evaluators.</span>
              </div>
              <div class="metricTile">
                <span>Strong secondary fit</span>
                <strong>Long-horizon planning</strong>
                <span>Natural extension path through longer queues and delayed outcomes.</span>
              </div>
              <div class="metricTile">
                <span>Best pivot</span>
                <strong>Support ops control tower</strong>
                <span>Most compelling hackathon story built from the current repo foundation.</span>
              </div>
            </div>
          </div>
        </div>
        <div class="ribbonRow">
          <div class="ribbon">
            <span>What this site gives you</span>
            <p>A detailed walkthrough of the current Support_triage_env repo, a grounded analysis of how it matches the hackathon themes, and a practical plan to pivot it into a stronger finalist-style submission.</p>
          </div>
        </div>
      </header>

      <section>
        <div class="sectionIntro">
          <p>What the documentation covers</p>
          <h2>Built to help you explain the project and improve it</h2>
        </div>
        <div class="featureGrid">
          <article class="featureCard">
            <p class="calloutLabel">Project</p>
            <h3>Grounded enterprise workflow simulation</h3>
            <p>Support_triage_env already simulates realistic support queues, typed actions, policy constraints, and deterministic grading. That makes it a strong foundation instead of just a pitch concept.</p>
          </article>
          <article class="featureCard">
            <p class="calloutLabel">Theme fit</p>
            <h3>Best aligned with World Modeling plus Long Horizon</h3>
            <p>The current repo maps most naturally to Theme 3.1 because agents must maintain state, act safely in a professional workflow, and sequence actions against a partially observable queue.</p>
          </article>
          <article class="featureCard">
            <p class="calloutLabel">Submission strategy</p>
            <h3>Stronger if framed as a support operations control tower</h3>
            <p>The recommended pivot is to evolve the environment from single-ticket triage into a multi-team support command center with SLA clocks, policy drift, delayed outcomes, and internal specialist handoffs.</p>
          </article>
          <article class="featureCard">
            <p class="calloutLabel">Evaluation</p>
            <h3>Reward logic is already one of the project strengths</h3>
            <p>The repo includes deterministic graders, shaped rewards, penalties for unsafe behavior, and reproducible tasks. That is exactly the kind of measurable environment foundation judges usually want to see.</p>
          </article>
        </div>
      </section>

      <section class="calloutSection">
        <div class="calloutBox">
          <div>
            <p class="calloutLabel">Recommended positioning</p>
            <h2 class="calloutTitle">Pitch this as a professional support-operations world model, then extend it with longer horizons and multi-actor coordination.</h2>
          </div>
          <div class="calloutActions">
            <a class="button button--primary" href="/project-docs/problem-statement">Read the proposed problem statement</a>
            <a class="button button--secondary" href="/project-docs/pivot-strategy">Open the pivot roadmap</a>
          </div>
        </div>
      </section>
    </main>
    <div class="footer">Extracted from the referenced documentation source and rebuilt inside TriageOS.</div>
  </body>
</html>
"""


DOCS_ORDER = [
    "intro",
    "project-overview",
    "architecture",
    "environment-loop",
    "reward-and-evaluation",
    "training-and-submission",
    "hackathon-fit",
    "problem-statement",
    "pivot-strategy",
    "judging-and-demo",
]

DOCS_META = {
    "intro": {
        "title": "Overview",
        "section": "Overview",
        "description": "What Support_triage_env is, why it matters, and how this documentation is organized.",
        "content": """
<p>Support_triage_env is an OpenEnv-compatible customer support triage simulator. It evaluates and trains agents on realistic business workflows: reading a queue of support tickets, classifying the issue correctly, prioritizing urgent work, drafting policy-safe customer replies, routing tickets to the right internal team, and deciding whether to escalate or resolve.</p>
<h2>What already exists in the repo</h2>
<ul>
  <li>a typed action, observation, reward, and state model</li>
  <li>a simulator with <code>reset</code>, <code>step</code>, and <code>state</code></li>
  <li>seeded task families with deterministic graders</li>
  <li>an OpenEnv and FastAPI server</li>
  <li>a competition-style <code>inference.py</code> entrypoint</li>
  <li>synthetic dataset generation and a lightweight classifier baseline</li>
</ul>
<h2>Fast conclusion</h2>
<ol>
  <li><strong>Theme 3.1: World Modeling across professional tasks</strong></li>
  <li><strong>Theme 2: Long-Horizon Planning and Instruction Following</strong></li>
  <li><strong>Optional expansion into Theme 1: Multi-Agent Interactions</strong></li>
</ol>
<p>The best framing is: a policy-aware support operations environment where an agent manages a partially observable enterprise queue, coordinates routing and customer communication, and optimizes safe outcomes under delayed business impact.</p>
""",
    },
    "project-overview": {
        "title": "Project Overview",
        "section": "Project",
        "description": "A practical overview of the Support_triage_env repository and what it currently implements.",
        "content": """
<p>This project simulates a customer support operations workflow rather than a toy classification benchmark. The agent must operate inside an environment with a queue of tickets, typed actions, mutable ticket state, explicit policy hints, task-specific grading logic, and penalties for unsafe or low-quality decisions.</p>
<h2>What the agent can do</h2>
<ul>
  <li><code>view_ticket</code></li>
  <li><code>classify_ticket</code></li>
  <li><code>draft_reply</code></li>
  <li><code>request_info</code></li>
  <li><code>escalate_ticket</code></li>
  <li><code>resolve_ticket</code></li>
  <li><code>finish</code></li>
</ul>
<h2>Task families in the repo</h2>
<ul>
  <li><strong>billing_refund_easy</strong>: refund classification, safe reply, billing routing, clean resolution</li>
  <li><strong>export_outage_medium</strong>: outage handling, escalation judgment, and avoiding premature resolution</li>
  <li><strong>security_and_refund_hard</strong>: prioritization, urgent security handling, safe escalation, and secondary refund completion</li>
</ul>
<h2>Current strengths</h2>
<ul>
  <li>realistic business setting</li>
  <li>deterministic grading</li>
  <li>clear reward shaping</li>
  <li>OpenEnv server support</li>
  <li>inference entrypoint compatible with evaluator-style execution</li>
</ul>
""",
    },
    "architecture": {
        "title": "Architecture",
        "section": "Project",
        "description": "How the simulator, tasks, graders, server, and inference components fit together.",
        "content": """
<p>The implementation being documented lives inside <code>Support_triage_env/</code>. The important modules are models.py, tasks.py, graders.py, simulator.py, client.py, synthetic_dataset.py, training_data.py, train_classifier.py, server/app.py, and inference.py.</p>
<h2>System flow</h2>
<pre>task definition + seed
        ->
scenario generation
        ->
simulator reset
        ->
observation returned to agent
        ->
agent chooses typed action
        ->
simulator mutates ticket state
        ->
grader evaluates full state
        ->
reward + progress snapshot returned</pre>
<h2>Main architectural layers</h2>
<ul>
  <li><strong>Scenario generation</strong>: reproducible variations of each task family</li>
  <li><strong>Stateful environment execution</strong>: resets episodes, validates actions, updates ticket records, computes reward</li>
  <li><strong>Deterministic grading</strong>: checks category, priority, team assignment, reply quality, escalation quality, terminal action</li>
  <li><strong>Environment serving</strong>: <code>POST /reset</code>, <code>POST /step</code>, <code>GET /state</code>, <code>GET /metadata</code>, <code>GET /schema</code></li>
</ul>
""",
    },
    "environment-loop": {
        "title": "Environment Loop",
        "section": "Project",
        "description": "How reset, step, state, task structure, and partial observability work in the simulator.",
        "content": """
<p>The project follows a familiar environment pattern using reset, step, and state. This makes the environment usable for scripted baselines, model-driven rollouts, future RL or post-training pipelines, and server-based evaluation through OpenEnv.</p>
<h2>Observation design</h2>
<ul>
  <li><code>task</code></li>
  <li><code>instructions</code></li>
  <li><code>policy_hints</code></li>
  <li><code>queue</code></li>
  <li><code>focused_ticket</code></li>
  <li><code>last_action_result</code></li>
  <li><code>progress</code></li>
  <li><code>reward</code></li>
  <li><code>done</code></li>
</ul>
<h2>Current task progression</h2>
<ul>
  <li><strong>Billing refund</strong>: classify correctly, draft a safe apology and refund timeline, resolve with <code>refund_submitted</code></li>
  <li><strong>Export outage</strong>: classify as product bug, set high priority, route to engineering, reply with urgency-aware guidance, escalate instead of resolving</li>
  <li><strong>Security plus refund</strong>: prioritize security first, classify urgent takeover, escalate to <code>trust_safety</code>, then complete the billing refund task</li>
</ul>
""",
    },
    "reward-and-evaluation": {
        "title": "Reward and Evaluation",
        "section": "Project",
        "description": "How deterministic grading, shaped reward, and penalties are implemented.",
        "content": """
<p>The evaluation logic is implemented in code and tied directly to task expectations. The grader returns a grading snapshot with score, component contributions, penalties, satisfied requirements, outstanding requirements, and violations.</p>
<h2>Reward structure</h2>
<ul>
  <li>score delta from the previous step</li>
  <li>per-step cost</li>
  <li>repeated-action penalty</li>
  <li>invalid-action penalty</li>
</ul>
<h2>Why this evaluation is convincing</h2>
<ul>
  <li>deterministic</li>
  <li>interpretable</li>
  <li>decomposed into components</li>
  <li>aligned with business behavior</li>
  <li>safety aware</li>
</ul>
<p>The best next reward extensions are delayed business outcomes, queue-level metrics, tool-use quality, and policy drift handling.</p>
""",
    },
    "training-and-submission": {
        "title": "Training and Submission",
        "section": "Project",
        "description": "How the repo supports dataset generation, baselines, inference, and hackathon submission readiness.",
        "content": """
<p>The repository already includes synthetic scenario generation, combined training data generation, a lightweight classifier baseline, a local model-driven baseline runner, a competition-facing <code>inference.py</code>, and a submission validation shell script.</p>
<h2>Synthetic dataset pipeline</h2>
<ul>
  <li>ticket details</li>
  <li>task metadata</li>
  <li>policy hints</li>
  <li>expected routing</li>
  <li>expected terminal actions</li>
  <li>reply requirements</li>
  <li>forbidden phrases</li>
</ul>
<h2>What is still missing for Round 2</h2>
<p>The biggest missing artifact is a minimal post-training notebook or script using Unsloth or Hugging Face TRL.</p>
<h2>Best post-training story</h2>
<ol>
  <li>supervised warm start</li>
  <li>environment rollouts</li>
  <li>preference or RL-style refinement</li>
  <li>before/after comparison</li>
</ol>
""",
    },
    "hackathon-fit": {
        "title": "Hackathon Theme Fit",
        "section": "Hackathon Strategy",
        "description": "Detailed analysis of where Support_triage_env best fits among the Round 2 themes.",
        "content": """
<p>After reviewing the current project and the Round 2 themes, the strongest fit is Theme 3.1: World Modeling across professional tasks, followed by Theme 2: Long-Horizon Planning and Instruction Following, with Theme 1 as an optional expansion path.</p>
<h2>Why Theme 3.1 is the best fit</h2>
<ul>
  <li>the agent interacts with an environment instead of answering a single prompt</li>
  <li>tickets evolve over time</li>
  <li>actions change the world state</li>
  <li>the workflow is clearly professional and enterprise-oriented</li>
  <li>evaluation is grounded in business logic and safety policy</li>
</ul>
<h2>Fit matrix</h2>
<ul>
  <li>Theme 1: Medium</li>
  <li>Theme 2: Medium to strong</li>
  <li>Theme 3.1: Strongest</li>
  <li>Theme 3.2: Weak</li>
  <li>Theme 4: Weak to medium</li>
</ul>
""",
    },
    "problem-statement": {
        "title": "Submission-Ready Problem Statement",
        "section": "Hackathon Strategy",
        "description": "A refined hackathon problem statement built from the current Support_triage_env project.",
        "content": """
<p><strong>Recommended title:</strong> Support Operations Control Tower.</p>
<p>Build an OpenEnv environment in which an agent operates as a frontline support triage coordinator for an enterprise software company. The agent must inspect a partially observable support queue, classify and prioritize tickets, write safe and useful customer responses, route issues to the correct internal teams, and decide when cases should be escalated versus resolved.</p>
<h2>Capabilities of the agent</h2>
<ul>
  <li>read and interpret support ticket content</li>
  <li>infer issue category and urgency</li>
  <li>prioritize work across a queue</li>
  <li>produce policy-safe customer communication</li>
  <li>route issues to the correct internal team</li>
  <li>escalate incidents when frontline resolution is unsafe or insufficient</li>
  <li>preserve context across multiple steps</li>
  <li>recover from mistakes without repeated action loops</li>
</ul>
<p>The refined problem statement sounds like a serious enterprise workflow, supports longer horizons and richer reward shaping, and opens the door to multi-agent extensions.</p>
""",
    },
    "pivot-strategy": {
        "title": "Pivot Strategy",
        "section": "Hackathon Strategy",
        "description": "How to evolve the current problem statement into a more unique and competitive Round 2 submission.",
        "content": """
<p>Do not abandon the current project. Instead, pivot it upward into <strong>Support Operations Control Tower</strong>.</p>
<h2>Recommended pivot path</h2>
<ol>
  <li><strong>Strengthen the current single-agent world</strong>: larger mixed queues, SLA timers, enterprise account weighting, reopen events, richer task families</li>
  <li><strong>Add multi-actor behavior</strong>: engineering triage, billing specialist, trust and safety reviewer, customer simulator, support manager</li>
  <li><strong>Add drift and delayed consequences</strong>: routing schema changes, policy updates, evolving templates, downstream outcomes arriving several steps later</li>
</ol>
<h2>Concrete features that improve your chances</h2>
<ul>
  <li>queue-level objectives</li>
  <li>tool-like internal systems</li>
  <li>policy and schema drift</li>
  <li>oversight layer</li>
  <li>before versus after training evidence</li>
</ul>
""",
    },
    "judging-and-demo": {
        "title": "Judging and Demo",
        "section": "Hackathon Strategy",
        "description": "How to map the project to the judging criteria and present it effectively.",
        "content": """
<p>The submission should show OpenEnv usage, a minimal training script or notebook using Unsloth or HF TRL, and a short public-facing explanation asset such as a mini-blog or short video.</p>
<h2>Recommended 3-minute pitch flow</h2>
<ol>
  <li>Explain the real-world problem: enterprise support queues are high stakes and safe routing matters</li>
  <li>Show the environment: reset a task, inspect the queue, step through actions, and show score/progress changing live</li>
  <li>Show evidence of learning and the future path: before/after metrics, meaningful reward model, and extensions to longer-horizon multi-agent workflows</li>
</ol>
<h2>Best demo narrative</h2>
<p>The most memorable demo is not “our agent got the right label,” but “our agent handled a realistic support queue, prioritized a security incident over a routine billing issue, used safe communication, routed work correctly, and improved measurable reward after training.”</p>
""",
    },
}


def _render_docs_page(slug: str) -> str:
    doc = DOCS_META[slug]
    current_index = DOCS_ORDER.index(slug)
    prev_slug = DOCS_ORDER[current_index - 1] if current_index > 0 else None
    next_slug = DOCS_ORDER[current_index + 1] if current_index < len(DOCS_ORDER) - 1 else None
    prev_link = (
        f'<a class="pager-link" href="/project-docs/{prev_slug}"><span>Previous</span><strong>{DOCS_META[prev_slug]["title"]}</strong></a>'
        if prev_slug
        else ""
    )
    next_link = (
        f'<a class="pager-link" href="/project-docs/{next_slug}"><span>Next</span><strong>{DOCS_META[next_slug]["title"]}</strong></a>'
        if next_slug
        else ""
    )
    sections = ["Project", "Hackathon Strategy"]
    sidebar_html = []
    for section in sections:
        items = []
        for item_slug in DOCS_ORDER:
            item = DOCS_META[item_slug]
            if item["section"] != section and not (section == "Project" and item_slug == "intro"):
                continue
            active = " active" if item_slug == slug else ""
            items.append(
                f'<a class="sidebar-link{active}" href="/project-docs/{item_slug}">{item["title"]}</a>'
            )
        if items:
            section_label = "Overview" if section == "Project" else section
            sidebar_html.append(
                f'<div class="sidebar-group"><strong>{section_label}</strong>{"".join(items)}</div>'
            )
    return f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{doc["title"]} | TriageOS Docs</title>
    <link rel="icon" href="data:," />
    <style>
      :root {{
        color-scheme: light;
        --bg: #fffdf9;
        --panel: rgba(255, 255, 255, 0.9);
        --line: rgba(11, 59, 93, 0.1);
        --ink: #173049;
        --muted: #5d7188;
        --accent: #0d5c91;
        --heading: Georgia, "Iowan Old Style", serif;
        --body: "Segoe UI", Aptos, sans-serif;
        --shadow: 0 22px 60px rgba(20, 44, 68, 0.08);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: var(--body);
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(13, 92, 145, 0.08), transparent 24%),
          radial-gradient(circle at bottom right, rgba(26, 127, 200, 0.08), transparent 22%),
          linear-gradient(180deg, #fffdf9 0%, #f7f2e9 100%);
      }}
      .topbar {{
        position: sticky;
        top: 0;
        z-index: 20;
        backdrop-filter: blur(12px);
        background: rgba(255, 252, 247, 0.92);
        border-bottom: 1px solid var(--line);
      }}
      .topbar-inner {{
        max-width: 1280px;
        margin: 0 auto;
        padding: 14px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }}
      .brand {{
        display: inline-flex;
        align-items: center;
        gap: 12px;
        color: var(--ink);
        font-weight: 700;
        text-decoration: none;
      }}
      .brand-mark {{
        width: 32px;
        height: 32px;
        border-radius: 12px;
        background: linear-gradient(180deg, #0f65a3, #1a7fc8);
        box-shadow: 0 10px 24px rgba(13, 92, 145, 0.18);
      }}
      .top-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }}
      .top-actions a {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 40px;
        padding: 0 14px;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.72);
        color: var(--ink);
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
      }}
      .layout {{
        max-width: 1280px;
        margin: 0 auto;
        padding: 28px 24px 48px;
        display: grid;
        grid-template-columns: 280px minmax(0, 1fr);
        gap: 20px;
      }}
      .sidebar,
      .content {{
        border: 1px solid var(--line);
        border-radius: 28px;
        background: var(--panel);
        box-shadow: var(--shadow);
      }}
      .sidebar {{
        position: sticky;
        top: 78px;
        align-self: start;
        padding: 20px;
      }}
      .sidebar h2,
      .content h1,
      .content h2,
      .content h3 {{
        font-family: var(--heading);
        letter-spacing: -0.03em;
      }}
      .sidebar h2 {{
        margin: 0 0 16px;
        font-size: 28px;
      }}
      .sidebar-group + .sidebar-group {{
        margin-top: 18px;
      }}
      .sidebar-group strong {{
        display: block;
        margin-bottom: 8px;
        color: var(--accent);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .sidebar-link {{
        display: block;
        padding: 10px 12px;
        border-radius: 14px;
        color: var(--muted);
        text-decoration: none;
        font-weight: 600;
      }}
      .sidebar-link.active {{
        background: rgba(13, 92, 145, 0.08);
        color: var(--accent);
      }}
      .content {{
        padding: 30px;
      }}
      .eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(13, 92, 145, 0.14);
        background: rgba(13, 92, 145, 0.06);
        color: var(--accent);
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .content h1 {{
        margin: 18px 0 8px;
        font-size: 48px;
        line-height: 1;
      }}
      .lead {{
        margin: 0 0 22px;
        color: var(--muted);
        font-size: 17px;
        line-height: 1.8;
      }}
      .markdown p,
      .markdown li {{
        color: var(--muted);
        line-height: 1.85;
        font-size: 16px;
      }}
      .markdown h2 {{
        margin: 28px 0 10px;
        font-size: 30px;
      }}
      .markdown ul,
      .markdown ol {{
        padding-left: 22px;
      }}
      .markdown pre {{
        padding: 16px;
        border-radius: 18px;
        border: 1px solid var(--line);
        background: #f3f6fb;
        color: #26405b;
        overflow: auto;
      }}
      .pager {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        margin-top: 28px;
      }}
      .pager-link {{
        display: block;
        padding: 18px;
        border-radius: 20px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.72);
        text-decoration: none;
      }}
      .pager-link span {{
        display: block;
        color: var(--accent);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .pager-link strong {{
        display: block;
        margin-top: 8px;
        color: var(--ink);
        font-size: 18px;
      }}
      @media (max-width: 980px) {{
        .layout {{
          grid-template-columns: 1fr;
        }}
        .sidebar {{
          position: static;
        }}
        .pager {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <header class="topbar">
      <div class="topbar-inner">
        <a class="brand" href="/project-docs">
          <span class="brand-mark" aria-hidden="true"></span>
          <span>TriageOS Docs</span>
        </a>
        <nav class="top-actions">
          <a href="/project-docs">Docs Home</a>
          <a href="/docs">FastAPI Docs</a>
          <a href="/api">API Page</a>
          <a href="/">Dashboard</a>
        </nav>
      </div>
    </header>
    <main class="layout">
      <aside class="sidebar">
        <h2>Documentation</h2>
        {''.join(sidebar_html)}
      </aside>
      <article class="content">
        <div class="eyebrow">{doc["section"]}</div>
        <h1>{doc["title"]}</h1>
        <p class="lead">{doc["description"]}</p>
        <div class="markdown">
          {doc["content"]}
        </div>
        <div class="pager">
          {prev_link}
          {next_link}
        </div>
      </article>
    </main>
  </body>
</html>
"""


@app.get("/project-docs/{slug}", response_class=HTMLResponse, include_in_schema=False)
async def project_docs_page(slug: str) -> HTMLResponse:
    return HTMLResponse(
        '<!DOCTYPE html><html><head><title>Docs Build Required</title></head><body style="font-family:Segoe UI,sans-serif;padding:40px;"><h1>Project docs are not built yet.</h1><p>Build the local <code>documentation-customer_support</code> site to serve exact docs pages here.</p></body></html>',
        status_code=404,
    )


@app.get("/api", response_class=HTMLResponse, include_in_schema=False)
async def api_landing() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>TriageOS API</title>
    <style>
      :root {
        color-scheme: dark;
        --bg: #0a0d14;
        --panel: rgba(16, 21, 32, 0.94);
        --line: rgba(162, 180, 212, 0.12);
        --ink: #f4f7fb;
        --muted: #98a6bc;
        --accent: #7d8cff;
        --accent-2: #56d6ff;
        --shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(125, 140, 255, 0.18), transparent 24%),
          radial-gradient(circle at bottom right, rgba(86, 214, 255, 0.12), transparent 22%),
          linear-gradient(180deg, #0a0d14 0%, #101521 100%);
      }
      main {
        max-width: 1180px;
        margin: 0 auto;
        padding: 40px 24px 56px;
      }
      .hero {
        padding: 32px;
        border-radius: 28px;
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(15, 20, 31, 0.98), rgba(11, 15, 24, 0.98));
        box-shadow: var(--shadow);
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid rgba(125, 140, 255, 0.18);
        background: rgba(125, 140, 255, 0.1);
        color: #dbe3ff;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
      }
      h1 {
        margin: 18px 0 12px;
        font-size: 52px;
        line-height: 0.95;
        letter-spacing: -0.05em;
      }
      .sub {
        max-width: 760px;
        margin: 0;
        color: var(--muted);
        font-size: 16px;
        line-height: 1.8;
      }
      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
      }
      .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 48px;
        padding: 0 18px;
        border-radius: 14px;
        border: 1px solid var(--line);
        color: var(--ink);
        text-decoration: none;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.04);
      }
      .btn.primary {
        border-color: transparent;
        background: linear-gradient(180deg, #6d7cff, #5262f1);
        color: white;
        box-shadow: 0 14px 28px rgba(82, 98, 241, 0.28);
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin-top: 22px;
      }
      .card {
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.04);
      }
      .card strong {
        display: block;
        font-size: 12px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
      }
      .card span {
        display: block;
        margin-top: 10px;
        font-size: 22px;
        font-weight: 700;
      }
      .card p {
        margin: 10px 0 0;
        color: var(--muted);
        line-height: 1.7;
      }
      .stack {
        display: grid;
        grid-template-columns: 1.15fr 0.85fr;
        gap: 16px;
        margin-top: 18px;
      }
      .panel {
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 22px;
        background: rgba(255, 255, 255, 0.04);
      }
      .panel h2 {
        margin: 0 0 12px;
        font-size: 22px;
      }
      .panel p, .panel li, .code {
        color: var(--muted);
      }
      ul {
        margin: 0;
        padding-left: 18px;
      }
      li + li {
        margin-top: 8px;
      }
      .code {
        margin-top: 14px;
        padding: 14px;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(8, 10, 16, 0.84);
        font-family: Consolas, "SFMono-Regular", monospace;
        white-space: pre-wrap;
      }
      @media (max-width: 980px) {
        .grid, .stack {
          grid-template-columns: 1fr;
        }
        h1 {
          font-size: 40px;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <span class="eyebrow">OpenEnv API Surface</span>
        <h1>TriageOS Developer Portal</h1>
        <p class="sub">
          Explore the support triage environment through schema-aware HTTP endpoints, interactive docs,
          and OpenAPI JSON. This surface is designed for hackathon demos, integrations, and agent testing.
        </p>
        <div class="actions">
          <a class="btn primary" href="/project-docs">Open Project Docs</a>
          <a class="btn" href="/docs">FastAPI Interactive Docs</a>
          <a class="btn" href="/openapi.json">View OpenAPI JSON</a>
          <a class="btn" href="/metadata">Metadata</a>
          <a class="btn" href="/schema">Schema</a>
          <a class="btn" href="/">Back To Dashboard</a>
        </div>

        <div class="grid">
          <article class="card">
            <strong>Runtime</strong>
            <span>OpenEnv HTTP</span>
            <p>Typed environment server exposing reset, step, state, metadata, and schema.</p>
          </article>
          <article class="card">
            <strong>Use Case</strong>
            <span>Support Triage</span>
            <p>Billing, incident, trust, policy, and queue-state workflows in one environment.</p>
          </article>
          <article class="card">
            <strong>Mode</strong>
            <span>Agent Testing</span>
            <p>Built for controlled multi-step evaluation with observable reward and score traces.</p>
          </article>
        </div>

        <div class="stack">
          <section class="panel">
            <h2>Core Endpoints</h2>
            <ul>
              <li><code>POST /reset</code> starts a new seeded task episode.</li>
              <li><code>POST /step</code> applies one environment action.</li>
              <li><code>GET /state</code> returns current environment state.</li>
              <li><code>GET /metadata</code> returns environment metadata.</li>
              <li><code>GET /schema</code> returns model/schema info.</li>
            </ul>
            <div class="code">from support_triage_env import SupportTriageEnv

env = SupportTriageEnv(base_url="http://127.0.0.1:8000")
await env.connect()</div>
          </section>

          <section class="panel">
            <h2>Why Use This Page</h2>
            <p>
              Use the interactive docs for manual request testing, OpenAPI JSON for integrations, and
              metadata/schema endpoints for quick environment introspection during demos or debugging.
            </p>
            <div class="code">Recommended flow:
1. Reset an episode
2. Inspect state
3. Send step actions
4. Track reward + final score</div>
          </section>
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
