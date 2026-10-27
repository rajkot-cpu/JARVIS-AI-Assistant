# JARVIS 3D Desk Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship local-only `Jarvis3D.exe` — WebView2 host + Three.js holographic desk with status, brief, Session Start / Dry-run / Mute, and R3-gated Start Workday — while keeping flat `Jarvis.exe` for other tabs.

**Architecture:** Thin Python host (`pywebview` → WebView2) loads bundled `ui/`; JS bridge calls `bridge_api` which wraps existing `apps/windows-panel/panel_api.Panel` + `voice`. Three.js scene + CSS2D HTML plates for readable HUD text.

**Tech Stack:** Python 3.13, pywebview (EdgeChromium/WebView2), Three.js r160+ (CDN vendored into `ui/vendor/`), PyInstaller; reuse `panel_api`, `voice`, `scripts/win`.

**Spec:** `docs/superpowers/specs/2026-10-28-jarvis-3d-desk-phase1-design.md`

## Global Constraints

- Local only — no remote UI URLs; no Grok Bot bridge in Phase 1.
- Standalone `Jarvis3D.exe` on Windows desktop `chandan` (`C:\Users\rajk1\jarvis`).
- Palette: bg `#04070b`, panel `#0b2233`, cyan `#38d4ff`, text `#e4f6ff`, gold `#ff9d2e`, muted `#7a8fa8`, danger `#ff3b30`, ok `#3dff9a`.
- Gold only for Mute / Quiet / R3 title.
- One big status read; no fake targeting reticles; no cinema strobes (≤3 flashes/sec if any pulse).
- R3 confirm before `workday(dry=False)`.
- Never write outside JARVIS_ROOT; audit via existing `panel_api` paths.
- Keep `Jarvis.exe` for Skills / POLICY / Logs / Apps / STATE.
- Default root: `C:\Users\rajk1\jarvis`; `JARVIS_HOME` / `discover_root` same as panel.
- Window icon: `apps/windows-panel/assets/jarvis.ico` (helmet).

## File structure

| Path | Responsibility |
|---|---|
| `apps/windows-3d/bridge_api.py` | JSON-safe facade over `Panel` + `voice` for the JS bridge |
| `apps/windows-3d/host_main.py` | pywebview window, expose bridge, resolve root |
| `apps/windows-3d/ui/index.html` | Shell page |
| `apps/windows-3d/ui/css/desk.css` | HUD plate styles |
| `apps/windows-3d/ui/js/bridge.js` | Call host API / mock fallback |
| `apps/windows-3d/ui/js/scene.js` | Three.js desk + CSS2D plates |
| `apps/windows-3d/ui/js/app.js` | Wire UI actions, refresh, R3 modal |
| `apps/windows-3d/ui/vendor/three.min.js` | Vendored Three.js |
| `apps/windows-3d/ui/vendor/CSS2DRenderer.js` | Vendored CSS2D |
| `apps/windows-3d/requirements.txt` | pywebview, pyinstaller (+ path note for panel deps) |
| `apps/windows-3d/build_exe.ps1` | Freeze → `apps/Jarvis3D.exe` + Desktop shortcut |
| `apps/windows-3d/README.md` | Run from source + WebView2 note |
| `apps/windows-3d/tests/test_bridge_api.py` | Unit tests (no GUI) |

---

### Task 1: Scaffold + `bridge_api` status/brief (TDD)

**Files:**
- Create: `apps/windows-3d/requirements.txt`
- Create: `apps/windows-3d/bridge_api.py`
- Create: `apps/windows-3d/tests/test_bridge_api.py`
- Create: `apps/windows-3d/README.md` (stub: purpose + run later)

