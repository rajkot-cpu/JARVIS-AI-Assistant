# JARVIS on Windows (chandan)

Installed at `C:\Users\rajk1\jarvis`.

## Day-to-day (no bash required)
```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\scripts\Start-Jarvis.ps1
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\scripts\Start-Jarvis.ps1 -Cmd session
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\scripts\Start-Jarvis.ps1 -Dry
```

Live calendar/mail: Grok Bot JARVIS chat (07:30 routine). Local brief = STATE + audit only.

## Optional
Install Git for Windows for bash scripts and hooks: https://git-scm.com/download/win

## Control panel app (Jarvis.exe)
Double-click `C:\Users\rajk1\jarvis\apps\Jarvis.exe` or the Desktop `JARVIS` shortcut.
Tabs: Home (status, brief, Start Workday / Dry-run), STATE, Skills, POLICY, Logs, Apps.
Rebuild: `powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\apps\windows-panel\build_exe.ps1`
See `apps\windows-panel\README.md`.

## Jarvis.exe notes

- After installing/rebuilding, open `apps\Jarvis.exe` and click **Dry-run Workday** once to confirm the UI works.
- Rebuild `Jarvis.exe` (`apps\windows-panel\build_exe.ps1`) whenever `scripts\win\*.py` or `lib_jarvis.py` change — the exe uses bundled copies.
- `block_delete.py`: exit 0 `DELETED:` only for approved fixtures paths; exit 1 `BLOCKED:`/`MISSING:`; exit 2 usage. Worktree copy is the source of truth.
