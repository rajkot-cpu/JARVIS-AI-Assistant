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
- **UI load path:** `host_main.py` currently loads `ui/index.html` as a `file://` URI (`url=ui.as_uri()`, resolved from the bundle dir when frozen). ES modules (`<script type="module">`, Three.js imports) can be blocked on `file://` by some WebViews; preferred is pywebview's built-in local HTTP server (pass a relative path such as `url="ui/index.html"` so pywebview serves it over `http://127.0.0.1`). If the 3D scene is blank in the exe, switch to that.