**Interfaces:**
- Consumes: `panel_api.Panel`, `panel_api.discover_root`, `panel_api.is_valid_root`
- Produces:
  - `class Bridge:`
  - `def __init__(self, panel: panel_api.Panel) -> None`
  - `def get_status(self) -> dict` → `{ok: True, data: {today, policy_ok, quiet_hours, root, headline}}`
  - `def get_brief(self) -> dict` → `{ok: True, data: {text: str}}`
  - Headline rules: if not `policy_ok` → `"POLICY NOT APPROVED"`; elif `quiet_hours` → `"QUIET HOURS"`; else `"SYSTEMS NOMINAL"`

- [ ] **Step 1: Write failing tests**

```python
# apps/windows-3d/tests/test_bridge_api.py
import sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))
sys.path.insert(0, str(ROOT / "apps" / "windows-3d"))
sys.path.insert(0, str(ROOT / "scripts" / "win"))

import panel_api
import bridge_api


def _make_root(tmp: Path, *, approved: bool = True, quiet: str = "22:00-07:00") -> Path:
    (tmp / "STATE.md").write_text("# STATE\n", encoding="utf-8")
    status = "approved" if approved else "draft"
    (tmp / "POLICY.yaml").write_text(
        f"status: {status}\nschedule:\n  quiet_hours: \"{quiet}\"\n",
        encoding="utf-8",
    )
    (tmp / "reports").mkdir()
    (tmp / "logs").mkdir()
    return tmp


class TestBridgeReads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = _make_root(Path(self.tmp.name), approved=True)
        self.bridge = bridge_api.Bridge(panel_api.Panel(self.root))

    def tearDown(self):
        self.tmp.cleanup()

    def test_get_status_ok_shape(self):
        r = self.bridge.get_status()
        self.assertTrue(r["ok"])
        d = r["data"]
        self.assertIn("today", d)
        self.assertTrue(d["policy_ok"])
        self.assertEqual(d["headline"], "SYSTEMS NOMINAL")
        self.assertEqual(d["root"], str(self.root.resolve()))

    def test_headline_policy_not_approved(self):
        root = _make_root(Path(tempfile.mkdtemp()), approved=False)
        b = bridge_api.Bridge(panel_api.Panel(root))
        self.assertEqual(b.get_status()["data"]["headline"], "POLICY NOT APPROVED")

    def test_get_brief_empty_then_text(self):
        r = self.bridge.get_brief()
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["text"], "")
        day = self.bridge.get_status()["data"]["today"]
        (self.root / "reports" / f"{day}.md").write_text("# Brief\nHello\n", encoding="utf-8")
        self.assertIn("Hello", self.bridge.get_brief()["data"]["text"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests — expect fail (no module)**

```bash
cd /home/box/jarvis && python -m unittest apps.windows-3d.tests.test_bridge_api -v
```

Expected: `ModuleNotFoundError: bridge_api` (or import path fail). Prefer:

```bash
cd /home/box/jarvis/apps/windows-3d && PYTHONPATH="../windows-panel:../../scripts/win:." python -m unittest tests.test_bridge_api -v
```

Expected: FAIL importing `bridge_api`.

- [ ] **Step 3: Minimal `bridge_api.py`**

```python
# apps/windows-3d/bridge_api.py
from __future__ import annotations
from pathlib import Path
import sys

_PANEL = Path(__file__).resolve().parents[1] / "windows-panel"
if str(_PANEL) not in sys.path:
    sys.path.insert(0, str(_PANEL))

import panel_api  # noqa: E402


def _headline(status: dict) -> str:
    if not status.get("policy_ok"):
        return "POLICY NOT APPROVED"
    if status.get("quiet_hours"):
        return "QUIET HOURS"
    return "SYSTEMS NOMINAL"


class Bridge:
    def __init__(self, panel: panel_api.Panel):
        self.panel = panel

    def get_status(self) -> dict:
        try:
            s = self.panel.status_strip()
            data = dict(s)
            data["headline"] = _headline(s)
            return {"ok": True, "data": data}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_brief(self) -> dict:
        try:
            return {"ok": True, "data": {"text": self.panel.today_brief() or ""}}
        except Exception as e:
            return {"ok": False, "error": str(e)}
