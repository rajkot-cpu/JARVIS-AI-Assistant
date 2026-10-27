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

## Post-build checks and rebuild rule

- **Smoke the real exe once:** open `Jarvis.exe`, go to Home, click **Dry-run Workday** once and confirm the HUD shows output (no red banner). Automated checks only confirm the process starts; they cannot see pixels.
- **Rebuild whenever `scripts/win/*.py` (incl. `lib_jarvis.py`) or `apps/windows-panel/*` change.** Frozen `Jarvis.exe` imports bundled copies of `lib_jarvis` and uses bundled `scripts/win` as fallback, so edits on disk are not picked up until you rerun `build_exe.ps1`.
- **Delete guard contract (`scripts/win/block_delete.py`, source of truth):** exit `0` + `DELETED: <path>` only when `JARVIS_ALLOW_DELETE=1` and path is inside `fixtures/`. Otherwise exit `1` with `BLOCKED: ...` (or `MISSING: ...`), exit `2` on bad usage. The panel treats any non-zero as refused.
