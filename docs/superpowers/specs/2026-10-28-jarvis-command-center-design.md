# JARVIS Command Center — Design Spec

**Date:** 2026-10-28  
**Status:** Draft for user review  
**Owner:** Dr Chandan Kumar  
**Depends on:** STARK OS / JARVIS on box + `chandan`; Phase 1 Jarvis3D (`apps/windows-3d`) merged to `main` at `7a0df34`

## Goal

Ship a Windows Command Center that **looks and works like** the approved HUD mock (sidebar, AI Core, agents, timeline, feed, system gauges, memory map, LLM grid, voice, quick commands). Every tile is **fully live** — no decorative stubs. Host the project on **GitHub** and research open-source HUD/dashboard patterns there before implementation.

## Decisions (locked in design chat)

| Decision | Choice |
|---|---|
| Timing | Phase 2 after Phase 1 3D desk (desk kept) |
| Scope | Entire mock as one release |
| Approach | **A** — new WebView2 HTML/CSS/JS Command Center as main Windows shell |
| Stubs | **None** — every tile fully live |
| LLM / Agents backends | Real API keys (Claude, OpenAI, Gemini, Groq, …) via vault |
| Active Agents | Six **fixed roles** with own prompts/tools calling those APIs |
| Packaging | New main `Jarvis.exe` Command Center; archive/rename current flat panel; keep `Jarvis3D.exe` optional |
| GitHub | Research HUD repos **and** host the JARVIS project there |

## Non-goals (this release)

- Replacing Grok Bot / STARK OS kernel on the box  
- Merging Jarvis3D into the Command Center (3D stays a separate optional exe)  
- Cinema targeting reticles or strobes  
- Remote-hosted UI (must stay local / `127.0.0.1`)  
- Committing API keys or secrets to git  

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Jarvis.exe (PyInstaller)                               │
│  pywebview → WebView2                                   │
│       │                                                 │
│       ▼                                                 │
│  bundled ui/  (HTML/CSS/JS Command Center HUD)          │
│       │  js bridge                                      │
│       ▼                                                 │
│  command_center bridge (Python)                         │
│       ├── panel_api / voice / scripts/win (existing)    │
│       ├── host metrics (CPU/RAM/Disk)                   │
│       ├── audit / STATE / brief / calendar              │
│       ├── memory index (on-disk JARVIS memory files)    │
│       ├── LLM providers (vault keys → live probes)      │
│       └── Agent workers (6 fixed roles → LLM + tools) │
└─────────────────────────────────────────────────────────┘
```

- **Shell:** pywebview EdgeChromium/WebView2; load `ui/` via local HTTP (`http_server=True`), same lesson as Jarvis3D.  
- **UI:** Pixel-close to the mock; Stark palette (bg `#04070b`, panel `#0b2233`, cyan `#38d4ff`, text `#e4f6ff`, gold `#ff9d2e`, muted `#7a8fa8`, danger `#ff3b30`, ok `#3dff9a`). Gold only for Mute / Quiet / R3.  
- **AI Core sphere:** Local canvas/Three decorative viz driven by live health list (not a fake status).  
- **Bridge contract:** JSON-safe `{ok, data?, error?}` methods; never throw across the JS boundary.  
- **GitHub:** Create/connect remote for this repo; feature branch + PR workflow; research open-source HUD dashboards for layout/CSS patterns only (license-check before reuse).

## UI map (live behavior)