```

- [ ] **Step 4: requirements + README stub**

`requirements.txt`:
```
pywebview>=5.0
pyinstaller>=6.0
```

`README.md`: one paragraph — Phase 1 3D desk; depends on sibling `windows-panel` for `panel_api`/`voice`.

- [ ] **Step 5: Re-run tests — expect PASS**

```bash
cd /home/box/jarvis/apps/windows-3d && PYTHONPATH="../windows-panel:../../scripts/win:." python -m unittest tests.test_bridge_api -v
```

Expected: OK (all tests PASS).

- [ ] **Step 6: Commit**

```bash
git add apps/windows-3d && git commit -m "feat(windows-3d): bridge_api status/brief + tests"
```

---

### Task 2: Bridge actions — session, workday, mute (TDD)

**Files:**
- Modify: `apps/windows-3d/bridge_api.py`
- Modify: `apps/windows-3d/tests/test_bridge_api.py`

**Interfaces:**
- Consumes: `Panel.session_start`, `Panel.workday`, `voice.load_prefs`, `voice.is_muted`, `voice.set_muted`
- Produces:
  - `session_start(self) -> dict` → `{ok: bool, code?: int, error?: str}`
  - `workday(self, dry: bool = True) -> dict` (same shape)
  - `get_mute(self) -> dict` → `{ok: True, data: {muted: bool}}`
  - `set_mute(self, muted: bool) -> dict` → `{ok: True, data: {muted: bool}}`
  - Note: R3 is enforced in the UI/host before calling `workday(False)` — bridge itself may call dry or non-dry when invoked; do not add a second gate inside bridge that blocks dry runs.

- [ ] **Step 1: Add failing tests**

```python
class TestBridgeActions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = _make_root(Path(self.tmp.name))
        self.panel = panel_api.Panel(self.root)
        self.bridge = bridge_api.Bridge(self.panel)
        # voice prefs path
        import voice
        voice.load_prefs(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_mute_roundtrip(self):
        import voice
        self.assertFalse(self.bridge.get_mute()["data"]["muted"])
        self.bridge.set_mute(True)
        self.assertTrue(voice.is_muted())
        self.assertTrue(self.bridge.get_mute()["data"]["muted"])

    def test_workday_dry_returns_dict(self):
        # May fail scripts on Linux box — assert shape only; mock Panel.workday
        self.panel.workday = lambda dry=False: (0, "ok", "")
        r = self.bridge.workday(dry=True)
        self.assertTrue(r["ok"])
        self.assertEqual(r["code"], 0)

    def test_session_start_shape(self):
        self.panel.session_start = lambda: (0, "ok", "")
        r = self.bridge.session_start()
        self.assertTrue(r["ok"])
```

- [ ] **Step 2: Run — expect FAIL (methods missing)**

```bash
cd /home/box/jarvis/apps/windows-3d && PYTHONPATH="../windows-panel:../../scripts/win:." python -m unittest tests.test_bridge_api.TestBridgeActions -v
```

- [ ] **Step 3: Implement actions on `Bridge`**

```python
# append to bridge_api.py
def session_start(self) -> dict:
    try:
        code, out, err = self.panel.session_start()
        if code == 0:
            return {"ok": True, "code": 0, "data": {"out": out}}
        return {"ok": False, "code": code, "error": (err or out or f"exit {code}").strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def workday(self, dry: bool = True) -> dict:
    try:
        code, out, err = self.panel.workday(dry=bool(dry))
        if code == 0:
            return {"ok": True, "code": 0, "data": {"out": out, "dry": bool(dry)}}
        return {"ok": False, "code": code, "error": (err or out or f"exit {code}").strip()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_mute(self) -> dict:
    import voice
    return {"ok": True, "data": {"muted": bool(voice.is_muted())}}

def set_mute(self, muted: bool = False) -> dict:
    import voice
    voice.set_muted(bool(muted))
    return {"ok": True, "data": {"muted": bool(voice.is_muted())}}
```

Call `voice.load_prefs(panel.root)` once from host on startup (Task 3), not necessarily inside every Bridge method — tests call `load_prefs` in `setUp`.

- [ ] **Step 4: Re-run — PASS**

- [ ] **Step 5: Commit**

```bash
git add apps/windows-3d/bridge_api.py apps/windows-3d/tests/test_bridge_api.py
git commit -m "feat(windows-3d): bridge session/workday/mute"
```

---

### Task 3: Python host (`host_main.py`) + JS API surface

**Files:**
- Create: `apps/windows-3d/host_main.py`
- Create: `apps/windows-3d/ui/index.html` (minimal placeholder: black page + `JARVIS 3D` text)
- Create: `apps/windows-3d/ui/js/bridge.js`

**Interfaces:**
- Consumes: `bridge_api.Bridge`, `panel_api.discover_root`, `voice.load_prefs`
- Produces: pywebview `js_api` object with methods matching JS names:
  - `getStatus`, `getBrief`, `sessionStart`, `workday`, `getMute`, `setMute`
  - Each returns a plain `dict` (JSON-serializable)

- [ ] **Step 1: Write `bridge.js` client**

```javascript
// apps/windows-3d/ui/js/bridge.js
export async function api(name, ...args) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api[name]) {
    return await window.pywebview.api[name](...args);
  }
  console.warn("bridge mock", name, args);
  if (name === "getStatus") {
    return { ok: true, data: { today: "2099-01-01", policy_ok: true, quiet_hours: false,
      root: "(mock)", headline: "SYSTEMS NOMINAL" } };
  }
  if (name === "getBrief") return { ok: true, data: { text: "(mock brief)" } };
  if (name === "getMute") return { ok: true, data: { muted: false } };
  return { ok: true, data: {} };
}
```

- [ ] **Step 2: Minimal `index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>JARVIS 3D</title>
  <style>html,body{margin:0;height:100%;background:#04070b;color:#38d4ff;font-family:Segoe UI,sans-serif}
  #boot{padding:24px}</style>
</head>
<body>
  <div id="boot">JARVIS 3D — host online</div>
  <script type="module">
    import { api } from "./js/bridge.js";
    window.addEventListener("pywebviewready", async () => {
      const s = await api("getStatus");
      document.getElementById("boot").textContent =
        s.ok ? `JARVIS 3D — ${s.data.headline}` : `JARVIS 3D — ${s.error}`;
    });
  </script>
</body>
</html>
```

- [ ] **Step 3: `host_main.py`**

```python
# apps/windows-3d/host_main.py
from __future__ import annotations
import os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PANEL_DIR = HERE.parent / "windows-panel"
sys.path.insert(0, str(PANEL_DIR))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "scripts" / "win"))

