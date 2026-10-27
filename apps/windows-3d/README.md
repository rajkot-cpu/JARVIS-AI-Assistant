# Jarvis3D (windows-3d)

Phase 1 holographic 3D desk for JARVIS: a local-only WebView2 + Three.js shell showing Home status, today's brief and Home actions. It depends on the sibling `apps/windows-panel` for `panel_api` and `voice`; host and build instructions arrive in later tasks.

## Vendored UI libraries
- three.js **r160** (`three@0.160.0`): `ui/vendor/three.module.min.js`, `ui/vendor/CSS2DRenderer.js`, `ui/vendor/OrbitControls.js` (addons' `'three'` import rewritten to `./three.module.min.js`). No CDN at runtime.
