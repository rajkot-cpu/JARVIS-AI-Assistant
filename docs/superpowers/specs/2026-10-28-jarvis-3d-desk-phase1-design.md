# JARVIS 3D Desk (Phase 1) — Design

Date: 2026-10-28  
Status: Draft for user review  
Owner: Dr Chandan kumar / IRON MAN · JARVIS  
Host target: Windows desktop `chandan` (`C:\Users\rajk1\jarvis`)

## Goal

Ship **`Jarvis3D.exe`**: a local-only Iron Man–style holographic desk shell (WebView2 + Three.js) with floating panels, depth, and orbit. Phase 1 wires **Home/status only** — live status, today’s brief, Session Start, Dry-run Workday, Mute — with R3 confirm before real Start Workday. Flat **`Jarvis.exe`** remains for Skills / POLICY / Logs / Apps / STATE until later phases.

## Decisions (approved)

| Decision | Choice |
|---|---|
| Long-term vision | Full Iron Man desk (floating 3D panels, maps, orbiting widgets) |
| Phase 1 scope | 3D holographic desk shell → Home/status + Home actions |
| Runtime | Standalone `Jarvis3D.exe`: WebView2 host + Three.js UI |
| Connectivity | Local only — same `JARVIS_HOME` / jarvis root; no cloud |
| Backend | Reuse `panel_api` / `scripts\win` (audit + POLICY unchanged) |
| Dual apps | Keep `Jarvis.exe` for non-Home tabs in Phase 1 |
| Phase 1 actions | Status + brief + Session Start / Dry-run Workday / Mute; Start Workday behind R3 |
| Approach | **A** — thin WebView2 host + Three.js desk (not Electron; not embed-in-CustomTkinter) |

## Out of scope (Phase 1)

- Maps, orbiting analytics widgets, full multi-panel Iron Man desk beyond the three plates below
- Conversational voice chat / LLM bridge
- Skills, POLICY editor, Logs, Apps, STATE tabs inside the 3D shell
- Replacing or removing `Jarvis.exe`
- Cinema strobes, fake targeting reticles, invented live data presented as real

## Architecture

```
Jarvis3D.exe
  └─ Host (Python + pywebview / WebView2 preferred)
       ├─ Resolves JARVIS_HOME (same rules as windows-panel)
       ├─ Loads bundled local UI (no remote URLs)
       └─ JS ↔ host bridge
            └─ Shared panel facade (panel_api or extracted shared module)
                 ├─ scripts/win/*.py  (session_start, workday_start, brief, …)
                 ├─ voice prefs (mute)
                 └─ files under JARVIS_ROOT
                      STATE.md · POLICY.yaml · logs/audit.jsonl · reports/

Jarvis.exe (unchanged role in Phase 1)
  └─ CustomTkinter control panel — Skills / POLICY / Logs / Apps / STATE
```

### Host responsibilities

1. Resolve jarvis root (`JARVIS_HOME`, exe parent heuristics matching today’s panel).
2. Open a frameless or dark chrome window; set helmet faceplate icon.
3. Serve or load UI only from bundled `apps/windows-3d/ui/` (or equivalent).
4. Expose bridge methods listed below; never fetch the open web for UI assets in Phase 1.
5. Optional: SAPI TTS for action OK / error lines (nice-to-have if host can share `voice.py`; banner-only is acceptable if TTS packing is costly).

### Bridge (JS → host)

| Method | Behavior |
|---|---|
| `getStatus()` | Same fields as panel Home status strip / one-read |
| `getBrief()` | Today’s `reports/YYYY-MM-DD.md` text or empty |
| `sessionStart()` | Run session_start via panel_api |
| `workday({ dry })` | Dry-run or real workday_start; real path only after R3 |
| `setMute(bool)` / `getMute()` | Local mute pref |

Returns `{ ok, data?, error? }`. Failures surface on the Status plate (danger color) and append audit as today’s scripts already do.

### Risk gates

| Action | Gate |
|---|---|
| getStatus / getBrief / getMute | R1 (read) |
| Session Start / Dry-run Workday | Existing script risk; audited |
| Mute | Local pref only |
| Start Workday (`dry=false`) | **R3** confirm in UI before bridge call |

No new privileges beyond what `Jarvis.exe` Home already allows. No POLICY write, no allowlisted app launch from Jarvis3D in Phase 1.

## Scene & UI

- **Palette:** bg `#04070b`, panel glass on `#0b2233`, cyan `#38d4ff`, frost text `#e4f6ff`, gold `#ff9d2e` (Mute / Quiet / R3 title only), danger `#ff3b30`, muted `#7a8fa8`, ok `#3dff9a`.
- **Camera:** mouse-drag orbit, wheel zoom; slow idle optional; ≤3 flashes/sec if any pulse.
- **Plates:**
  1. **Status** (center-front, largest) — one big read (SYSTEMS NOMINAL / POLICY NOT APPROVED / QUIET HOURS) + thin cyan underline + secondary DATE · POLICY · QUIET · ROOT strip.
  2. **Brief** (right, mid-depth) — scrollable today’s brief; empty-state copy if missing.
  3. **Actions** (left/lower) — Session Start · Dry-run Workday · Mute; Start Workday visible but R3-gated.
- Optional faint floor grid + soft under-glow; no targeting HUD chrome.
- Window/taskbar icon: dark helmet faceplate with cyan eyes (current `jarvis.ico`).

## Layout on disk

```
apps/windows-3d/
  host/          # WebView2 entry, root discovery, bridge adapters
  ui/            # Three.js scene, CSS, static assets
  README.md
  build_exe.ps1  # → apps/Jarvis3D.exe + Desktop shortcut
```

Prefer extracting a **shared** panel facade used by both `windows-panel` and `windows-3d` so Home actions cannot drift. If extraction is heavy, `windows-3d` may import `apps/windows-panel/panel_api.py` with a clear comment and a follow-up extract task.

## Packaging & install

- Build with PyInstaller (or equivalent) into `C:\Users\rajk1\jarvis\apps\Jarvis3D.exe`.
- Desktop shortcut `JARVIS 3D` (name may be adjusted at implement time; keep distinct from `JARVIS`).
- Document WebView2 Evergreen Runtime requirement if the host does not bundle it.
- Rebuild rule: any change under `apps/windows-3d/` or shared panel facade → rerun `build_exe.ps1`.

## Testing / done when

1. Double-click `Jarvis3D.exe` on `chandan` → desk loads offline.
2. Orbit / zoom works; three plates readable.
3. Status matches jarvis root; brief shows today’s file or empty state.
4. Session Start, Dry-run Workday, Mute succeed (or show clear error); audit lines appear for writes.
5. Start Workday prompts R3; cancel leaves no workday start; confirm runs and refreshes status/brief.
6. `Jarvis.exe` still opens and covers Skills / POLICY / Logs / Apps / STATE.

## Later phases (not this spec)

- Maps and orbiting data widgets  
- Conversational JARVIS in the desk  
- Migrate Skills / POLICY / Logs into 3D plates  
- Optional merge into a single exe  

## Open implementer choices (non-blocking)

- Exact Python WebView2 library (`pywebview` vs alternatives) — pick the one that freezes cleanly on Windows 10.  
- Frameless vs standard window chrome.  
- Whether Phase 1 TTS is in host or deferred.