import panel_api
import bridge_api
import voice


class Api:
    def __init__(self, bridge: bridge_api.Bridge):
        self._b = bridge

    def getStatus(self):
        return self._b.get_status()

    def getBrief(self):
        return self._b.get_brief()

    def sessionStart(self):
        return self._b.session_start()

    def workday(self, dry: bool = True):
        return self._b.workday(dry=bool(dry))

    def getMute(self):
        return self._b.get_mute()

    def setMute(self, muted: bool = False):
        return self._b.set_mute(bool(muted))


def main() -> int:
    exe_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else HERE
    root = None
    env = os.environ.get("JARVIS_HOME")
    if env:
        cand = Path(env)
        if panel_api.is_valid_root(cand):
            root = cand.resolve()
    if root is None:
        root = panel_api.discover_root(exe_dir=exe_dir)
    if root is None:
        print("JARVIS_ROOT not found", file=sys.stderr)
        return 2
    voice.load_prefs(root)
    bridge = bridge_api.Bridge(panel_api.Panel(root))
    ui = HERE / "ui" / "index.html"
    import webview
    window = webview.create_window(
        "JARVIS 3D // STARK OS",
        url=ui.as_uri(),
        js_api=Api(bridge),
        width=1280,
        height=800,
        background_color="#04070b",
    )
    webview.start(gui="edgechromium")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Smoke from source on Windows** (skip GUI on Linux box)