| Area | Behavior |
|---|---|
| Left nav (10 items) | Real routes; badges from live counts (tasks, conversations, skills) |
| Header | Live clock; SYSTEM STATUS from POLICY/STATE; search filters Live Feed |
| AI Core + health list | Sphere local; list from policy, quiet hours, voice/mute, agents running, LLMs connected, system optimal |
| Active Agents (6) | Coding, Research, Memory, Browser, Task, System — start/stop; Active/Standby from real workers; each calls LLM APIs with role prompt + tool allowlist under R2/R3 |
| Mission Timeline | Live calendar events + brief-derived blocks |
| Live Intelligence Feed | Audit JSONL + workday/session receipts + agent events |
| System Monitor | Live CPU / RAM / Disk from Windows host APIs |
| Memory Insights | Live graph/counts from on-disk JARVIS memory / STATE / journal |
| LLM Status | Live probe per configured provider; Connected only if ping succeeds |
| Voice / Talk to JARVIS | TTS + mute existing; STT via Windows speech recognition into commands |
| Quick Commands | Session Start, Open Calendar, Start Voice Chat, Run Workflow / Dry-run; **R3** before real workday or destructive workflow |

## Live backends

### LLM providers
- Keys only from vault / host-env (`JARVIS_*_API_KEY` or vault fill) — never in UI or git.  
- Providers at minimum: Anthropic (Claude), OpenAI, Google (Gemini), Groq; extensible config file for Cursor/Copilot/Ollama as local probes where applicable.  
- Tile state = last probe result (success / auth error / network error).

### Six fixed agents
| Role | Intent (high level) | Tools (initial allowlist) |
|---|---|---|
| Coding | Code/explain/patch in JARVIS_ROOT allowlisted paths | read/search files, propose diffs (R3 to apply) |
| Research | Web/doc research summaries | web fetch allowlist, summarize |
| Memory | Query/update JARVIS memory notes | memory read/write (R2/R3 per POLICY) |
| Browser | Allowlisted browser control | existing Day 4–5 allowlist |
| Task | Tasks / checklist / Notion if connected | create/list tasks |
| System | Host health, POLICY status, workday dry | metrics, status, dry-run only by default |

Workers are local processes/threads managed by the host; UI reflects true Active/Standby.

### Memory Insights
- Source of truth: on-disk JARVIS memory/STATE/journal (and shared memory exports if present).  
- Counts and graph edges derived from real files — empty state if none.

### Voice
- TTS: existing `voice` module.  
- STT: Windows speech recognition; failed hear → clear banner, no fake success.

### System / feed / timeline
- Metrics: `psutil` or Win APIs on chandan.  
- Feed: append-only audit + agent event stream.  
- Timeline: Google Calendar connector when available + today’s brief.

## Risk & POLICY

- R1 auto-log; R2 preview / standing POLICY; R3 every time for real workday, applying code diffs, spending new API budget thresholds, first use of a new provider key; R4 typed confirm + rollback for destructive system actions.  
- Agents never expand their own allowlist.  
- Offline: app opens; network tiles show real failures (red), never fake Connected/Active.

## Packaging & repo

- **Output:** `C:\Users\rajk1\jarvis\apps\Jarvis.exe` (Command Center) + Desktop shortcut; `Jarvis3D.exe` remains.  
- Current CustomTkinter panel: rename/archive under `apps/windows-panel` (still importable as `panel_api` / `voice`).  
- Icon: helmet faceplate (existing).  
- GitHub: host jarvis; PRs for Command Center work; document WebView2 Evergreen requirement.

## Testing / done when (chandan)

1. Double-click Command Center `Jarvis.exe` → mock layout offline shell loads.  
2. Every left-nav destination opens a real page (not a dead link).  
3. Home tiles all live: gauges move, feed scrolls from audit, timeline from calendar/brief, memory counts from disk, LLM tiles match real probes, agents start/stop with real API calls.  
4. Talk to JARVIS listens (STT) and TTS replies; Mute works.  
5. Quick Commands work; real workday still R3.  
6. No secrets in git; `Jarvis3D.exe` still opens.  
7. Repo is on GitHub with the feature history.

## Open implementer choices (non-blocking)

- Exact CSS approach (vanilla vs small component set) after GitHub HUD research.  
- Agent worker isolation (thread vs subprocess).  
- Whether Ollama appears as a first-class local provider in v1 config.

## Later (explicitly not this release)

- Folding Skills/POLICY/Logs tabs into 3D plates  
- Single merged 3D+Command Center exe  
- Multi-user / cloud-hosted Command Center  

