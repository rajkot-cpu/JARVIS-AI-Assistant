# Task 8 report — PyInstaller build + install (2026-10-28 ~04:21 IST)

Commit: 978059b (branch jarvis/feat/windows-panel)

## Changes
- panel_api.run_script: when `sys.frozen` (or in_process=True) runs scripts/win/*.py in-process via runpy.run_path with argv/cwd/sys.path/JARVIS_HOME swapped, stdout/stderr captured, SystemExit -> rc. Non-frozen keeps subprocess.
- 2 new tests (in-process + frozen auto-select). 12/12 pass on box and on chandan.
- build_exe.ps1: --paths scripts\win, hidden imports lib_jarvis/session_start/brief/workday_start/block_delete/yaml, --collect-all customtkinter, copies to apps\Jarvis.exe, Desktop JARVIS.lnk.
- apps/windows-panel/README.md, WIN_README.md panel section.

## chandan
- Synced via tarball + CopyFromBox to C:\Users\rajk1\jarvis (apps/windows-panel, scripts/win, WIN_README.md).
- Build: `powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\apps\windows-panel\build_exe.ps1` -> INSTALLED=C:\Users\rajk1\jarvis\apps\Jarvis.exe (26.6 MB), Python 3.13.6.

## Smoke
- panel_api (sys.frozen=True) workday dry: rc 0, audit line ok.
- block_delete STATE.md: rc 1 BLOCKED, audit "refused".
- Jarvis.exe launched, alive after 8s, then killed. MainWindowTitle empty from agent shell — visual GUI check (tabs, POLICY cancel, Apps list) not verified by eye.

## Task 8 review fixes (2026-10-28 04:23 IST)
- `rg "sys.executable|subprocess" scripts/win` → no matches. No code change needed.
- chandan `scripts\win\*.py` SHA256 identical (LF) to worktree for all 5 files, incl. block_delete.py (BLOCKED:/exit 1). No sync needed.
- Docs: Dry-run smoke, rebuild rule, block_delete exit contract added to apps/windows-panel/README.md + WIN_README.md (commit ade384f); WIN_README synced to chandan.
- Launched C:\Users\rajk1\jarvis\apps\Jarvis.exe: PID 13764 alive after 8s, Responding=True. Pixels/UI not verified — user should click Dry-run Workday once.