On `chandan`:

```powershell
cd C:\Users\rajk1\jarvis\apps\windows-3d
python -m pip install -r requirements.txt
python host_main.py
```

Expected: window opens; boot line shows headline after `pywebviewready`.

On Linux box: keep unit tests green only.

- [ ] **Step 5: Commit**

```bash
git add apps/windows-3d && git commit -m "feat(windows-3d): pywebview host + JS bridge client"
```

---

### Task 4: Three.js desk scene + three CSS2D plates (visual shell)

**Files:**
- Create: `apps/windows-3d/ui/css/desk.css`
- Create: `apps/windows-3d/ui/js/scene.js`
- Modify: `apps/windows-3d/ui/index.html`
- Create: `apps/windows-3d/ui/vendor/three.min.js` (download Three r160+ UMD or ES module build)
- Create: `apps/windows-3d/ui/vendor/CSS2DRenderer.js` (from three/examples, matched version)

**Interfaces:**
- Produces `createDesk(containerEl) -> { setStatus, setBrief, setMuteUi, onAction, render loop }`
  - `setStatus({ headline, today, policy_ok, quiet_hours, root, error? })`
  - `setBrief(text: string)`
  - `setMuteUi(muted: boolean)`
  - `onAction(cb)` where action is `"sessionStart" | "workdayDry" | "workdayReal" | "toggleMute"`

- [ ] **Step 1: Vendor Three + CSS2D** into `ui/vendor/` (no CDN at runtime). Record version in README.

- [ ] **Step 2: `desk.css`** — plate cards: dark glass, cyan border 1px, headline large cyan/gold/danger, secondary muted, buttons cyan outline; primary dry-run outline; Start Workday filled cyan; Mute gold label.

- [ ] **Step 3: `scene.js`** — scene with dark fog/bg `#04070b`, faint grid helper on floor, OrbitControls (or simple drag), three `CSS2DObject` plates:
  - Status center-front
  - Brief right
  - Actions left/lower with buttons + mute checkbox/switch
  Wire button clicks to `onAction`.

- [ ] **Step 4: Update `index.html`** — full viewport `#desk`, load css + modules; remove boot-only layout (keep a small `#banner` for errors).

- [ ] **Step 5: Open `ui/index.html` via host** — visually confirm orbit + three plates (mock bridge OK if host not ready). Screenshot optional.

- [ ] **Step 6: Commit**

```bash
git add apps/windows-3d/ui && git commit -m "feat(windows-3d): Three.js desk + CSS2D plates"
```

---

### Task 5: Wire app.js — refresh + actions + R3 modal

**Files:**
- Create: `apps/windows-3d/ui/js/app.js`
- Modify: `apps/windows-3d/ui/index.html` (import app)
- Create: `apps/windows-3d/ui/js/r3.js` (modal)

**Interfaces:**
- On load / `pywebviewready`: `getStatus`, `getBrief`, `getMute` → scene setters
- Actions:
  - sessionStart → `api("sessionStart")` → banner + refresh
  - workdayDry → `api("workday", true)`
  - toggleMute → `api("setMute", !current)`
  - workdayReal → show R3 modal; on confirm `api("workday", false)`; on cancel banner `"Start Workday cancelled"`

- [ ] **Step 1: `r3.js`**

```javascript
export function confirmR3({ title, body }) {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "r3-overlay";
    overlay.innerHTML = `<div class="r3-card"><h2>R3 // ${title}</h2><p>${body}</p>
      <div class="r3-row"><button class="ok">Confirm</button><button class="cancel">Cancel</button></div></div>`;
    document.body.appendChild(overlay);
    overlay.querySelector(".ok").onclick = () => { overlay.remove(); resolve(true); };
    overlay.querySelector(".cancel").onclick = () => { overlay.remove(); resolve(false); };
  });
}
```

