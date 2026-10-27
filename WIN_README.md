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
