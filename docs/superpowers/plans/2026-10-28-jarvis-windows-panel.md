# JARVIS Windows Control Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Stark-HUD CustomTkinter control panel frozen as `Jarvis.exe` that runs fully offline against `C:\Users\rajk1\jarvis`.

**Architecture:** Thin `panel_api` facade over `scripts/win/*.py` + file IO under JARVIS_ROOT; CustomTkinter UI in `apps/windows-panel/`; PyInstaller onefile build on desktop `chandan`.

**Tech Stack:** Python 3.13, CustomTkinter, PyYAML, PyInstaller; reuse `scripts/win/lib_jarvis.py`.

**Spec:** `docs/superpowers/specs/2026-10-28-jarvis-windows-panel-design.md`

## Global Constraints

- Local only — no Grok Bot bridge in v1.
- Standalone `.exe` for end user (no Python required after freeze).
- Stark HUD: dark background, cyan accents, gold highlights.
- Never write outside JARVIS_ROOT except allowlisted app launches.
- R3 in-app confirm before POLICY save, workday (non-dry), write/launch skills, app launch.
- `block_delete` remains authoritative; panel never bypasses it.
- Audit every write/launch/refusal via JSONL under `logs/`.
- Default root: `C:\Users\rajk1\jarvis`; override via `JARVIS_HOME` env for tests.
- STATE tab is read-only in v1.
- Windows apps map for v1: `chrome` → `chrome.exe` (or Program Files path), `terminal` → `wt.exe` then `powershell.exe`.

## File structure

| Path | Responsibility |
|---|---|
| `scripts/win/lib_jarvis.py` | Add `JARVIS_HOME` env override to `jarvis_home()` |
| `apps/windows-panel/requirements.txt` | customtkinter, pyyaml, pyinstaller |
| `apps/windows-panel/panel_api.py` | Root discovery, reads, actions, audit helper |
| `apps/windows-panel/theme.py` | Stark color constants |
| `apps/windows-panel/ui/app.py` | Main window + left nav |
| `apps/windows-panel/ui/home.py` | Home tab |
| `apps/windows-panel/ui/skills.py` | Skills tab |
| `apps/windows-panel/ui/policy.py` | POLICY tab |
| `apps/windows-panel/ui/logs.py` | Logs tab |
| `apps/windows-panel/ui/apps.py` | Apps tab |
| `apps/windows-panel/ui/state_view.py` | STATE read-only tab |
| `apps/windows-panel/ui/confirm.py` | R3 confirm dialog |
| `apps/windows-panel/main.py` | Entry point |
| `apps/windows-panel/build_exe.ps1` | PyInstaller onefile on Windows |
| `apps/windows-panel/tests/test_panel_api.py` | Unit tests (no GUI) |
| `apps/Jarvis.exe` | Built artifact (not committed; install target) |
| `WIN_README.md` | Document how to launch the panel |

---

### Task 1: JARVIS_HOME override + panel_api root discovery

**Files:**
- Modify: `scripts/win/lib_jarvis.py`
- Create: `apps/windows-panel/panel_api.py`
- Create: `apps/windows-panel/tests/test_panel_api.py`
- Create: `apps/windows-panel/requirements.txt`

**Interfaces:**
- Consumes: existing `lib_jarvis.jarvis_home`, `append_audit`, `quiet_hours_active`, `load_policy`
- Produces:
  - `jarvis_home() -> Path` respects `os.environ["JARVIS_HOME"]` if set and valid
  - `panel_api.is_valid_root(path: Path) -> bool` — true iff `STATE.md` and `POLICY.yaml` exist
  - `panel_api.discover_root(exe_dir: Path | None = None, default: Path | None = None) -> Path | None`
  - `panel_api.Panel(root: Path)` with `.root`

- [ ] **Step 1: Write the failing test**

Create `apps/windows-panel/tests/test_panel_api.py`:

```python
import os, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # /home/box/jarvis or C:\Users\rajk1\jarvis
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))
sys.path.insert(0, str(ROOT / "scripts" / "win"))

import panel_api


class TestRoot(unittest.TestCase):
    def test_is_valid_root_requires_state_and_policy(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self.assertFalse(panel_api.is_valid_root(p))
            (p / "STATE.md").write_text("#", encoding="utf-8")
            self.assertFalse(panel_api.is_valid_root(p))
            (p / "POLICY.yaml").write_text("status: approved\n", encoding="utf-8")
            self.assertTrue(panel_api.is_valid_root(p))

    def test_discover_root_prefers_exe_dir_when_valid(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "STATE.md").write_text("#", encoding="utf-8")
            (p / "POLICY.yaml").write_text("status: approved\n", encoding="utf-8")
            found = panel_api.discover_root(exe_dir=p, default=Path("/nonexistent"))
            self.assertEqual(found, p.resolve())

    def test_jarvis_home_env_override(self):
        import lib_jarvis
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            old = os.environ.get("JARVIS_HOME")
            os.environ["JARVIS_HOME"] = str(p)
            try:
                self.assertEqual(lib_jarvis.jarvis_home(), p.resolve())
            finally:
                if old is None:
                    os.environ.pop("JARVIS_HOME", None)
                else:
                    os.environ["JARVIS_HOME"] = old


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/box/jarvis && python3 apps/windows-panel/tests/test_panel_api.py -v`  
Expected: FAIL (module `panel_api` missing and/or `JARVIS_HOME` ignored)

- [ ] **Step 3: Write minimal implementation**

In `scripts/win/lib_jarvis.py`, replace `jarvis_home` with:

```python
def jarvis_home() -> Path:
    env = os.environ.get("JARVIS_HOME", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return Path(r"C:\Users\rajk1\jarvis")
```

Add `import os` at top of `lib_jarvis.py` if missing.

Create `apps/windows-panel/panel_api.py`:

```python
from __future__ import annotations
from pathlib import Path

DEFAULT_ROOT = Path(r"C:\Users\rajk1\jarvis")


def is_valid_root(path: Path) -> bool:
    p = Path(path)
    return (p / "STATE.md").is_file() and (p / "POLICY.yaml").is_file()


def discover_root(exe_dir: Path | None = None, default: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if exe_dir is not None:
        candidates.append(Path(exe_dir))
        # exe living in apps/ → parent may be jarvis root
        candidates.append(Path(exe_dir).parent)
    candidates.append(Path(default) if default is not None else DEFAULT_ROOT)
    for c in candidates:
        try:
            r = c.resolve()
        except Exception:
            continue
        if is_valid_root(r):
            return r
    return None


class Panel:
    def __init__(self, root: Path):
        root = Path(root).resolve()
        if not is_valid_root(root):
            raise ValueError(f"invalid JARVIS_ROOT: {root}")
        self.root = root
```

Create `apps/windows-panel/requirements.txt`:

```
customtkinter>=5.2.0
pyyaml>=6.0
pyinstaller>=6.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/box/jarvis && python3 apps/windows-panel/tests/test_panel_api.py -v`  
Expected: PASS for the three tests above

- [ ] **Step 5: Commit**

```bash
git add scripts/win/lib_jarvis.py apps/windows-panel/panel_api.py apps/windows-panel/tests/test_panel_api.py apps/windows-panel/requirements.txt
git commit -m "feat(panel): JARVIS_HOME override and root discovery"
```

---

### Task 2: panel_api reads — STATE, POLICY, brief, skills, logs, apps

**Files:**
- Modify: `apps/windows-panel/panel_api.py`
- Modify: `apps/windows-panel/tests/test_panel_api.py`