Style `.r3-overlay` fixed full-screen dim; gold title.

- [ ] **Step 2: `app.js`** — createDesk, bind onAction, refresh helpers, set banner on errors (`#banner` text + danger color).

- [ ] **Step 3: Manual check on Windows** — Dry-run Workday, Mute, Session Start; cancel Start Workday; then confirm once if safe.

- [ ] **Step 4: Commit**

```bash
git add apps/windows-3d/ui && git commit -m "feat(windows-3d): wire bridge actions + R3 modal"
```

---

### Task 6: PyInstaller build + Desktop shortcut

**Files:**
- Create: `apps/windows-3d/build_exe.ps1`
- Modify: `apps/windows-3d/README.md` (WebView2 Evergreen note + rebuild rule)
- Copy icon reference: use `../windows-panel/assets/jarvis.ico`

**Interfaces:**
- Produces `C:\Users\rajk1\jarvis\apps\Jarvis3D.exe` and Desktop shortcut `JARVIS 3D.lnk`

- [ ] **Step 1: Write `build_exe.ps1`** mirroring `windows-panel/build_exe.ps1`:
  - `--name Jarvis3D`
  - `--add-data "ui;ui"`
  - `--paths` to `windows-panel` and `scripts\win`
  - hidden-imports: `panel_api`, `bridge_api`, `voice`, `yaml`, `webview`, `lib_jarvis`, win scripts as needed
  - `--icon ..\windows-panel\assets\jarvis.ico`
  - Copy to `apps\Jarvis3D.exe`; shortcut name `JARVIS 3D`

- [ ] **Step 2: Run on chandan**

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\apps\windows-3d\build_exe.ps1
```

Expected: `INSTALLED=...\apps\Jarvis3D.exe`

- [ ] **Step 3: Smoke** — double-click; status loads; Dry-run once; Mute toggles; Jarvis.exe still opens.

- [ ] **Step 4: Commit build script + README** (not the exe)

```bash
git add apps/windows-3d/build_exe.ps1 apps/windows-3d/README.md
git commit -m "feat(windows-3d): PyInstaller Jarvis3D.exe build"
```

---

### Task 7: Done checklist + sync note

**Files:**
- Modify: `apps/windows-3d/README.md` — paste done-when checklist from spec
- Optional: one-line pointer in `apps/windows-panel/README.md` → Jarvis3D Phase 1

- [ ] **Step 1: Verify checklist** (all must be true on `chandan`):
  1. `Jarvis3D.exe` opens offline
  2. Orbit/zoom + three plates
  3. Live status + brief
  4. Session Start / Dry-run / Mute work or clear error
  5. Start Workday R3 cancel/confirm
  6. `Jarvis.exe` still covers other tabs

- [ ] **Step 2: Commit doc touch if any**

```bash
git add apps/windows-3d/README.md apps/windows-panel/README.md
git commit -m "docs(windows-3d): Phase 1 done-when + panel cross-link"
```

---

## Spec coverage (self-review)

| Spec item | Task |
|---|---|
| WebView2 + Three.js local exe | 3, 4, 6 |
| Floating panels / orbit / depth | 4 |
| Status one-read + secondary strip | 1, 4, 5 |
| Brief plate | 1, 4, 5 |
| Session Start / Dry-run / Mute | 2, 5 |
| R3 Start Workday | 5 |
| Reuse panel_api / audit | 1–2 |
| Keep Jarvis.exe | 6–7 (no removal) |
| Palette / gold sparingly | 4 |
| Packaging + WebView2 note | 6 |
| Helmet icon | 6 |

No TBD/TODO placeholders. Bridge method names consistent: Python `get_status` ↔ JS API `getStatus`.
