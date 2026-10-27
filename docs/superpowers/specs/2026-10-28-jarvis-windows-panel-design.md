# JARVIS Windows Control Panel — Design

Date: 2026-10-28  
Status: Draft for user review  
Owner: Dr Chandan kumar / IRON MAN · JARVIS  
Host target: Windows desktop `chandan` (`C:\Users\rajk1\jarvis`)

## Goal

Ship a **standalone `.exe`** Stark-HUD control panel that runs **fully offline** against the local JARVIS tree. Double-click; no Python install required for the end user. No Grok Bot chat bridge in v1.

## Decisions (approved)

| Decision | Choice |
|---|---|
| Purpose | Full control panel — skills, POLICY, logs, apps |
| Packaging | Standalone `.exe` (PyInstaller) |
| Connectivity | Local only — read/write jarvis root; offline OK |
| Look | Stark HUD — dark, cyan/gold |
| Stack | Python 3 + CustomTkinter → freeze with PyInstaller |

## Architecture

```
Jarvis.exe
  └─ CustomTkinter HUD (apps/windows-panel/)
       └─ panel_api (thin Python facade)
            ├─ scripts/win/*.py  (session_start, workday_start, brief, block_delete, lib_jarvis)
            └─ files under JARVIS_ROOT
                 STATE.md · POLICY.yaml · host/ · skills/ · logs/ · reports/
```

- **JARVIS_ROOT discovery:** (1) folder containing the `.exe` if it looks like a jarvis tree, (2) else `C:\Users\rajk1\jarvis`, (3) else a folder picker. Refuse to run without a valid root (`STATE.md` + `POLICY.yaml` present).
- **Write boundary:** never write outside JARVIS_ROOT except launching allowlisted apps from POLICY.
- **Risk gates:** POLICY edits, skill runs that write, and app launches are **R3** — in-app confirm dialog before action. `block_delete` remains authoritative; the panel never bypasses it.
- **Repo layout:** source lives at `apps/windows-panel/` in the jarvis repo; built artifact at `apps/Jarvis.exe` (and Desktop shortcut on install).

## Screens (v1)

One main window; left nav; Stark HUD chrome (dark background, cyan accents, gold highlights).

1. **Home** — status strip (install path, POLICY present, quiet-hours flag if detectable), today’s brief preview from `reports/YYYY-MM-DD.md`, buttons: **Start Workday**, **Session Start**, **Dry-run**.
2. **Skills** — enumerate `skills/*` with short description from each skill’s docs; **Run** for read-only skills without confirm; write/launch skills require R3 confirm.
3. **POLICY** — view `POLICY.yaml` and `host/permission-rules.md`; **Edit** with R3 confirm; before save, copy previous file to `logs/policy-backups/POLICY-YYYYMMDD-HHMMSS.yaml`.
4. **Logs** — list/tail `logs/` and audit JSONL; filter by day; open files from `reports/`.
5. **Apps** — show allowlisted apps from POLICY; **Launch** with R3 confirm; show restricted/blocked paths read-only.
6. **STATE** — read-only view of `STATE.md` in v1 (no in-panel STATE writes unless a later revision adds an approved “mark decision” path).

### Explicitly out of scope for v1

- Grok Bot / chat bridge
- System tray / always-on notifications
- Auto-update
- Git / Git Bash install wizard
- Remote connectors (Gmail, Calendar) inside the exe

## Data flow

| Action | Path | Gate |
|---|---|---|
| Load Home | read STATE, POLICY meta, today’s report | none |
| Session Start / Workday / Dry-run | call `scripts/win/*.py` via subprocess or import | Dry-run none; Workday R3 confirm |
| List / run skill | read `skills/`; invoke documented entry | write/launch → R3 |
| Save POLICY | backup then overwrite | R3 + backup |
| Launch app | POLICY allowlist only | R3 |
| Delete | always through `block_delete` | blocked outside fixtures |

Every successful or refused write/launch appends one **audit JSONL** line: `{ts_ist, actor: "windows-panel", action, path, result, detail}`.

## Error handling

- Missing / invalid JARVIS_ROOT → picker; no silent default to a random folder.
- Subprocess / script failure → red HUD banner + full stderr copied into Logs view; no automatic retry of destructive steps.
- Delete outside fixtures → still refused by `block_delete`; panel surfaces the refusal message.
- Corrupt POLICY YAML on load → show error, keep last-known-good view, refuse Save until parseable.

## Packaging & ship

1. Develop under `apps/windows-panel/` (`main.py`, `panel_api.py`, `ui/*.py`, `requirements.txt`).
2. Build: `pyinstaller --onefile --windowed --name Jarvis …` (Windows build preferred on `chandan`; box may cross-check sources only).
3. Install: copy `Jarvis.exe` → `C:\Users\rajk1\jarvis\apps\Jarvis.exe`; create Desktop shortcut “JARVIS”.
4. End user: double-click; no Python required.

## Acceptance / smoke (on `chandan`)

1. Double-click `Jarvis.exe` → Home loads with today’s brief or clear empty state.
2. Dry-run Workday → exit 0, banner success, audit line written.
3. POLICY tab opens YAML; cancel edit does not write.
4. Attempt delete of `STATE.md` via any panel path → blocked.
5. Apps tab lists allowlist; Launch of non-allowlisted name impossible from UI.

## Test plan

- **Automated (box or chandan):** unit tests for `panel_api` root discovery and audit append (no GUI).
- **Manual:** smoke list above on `chandan` after PyInstaller build.

## Follow-ups (not v1)

- Optional Grok Bot bridge (local brief already exists; live calendar/mail stay in chat until then).
- System tray helper.
- STATE “mark decision” writes with R3.
