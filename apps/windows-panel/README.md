# JARVIS Windows Control Panel

Stark HUD control panel (CustomTkinter) for the local JARVIS tree. Local only, offline.

## Run from source
```powershell
cd C:\Users\rajk1\jarvis\apps\windows-panel
python -m pip install -r requirements.txt
python main.py
```

## Build Jarvis.exe
```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\apps\windows-panel\build_exe.ps1
```
Output: `C:\Users\rajk1\jarvis\apps\Jarvis.exe` + Desktop shortcut `JARVIS`.

## Notes
- Root: folder of the exe, its parent, or `C:\Users\rajk1\jarvis`; override with `JARVIS_HOME`.
- Frozen mode runs `scripts\win\*.py` in-process (`runpy`), so no Python is needed after build.
- R3 confirm before POLICY save, non-dry workday, app launch. Every write/launch/refusal → `logs\audit.jsonl`.
- Tests: `python -m unittest discover tests`