**Interfaces:**
- Consumes: `Panel.root`, filesystem layout under jarvis
- Produces on `Panel`:
  - `read_text(rel: str) -> str`
  - `status_strip() -> dict` with keys `root`, `policy_ok`, `quiet_hours`, `today`
  - `today_brief() -> str` — contents of `reports/YYYY-MM-DD.md` or `""`
  - `list_skills() -> list[dict]` each `{name, path, summary, risk}` where `risk` is `"read"` or `"write"`
  - `list_log_files() -> list[Path]`
  - `tail_log(path: Path, max_lines: int = 200) -> str`
  - `list_apps() -> list[dict]` each `{name, command}` from POLICY `apps_allowlist` + Windows map
  - `list_restricted() -> list[str]` from POLICY `restricted`
  - `parse_policy() -> dict` via PyYAML

Skill risk heuristic: if skill dir name contains `app-control` or `workday` → `"write"`; else `"read"`. Summary = first non-empty line of `SKILL.md` after the title, max 160 chars.

Windows app map constant in `panel_api.py`:

```python
WIN_APP_MAP = {
    "chrome": ["chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
    "terminal": ["wt.exe", "powershell.exe"],
}
```

- [ ] **Step 1: Write the failing tests**

Append to `test_panel_api.py`:

```python
class TestReads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "STATE.md").write_text("# STATE\n## Status\nok\n", encoding="utf-8")
        (self.root / "POLICY.yaml").write_text(
            'status: approved\napps_allowlist: [chrome, terminal]\n'
            'restricted: ["~/patients"]\n'
            'schedule:\n  quiet_hours: "22:00-07:00"\n',
            encoding="utf-8",
        )
        (self.root / "reports").mkdir()
        (self.root / "logs").mkdir()
        (self.root / "skills" / "file-search").mkdir(parents=True)
        (self.root / "skills" / "file-search" / "SKILL.md").write_text(
            "# Skill: file-search\nFind files under jarvis.\n", encoding="utf-8"
        )
        (self.root / "skills" / "app-control").mkdir(parents=True)
        (self.root / "skills" / "app-control" / "SKILL.md").write_text(
            "# Skill: app-control\nLaunch allowlisted apps.\n", encoding="utf-8"
        )
        self.panel = panel_api.Panel(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_skills(self):
        skills = {s["name"]: s for s in self.panel.list_skills()}
        self.assertEqual(skills["file-search"]["risk"], "read")
        self.assertEqual(skills["app-control"]["risk"], "write")
        self.assertIn("Find files", skills["file-search"]["summary"])

    def test_list_apps_and_restricted(self):
        apps = self.panel.list_apps()
        names = {a["name"] for a in apps}
        self.assertEqual(names, {"chrome", "terminal"})
        self.assertEqual(self.panel.list_restricted(), ["~/patients"])

    def test_today_brief_empty_then_present(self):
        self.assertEqual(self.panel.today_brief(), "")
        day = self.panel.status_strip()["today"]
        (self.root / "reports" / f"{day}.md").write_text("hello brief", encoding="utf-8")
        self.assertEqual(self.panel.today_brief(), "hello brief")
```

- [ ] **Step 2: Run tests — expect FAIL** on missing methods

Run: `python3 apps/windows-panel/tests/test_panel_api.py -v`

- [ ] **Step 3: Implement read methods on `Panel`**

