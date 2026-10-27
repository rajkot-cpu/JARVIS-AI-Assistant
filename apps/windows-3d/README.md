# Jarvis3D (windows-3d)

Phase 1 holographic 3D desk for JARVIS: a local-only WebView2 + Three.js shell showing Home status, today's brief and Home actions. It depends on the sibling `apps/windows-panel` for `panel_api` and `voice`; host and build instructions arrive in later tasks.

## Vendored UI libraries
- three.js **r160** (`three@0.160.0`): `ui/vendor/three.module.min.js`, `ui/vendor/CSS2DRenderer.js`, `ui/vendor/OrbitControls.js` (addons' `'three'` import rewritten to `./three.module.min.js`). No CDN at runtime.

## Build (Windows)
```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\apps\windows-3d\build_exe.ps1
```
Produces `apps\Jarvis3D.exe` (PyInstaller onefile, entry `host_main.py`, `ui/` bundled via `--add-data "ui;ui"`, icon `..\windows-panel\assets\jarvis.ico`) and a Desktop shortcut **JARVIS 3D**. `Jarvis.exe` / `apps/windows-panel` are untouched.

- **WebView2 Evergreen Runtime is required** (pywebview `edgechromium` backend). Windows 11 ships it; otherwise install from Microsoft.
- **Rebuild rule:** re-run `build_exe.ps1` whenever `ui/`, `bridge_api.py`, `host_main.py`, or the panel/scripts it bundles (`apps/windows-panel/panel_api.py`, `voice.py`, `scripts/win/*.py`) change — the exe embeds frozen copies.
- **UI load path:** `host_main.py` loads `ui/index.html` via a relative URL (`url="ui/index.html"`) with `webview.start(http_server=True)`, so pywebview serves the `ui/` folder over its local HTTP server on `http://127.0.0.1` (local-only; no remote URLs). This avoids WebView2 blocking ES modules (Three.js) on `file://`. The process chdirs to the script/bundle dir so `ui/` resolves when frozen.