Add implementations in `panel_api.py` (use `yaml.safe_load` for POLICY; `datetime` with IST offset +05:30 for `today`). Include `status_strip` using `lib_jarvis.quiet_hours_active` after setting `os.environ["JARVIS_HOME"]` to `str(self.root)` for the call, or pass policy text directly.

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add apps/windows-panel/panel_api.py apps/windows-panel/tests/test_panel_api.py
git commit -m "feat(panel): read STATE, POLICY, skills, logs, apps"
```

---

### Task 3: panel_api actions — audit, workday/session/brief, POLICY save, block_delete, launch

**Files:**
- Modify: `apps/windows-panel/panel_api.py`
- Modify: `apps/windows-panel/tests/test_panel_api.py`

**Interfaces:**
- Produces on `Panel`:
  - `audit(action: str, path: str, result: str, detail: str = "") -> None` — append JSONL to `logs/audit.jsonl` with `actor: "windows-panel"`
  - `run_script(name: str, args: list[str] | None = None) -> tuple[int, str, str]` — run `scripts/win/{name}.py` with `JARVIS_HOME` set; return `(code, stdout, stderr)`
  - `session_start() -> tuple[int, str, str]`
  - `workday(dry: bool = False) -> tuple[int, str, str]`
  - `write_brief() -> tuple[int, str, str]`
  - `save_policy(new_text: str) -> Path` — backup to `logs/policy-backups/POLICY-YYYYMMDD-HHMMSS.yaml`, write `POLICY.yaml`, audit; raise `ValueError` if YAML does not parse
  - `block_delete(target: Path) -> tuple[int, str, str]` — invoke `block_delete.py`
  - `launch_app(name: str) -> tuple[int, str, str]` — only if `name` in allowlist; try commands from `WIN_APP_MAP`; audit success/refusal

- [ ] **Step 1: Write failing tests**

```python
class TestActions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "STATE.md").write_text("# STATE\n", encoding="utf-8")
        (self.root / "POLICY.yaml").write_text(
            "status: approved\napps_allowlist: [chrome]\nrestricted: []\n",
            encoding="utf-8",
        )
        (self.root / "logs").mkdir()
        (self.root / "reports").mkdir()
        (self.root / "scripts" / "win").mkdir(parents=True)
        # minimal block_delete stub
        (self.root / "scripts" / "win" / "block_delete.py").write_text(
            "import sys\nfrom pathlib import Path\n"
            "p=Path(sys.argv[1])\n"
            "print('REFUSED' if p.name=='STATE.md' else 'OK')\n"
            "sys.exit(2 if p.name=='STATE.md' else 0)\n",
            encoding="utf-8",
        )
        self.panel = panel_api.Panel(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_audit_line(self):
        self.panel.audit("test", "STATE.md", "ok", "detail")
        lines = (self.root / "logs" / "audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("windows-panel", lines[0])

    def test_save_policy_backup_and_reject_bad_yaml(self):
        with self.assertRaises(ValueError):
            self.panel.save_policy(":\n  bad")
        path = self.panel.save_policy("status: approved\napps_allowlist: [chrome]\n")
        self.assertTrue(path.is_file())
        backups = list((self.root / "logs" / "policy-backups").glob("POLICY-*.yaml"))
        self.assertTrue(backups)

    def test_launch_unknown_refused(self):
        code, out, err = self.panel.launch_app("not-an-app")
        self.assertNotEqual(code, 0)
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement action methods**

`run_script` must set `env = os.environ | {"JARVIS_HOME": str(self.root)}` and invoke `sys.executable` on `self.root / "scripts" / "win" / f"{name}.py"`.

For `launch_app` on non-Windows CI/box: if no binary found, return `(1, "", "app binary not found")` after audit refusal — tests for unknown name still pass without launching Chrome.

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add apps/windows-panel/panel_api.py apps/windows-panel/tests/test_panel_api.py
git commit -m "feat(panel): actions audit workday policy save launch"
```

---

### Task 4: Stark theme + shell window + R3 confirm

**Files:**
- Create: `apps/windows-panel/theme.py`
- Create: `apps/windows-panel/ui/__init__.py`
- Create: `apps/windows-panel/ui/confirm.py`
- Create: `apps/windows-panel/ui/app.py`
- Create: `apps/windows-panel/main.py`

**Interfaces:**
- Consumes: `panel_api.Panel`, `discover_root`
- Produces: `theme.COLORS` dict; `confirm.ask(parent, title, body) -> bool`; `JarvisApp(panel)` main window with left nav placeholders

- [ ] **Step 1: Create theme**

```python
# apps/windows-panel/theme.py
COLORS = {
    "bg": "#0a0e17",
    "panel": "#121826",
    "cyan": "#00e5ff",
    "gold": "#f5c542",
    "text": "#e8eef7",
    "muted": "#8b9bb4",
    "danger": "#ff4d6d",
    "ok": "#3dff9a",
}
```

- [ ] **Step 2: Create R3 confirm dialog**

`ui/confirm.py` using `customtkinter.CTkToplevel` with title, body, **Confirm** (cyan) and **Cancel**; return `True` only on Confirm.

- [ ] **Step 3: Create shell `ui/app.py`**

`JarvisApp(ctk.CTk)`:
- Title `"JARVIS // STARK OS"`
- Left frame nav buttons: Home, Skills, POLICY, Logs, Apps, STATE
- Right content frame; `show(name)` swaps frames
- Banner label at top for errors/success (red/cyan)
- Instantiate empty placeholder frames for each tab (filled in later tasks)

- [ ] **Step 4: Create `main.py`**

```python
import sys
from pathlib import Path
import customtkinter as ctk
from panel_api import discover_root, Panel
from ui.app import JarvisApp

def main() -> int:
    exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    root = discover_root(exe_dir=exe_dir)
    if root is None:
        # fallback: still open a tiny picker using filedialog
        from tkinter import filedialog, messagebox
        ctk.set_appearance_mode("dark")
        pick = filedialog.askdirectory(title="Select JARVIS root")
        if not pick:
            messagebox.showerror("JARVIS", "No valid JARVIS_ROOT selected.")
            return 2
        root = Path(pick)
        from panel_api import is_valid_root
        if not is_valid_root(root):
            messagebox.showerror("JARVIS", "Folder missing STATE.md or POLICY.yaml.")
            return 2
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = JarvisApp(Panel(root))
    app.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Manual smoke on box (if display) or import check**

Run: `cd /home/box/jarvis/apps/windows-panel && python3 -c "import theme; import panel_api; print('ok')"`  
Expected: `ok`

On `chandan` (has display): `pip install -r requirements.txt` then `python main.py` briefly — window opens, close manually.

- [ ] **Step 6: Commit**

```bash
git add apps/windows-panel/theme.py apps/windows-panel/ui apps/windows-panel/main.py
git commit -m "feat(panel): Stark shell window and R3 confirm"
```

---

### Task 5: Home + STATE tabs

**Files:**
- Create: `apps/windows-panel/ui/home.py`
- Create: `apps/windows-panel/ui/state_view.py`
- Modify: `apps/windows-panel/ui/app.py`

**Interfaces:**
- Home calls `panel.status_strip()`, `today_brief()`, `session_start()`, `workday(dry=...)`, `write_brief()`
- Workday (non-dry) and write_brief require `confirm.ask` before call
- STATE shows `panel.read_text("STATE.md")` in a read-only textbox

- [ ] **Step 1: Implement `HomeFrame`** with status labels, brief preview (`CTkTextbox` read-only), buttons Session Start / Dry-run Workday / Start Workday / Regenerate Brief

- [ ] **Step 2: Implement `StateFrame`** read-only textbox + Refresh

- [ ] **Step 3: Wire into `JarvisApp.show`**

- [ ] **Step 4: Manual check on chandan** — Dry-run Workday succeeds; Start Workday shows confirm

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(panel): Home and STATE tabs"
```

---

### Task 6: Skills + POLICY tabs

**Files:**
- Create: `apps/windows-panel/ui/skills.py`
- Create: `apps/windows-panel/ui/policy.py`
- Modify: `apps/windows-panel/ui/app.py`

- [ ] **Step 1: SkillsFrame** — listbox of skills; detail summary; Run button. If `risk == "write"`, require confirm. For v1 Run on read skills: open `SKILL.md` in textbox (execution of bash skills on Windows may no-op with banner `"skill runner: windows stub — see SKILL.md"`); `app-control` / `workday-start` map to `launch_app` / `workday` where applicable.

- [ ] **Step 2: PolicyFrame** — load POLICY.yaml + host/permission-rules.md into tabs or stacked textboxes; Edit toggle; Save calls confirm then `panel.save_policy`; Cancel reloads from disk

- [ ] **Step 3: Wire into app**

- [ ] **Step 4: Manual** — Save cancel writes nothing; intentional save creates backup under `logs/policy-backups/`

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(panel): Skills and POLICY tabs"
```

---

### Task 7: Logs + Apps tabs

**Files:**
- Create: `apps/windows-panel/ui/logs.py`
- Create: `apps/windows-panel/ui/apps.py`
- Modify: `apps/windows-panel/ui/app.py`

- [ ] **Step 1: LogsFrame** — list files in `logs/` and `reports/`; on select, `tail_log`; filter entry by date substring

- [ ] **Step 2: AppsFrame** — list `list_apps()`; show `list_restricted()` read-only; Launch requires confirm then `launch_app`

- [ ] **Step 3: Wire into app; ensure banner shows refusal for unknown apps**

- [ ] **Step 4: Manual** — restricted paths visible; Launch chrome asks confirm

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(panel): Logs and Apps tabs"
```

---

### Task 8: PyInstaller build + install on chandan + docs

**Files:**
- Create: `apps/windows-panel/build_exe.ps1`
- Modify: `WIN_README.md`
- Create: `apps/windows-panel/README.md`

- [ ] **Step 1: Write `build_exe.ps1`**

```powershell
param([string]$JarvisRoot = "C:\Users\rajk1\jarvis")
$ErrorActionPreference = "Stop"
Set-Location "$JarvisRoot\apps\windows-panel"
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Jarvis `
  --paths "$JarvisRoot\scripts\win" `
  --add-data "$JarvisRoot\apps\windows-panel\theme.py;." `
  main.py
New-Item -ItemType Directory -Force -Path "$JarvisRoot\apps" | Out-Null
Copy-Item -Force ".\dist\Jarvis.exe" "$JarvisRoot\apps\Jarvis.exe"
$desk = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$desk\JARVIS.lnk")
$sc.TargetPath = "$JarvisRoot\apps\Jarvis.exe"
$sc.WorkingDirectory = "$JarvisRoot"
$sc.Save()
Write-Output "INSTALLED=$JarvisRoot\apps\Jarvis.exe"
```

- [ ] **Step 2: Sync `apps/windows-panel` to chandan** (CopyFromBox or tar) into `C:\Users\rajk1\jarvis\apps\windows-panel` including updated `scripts\win\lib_jarvis.py`

- [ ] **Step 3: Run build on chandan**

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\rajk1\jarvis\apps\windows-panel\build_exe.ps1
```

Expected: `INSTALLED=C:\Users\rajk1\jarvis\apps\Jarvis.exe`

- [ ] **Step 4: Smoke on chandan** (from design acceptance list)

1. Double-click `Jarvis.exe` / Desktop `JARVIS` → Home loads  
2. Dry-run Workday → success banner + audit line  
3. POLICY open; Cancel does not write  
4. Confirm `block_delete` still refuses `STATE.md` via panel path if exposed  
5. Apps lists allowlist  

- [ ] **Step 5: Update WIN_README.md** with panel launch instructions; commit on box

```bash
git add apps/windows-panel WIN_README.md
git commit -m "feat(panel): PyInstaller build script and Windows install docs"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|---|---|
| Standalone exe / PyInstaller | 8 |
| Local-only Stark HUD | 4–7 |
| Root discovery + picker | 1, 4 |
| Home / Skills / POLICY / Logs / Apps / STATE | 5–7 |
| R3 confirms | 4–7 |
| POLICY backup on save | 3, 6 |
| Audit JSONL | 3 |
| block_delete authoritative | 3, 8 |
| Workday / session / brief via scripts/win | 3, 5 |
| Unit tests for panel_api | 1–3 |
| Desktop shortcut | 8 |

## Self-review notes

- No TBD placeholders.
- `JARVIS_HOME` override keeps box tests working despite hardcoded Windows default.
- Skill “Run” on Windows is intentionally stubby for bash-only skills; app-control/workday map to real panel actions.
- Build must run on `chandan` (Windows); box develops and unit-tests `panel_api` only.
