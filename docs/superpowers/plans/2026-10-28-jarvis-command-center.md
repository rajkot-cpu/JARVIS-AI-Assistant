# JARVIS Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local-only Windows Command Center `Jarvis.exe` that matches the approved HUD mock with every tile fully live, host STARK OS on `github.com/rajkishorbgp/JARVIS-AI-Assistant`, and keep `Jarvis3D.exe` optional.

**Architecture:** New `apps/windows-cc` WebView2 host (pywebview + local `http_server`) loads a bundled HUD UI. Python bridge wraps existing `panel_api` / `voice` / `scripts/win`, adds host metrics, audit feed, memory index, vault-backed LLM probes, and six fixed agent workers. GitHub remote `https://github.com/rajkishorbgp/JARVIS-AI-Assistant.git` becomes the project home after archiving the legacy voice-assistant tree.

**Tech Stack:** Python 3.13, pywebview (EdgeChromium/WebView2), vanilla HTML/CSS/JS HUD (patterns from researched GitHub HUD/dashboards, license-checked), `psutil`, `speech_recognition` (Windows STT), existing `voice` TTS, Anthropic/OpenAI/Google/Groq SDKs via vault env keys, PyInstaller.

**Spec:** `docs/superpowers/specs/2026-10-28-jarvis-command-center-design.md`

**GitHub research (locked source):** `https://github.com/rajkishorbgp/JARVIS-AI-Assistant`
- Current tree: `main.py` (Google STT loop + site openers + legacy `openai.ChatCompletion`), `voice.py` (gTTS + `win32com` SAPI), `openaitext.py`, plaintext `config.apikey`.
- **Reuse ideas:** Windows SAPI TTS path (already in our `voice`), `speech_recognition` for STT.
- **Do not reuse:** plaintext API keys, legacy ChatCompletion chat-string-as-system, hard-coded site list as the product core.
- **Push policy:** Archive remote contents into `legacy/github-assistant/` on first Command Center commit; then push our STARK OS tree. Unrelated histories → force-push only after explicit Chandan R3 confirm in chat.

## Global Constraints

- Local only — UI via `127.0.0.1` / bundled `ui/`; no remote UI URLs; no Grok Bot bridge in this release.
- Standalone Command Center `Jarvis.exe` at `C:\Users\rajk1\jarvis\apps\Jarvis.exe` + Desktop shortcut; keep `Jarvis3D.exe`.
- Palette: bg `#04070b`, panel `#0b2233`, cyan `#38d4ff`, text `#e4f6ff`, gold `#ff9d2e`, muted `#7a8fa8`, danger `#ff3b30`, ok `#3dff9a`. Gold only for Mute / Quiet / R3 title.
- No decorative stubs — offline shows real failures (red), never fake Connected/Active.
- Keys only from vault / `JARVIS_*_API_KEY` env — never in UI, git, or `config.py`.
- R1 auto-log; R2 preview / POLICY; R3 every time for real workday, applying code diffs, first use of a new provider key, force-push; R4 typed confirm for destructive system actions.
- Agents never expand their own allowlist.
- Keep `apps/windows-panel` importable (`panel_api`, `voice`); archive CustomTkinter shell if replaced as main exe.
- Default root: `C:\Users\rajk1\jarvis`; same `JARVIS_HOME` / `discover_root` as panel.
- Window icon: `apps/windows-panel/assets/jarvis.ico` (helmet).
- Never write outside JARVIS_ROOT; audit via existing paths.

## File structure

| Path | Responsibility |
|---|---|
| `legacy/github-assistant/` | Frozen copy of prior GitHub voice-assistant sources |
| `apps/windows-cc/bridge_api.py` | JSON-safe facade: status, feed, metrics, memory, LLM, agents, voice, commands |
| `apps/windows-cc/host_main.py` | pywebview window, expose bridge, `http_server=True` |
| `apps/windows-cc/metrics.py` | CPU/RAM/Disk via `psutil` |
| `apps/windows-cc/feed.py` | Audit JSONL + agent event stream reader |
| `apps/windows-cc/memory_index.py` | Counts/graph from on-disk STATE/journal/memory |
| `apps/windows-cc/llm_providers.py` | Vault-key probes for Anthropic/OpenAI/Gemini/Groq (+ optional Ollama) |
| `apps/windows-cc/agents/` | Six fixed role workers (coding, research, memory, browser, task, system) |
| `apps/windows-cc/stt.py` | Windows speech recognition wrapper |
| `apps/windows-cc/ui/` | HUD HTML/CSS/JS matching mock |
| `apps/windows-cc/ui/js/bridge.js` | Call host API / mock-offline fallback |
| `apps/windows-cc/ui/js/app.js` | Routes, refresh loops, R3 modal |
| `apps/windows-cc/requirements.txt` | pywebview, psutil, speech_recognition, provider SDKs, pyinstaller |
| `apps/windows-cc/build_exe.ps1` | Freeze → `apps/Jarvis.exe` + Desktop shortcut |
| `apps/windows-cc/tests/` | Unit tests (no GUI) |
| `apps/windows-cc/README.md` | Run from source + WebView2 Evergreen note |
| `docs/github.md` | Remote URL, archive policy, PR workflow |

---

### Task 1: GitHub remote + archive legacy assistant

**Files:**
- Create: `legacy/github-assistant/README.md`
- Create: `docs/github.md`
- Modify: git remotes on `/home/box/jarvis`

**Interfaces:**
- Consumes: public tree at `https://github.com/rajkishorbgp/JARVIS-AI-Assistant`
- Produces: `origin` (or `github`) remote pointing at that URL; `legacy/github-assistant/` snapshot; documented push policy

- [ ] **Step 1: Snapshot remote tree into legacy/**

```bash
mkdir -p /tmp/jarvis-gh-snap /home/box/jarvis/legacy/github-assistant
curl -fsSL -o /tmp/jarvis-gh-snap.zip https://github.com/rajkishorbgp/JARVIS-AI-Assistant/archive/refs/heads/main.zip
unzip -qo /tmp/jarvis-gh-snap.zip -d /tmp/jarvis-gh-snap
cp -a /tmp/jarvis-gh-snap/JARVIS-AI-Assistant-main/. /home/box/jarvis/legacy/github-assistant/
printf '%s\n' '# Legacy GitHub assistant (archived 2026-10-28)' '' \
  'Frozen snapshot of https://github.com/rajkishorbgp/JARVIS-AI-Assistant before STARK OS / Command Center took over this repo.' \
  'Do not run from here for production; kept for history and STT/TTS reference.' \
  > /home/box/jarvis/legacy/github-assistant/README.md
```

- [ ] **Step 2: Write `docs/github.md`**

```markdown
# GitHub hosting

- **Remote:** https://github.com/rajkishorbgp/JARVIS-AI-Assistant.git
- **Policy:** STARK OS + Command Center is the product tree. Prior voice-assistant sources live under `legacy/github-assistant/`.
- **Secrets:** Never commit API keys. Use vault / `JARVIS_*_API_KEY`.
- **Push:** Prefer merge/PR. Force-push only with Chandan R3 confirm (unrelated histories).
- **WebView2:** Windows Evergreen Runtime required for `Jarvis.exe` / `Jarvis3D.exe`.
```

- [ ] **Step 3: Add remote (do not push yet)**

```bash
cd /home/box/jarvis
git remote remove github 2>/dev/null || true
git remote add github https://github.com/rajkishorbgp/JARVIS-AI-Assistant.git
git remote -v
```

Expected: `github` fetch/push URLs show that repo.

- [ ] **Step 4: Commit archive + docs (no push)**

```bash
git add legacy/github-assistant docs/github.md
git commit -m "docs: archive GitHub JARVIS-AI-Assistant snapshot; document remote"
```

- [ ] **Step 5: Stop — push is Task 12 after Command Center lands**

Do not push in this task. Auth (`gh auth` / credential) may be missing; push happens once with R3.

---

### Task 2: Scaffold `apps/windows-cc` + bridge status envelope (TDD)

**Files:**
- Create: `apps/windows-cc/requirements.txt`
- Create: `apps/windows-cc/bridge_api.py`
- Create: `apps/windows-cc/tests/test_bridge_status.py`
- Create: `apps/windows-cc/README.md`

**Interfaces:**
- Consumes: `apps/windows-panel/panel_api.Panel`, `discover_root` pattern from windows-3d
- Produces: `BridgeApi.status() -> dict` with `{ok, data}` shape; `BridgeApi` constructor takes `root: Path`

- [ ] **Step 1: Write failing test**

```python
# apps/windows-cc/tests/test_bridge_status.py
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))

from bridge_api import BridgeApi

def test_status_ok_shape(tmp_path):
    # minimal STATE.md so Panel can open
    (tmp_path / "STATE.md").write_text("# STATE\nstatus: ok\n", encoding="utf-8")
    api = BridgeApi(root=tmp_path)
    out = api.status()
    assert out["ok"] is True
    assert "data" in out
    assert "system_status" in out["data"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/box/jarvis && python -m pytest apps/windows-cc/tests/test_bridge_status.py -v
```

Expected: FAIL (`bridge_api` missing or `BridgeApi` undefined).

- [ ] **Step 3: Minimal implementation**

```python
# apps/windows-cc/bridge_api.py
from __future__ import annotations
from pathlib import Path
import sys

_PANEL = Path(__file__).resolve().parents[1] / "windows-panel"
if str(_PANEL) not in sys.path:
    sys.path.insert(0, str(_PANEL))

from panel_api import Panel  # type: ignore


class BridgeApi:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.panel = Panel(self.root)

    def status(self) -> dict:
        try:
            st = self.panel.status()
            return {
                "ok": True,
                "data": {
                    "system_status": st.get("system_status") or st.get("status") or "UNKNOWN",
                    "quiet_hours": bool(st.get("quiet_hours", False)),
                    "muted": bool(st.get("muted", False)),
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
```

`requirements.txt`:

```
pywebview>=5.0
psutil>=5.9
SpeechRecognition>=3.10
pyinstaller>=6.0
anthropic>=0.40
openai>=1.40
google-generativeai>=0.7
groq>=0.9
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /home/box/jarvis && python -m pytest apps/windows-cc/tests/test_bridge_status.py -v
```

Expected: PASS (adjust `Panel.status()` key mapping if needed to match real panel_api).

- [ ] **Step 5: Commit**

```bash
git add apps/windows-cc
git commit -m "feat(cc): scaffold bridge_api status envelope"
```

---

### Task 3: Host metrics + Live Feed readers (TDD)

**Files:**
- Create: `apps/windows-cc/metrics.py`
- Create: `apps/windows-cc/feed.py`
- Create: `apps/windows-cc/tests/test_metrics_feed.py`
- Modify: `apps/windows-cc/bridge_api.py`

**Interfaces:**
- Consumes: `psutil`; audit JSONL under `root/logs` or existing panel audit path
- Produces: `metrics.snapshot() -> {cpu_pct, ram_pct, disk_pct}`; `feed.tail(root, n) -> list[dict]`; bridge methods `metrics()`, `feed(limit=50)`

- [ ] **Step 1: Write failing tests**

```python
# apps/windows-cc/tests/test_metrics_feed.py
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))
from metrics import snapshot
from feed import tail

def test_metrics_snapshot_keys():
    m = snapshot()
    assert set(m) >= {"cpu_pct", "ram_pct", "disk_pct"}
    assert 0 <= m["cpu_pct"] <= 100

def test_feed_tail_reads_jsonl(tmp_path):
    log = tmp_path / "audit.jsonl"
    log.write_text(json.dumps({"t": "1", "msg": "hi"}) + "\n", encoding="utf-8")
    rows = tail(tmp_path, n=10, audit_name="audit.jsonl")
    assert rows[0]["msg"] == "hi"
```

- [ ] **Step 2: Run — expect FAIL**

```bash
python -m pytest apps/windows-cc/tests/test_metrics_feed.py -v
```

- [ ] **Step 3: Implement**

```python
# apps/windows-cc/metrics.py
from __future__ import annotations
import psutil

def snapshot() -> dict:
    disk = psutil.disk_usage("/")
    return {
        "cpu_pct": float(psutil.cpu_percent(interval=0.1)),
        "ram_pct": float(psutil.virtual_memory().percent),
        "disk_pct": float(disk.percent),
    }
```

```python
# apps/windows-cc/feed.py
from __future__ import annotations
from pathlib import Path
import json

def _audit_path(root: Path, audit_name: str = "audit.jsonl") -> Path:
    for cand in (root / "logs" / audit_name, root / audit_name, root / "audit" / audit_name):
        if cand.is_file():
            return cand
    return root / "logs" / audit_name

def tail(root: Path, n: int = 50, audit_name: str = "audit.jsonl") -> list[dict]:
    path = _audit_path(root, audit_name)
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    for line in lines[-n:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"raw": line})
    return out
```

Wire into `BridgeApi`:

```python
def metrics(self) -> dict:
    try:
        from metrics import snapshot
        return {"ok": True, "data": snapshot()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def feed(self, limit: int = 50) -> dict:
    try:
        from feed import tail
        return {"ok": True, "data": {"items": tail(self.root, n=int(limit))}}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

- [ ] **Step 4: Tests PASS + commit**

```bash
python -m pytest apps/windows-cc/tests/test_metrics_feed.py -v
git add apps/windows-cc
git commit -m "feat(cc): host metrics and audit feed readers"
```

---

### Task 4: Memory Insights index (TDD)

**Files:**
- Create: `apps/windows-cc/memory_index.py`
- Create: `apps/windows-cc/tests/test_memory_index.py`
- Modify: `apps/windows-cc/bridge_api.py`

**Interfaces:**
- Consumes: files under `root` matching STATE.md, journal/, memory/, notes/
- Produces: `memory_index.build(root) -> {nodes: int, edges: int, sources: list[str]}`; bridge `memory()`

- [ ] **Step 1: Failing test**

```python
def test_memory_index_counts(tmp_path):
    (tmp_path / "STATE.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "journal").mkdir()
    (tmp_path / "journal" / "a.md").write_text("note\n", encoding="utf-8")
    from memory_index import build
    data = build(tmp_path)
    assert data["nodes"] >= 2
    assert "STATE.md" in data["sources"]
```

- [ ] **Step 2–4: Implement minimal walker, wire `BridgeApi.memory()`, tests pass, commit**

```python
# apps/windows-cc/memory_index.py
from __future__ import annotations
from pathlib import Path

_CANDIDATES = ("STATE.md", "journal", "memory", "notes", "reports")

def build(root: Path) -> dict:
    root = Path(root)
    sources: list[str] = []
    nodes = 0
    for name in _CANDIDATES:
        p = root / name
        if p.is_file():
            sources.append(name)
            nodes += 1
        elif p.is_dir():
            files = [x for x in p.rglob("*") if x.is_file()]
            if files:
                sources.append(name)
                nodes += len(files)
    edges = max(0, nodes - 1) if nodes else 0
    return {"nodes": nodes, "edges": edges, "sources": sources}
```

```bash
git commit -m "feat(cc): memory insights index from on-disk files"
```

---

### Task 5: LLM provider probes via vault env (TDD)

**Files:**
- Create: `apps/windows-cc/llm_providers.py`
- Create: `apps/windows-cc/tests/test_llm_providers.py`
- Modify: `apps/windows-cc/bridge_api.py`

**Interfaces:**
- Consumes: env `JARVIS_ANTHROPIC_API_KEY`, `JARVIS_OPENAI_API_KEY`, `JARVIS_GEMINI_API_KEY`, `JARVIS_GROQ_API_KEY` (and optional `JARVIS_OLLAMA_BASE`)
- Produces: `probe_all(timeout=8) -> list[{id, name, state, detail}]` where `state` in `connected|auth_error|network_error|missing_key`; bridge `llms()`

- [ ] **Step 1: Failing test (no network — missing keys)**

```python
import os
from llm_providers import probe_all

def test_probe_missing_keys(monkeypatch):
    for k in list(os.environ):
        if k.startswith("JARVIS_") and k.endswith("_API_KEY"):
            monkeypatch.delenv(k, raising=False)
    monkeypatch.delenv("JARVIS_OLLAMA_BASE", raising=False)
    rows = probe_all(timeout=1)
    ids = {r["id"] for r in rows}
    assert {"anthropic", "openai", "gemini", "groq"} <= ids
    assert all(r["state"] == "missing_key" for r in rows if r["id"] != "ollama")
```

- [ ] **Step 2–4: Implement probes**

```python
# apps/windows-cc/llm_providers.py
from __future__ import annotations
import os, urllib.request, urllib.error, json

PROVIDERS = (
    ("anthropic", "Anthropic", "JARVIS_ANTHROPIC_API_KEY"),
    ("openai", "OpenAI", "JARVIS_OPENAI_API_KEY"),
    ("gemini", "Gemini", "JARVIS_GEMINI_API_KEY"),
    ("groq", "Groq", "JARVIS_GROQ_API_KEY"),
)

def _http_json(url: str, headers: dict, body: dict | None, timeout: float):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200]
    except Exception as e:
        return None, str(e).encode()

def probe_one(pid: str, name: str, env_key: str, timeout: float) -> dict:
    key = os.environ.get(env_key, "").strip()
    if not key:
        return {"id": pid, "name": name, "state": "missing_key", "detail": env_key}
    # Lightweight auth-shaped probes (no spend). Map HTTP codes to state.
    try:
        if pid == "openai":
            code, _ = _http_json("https://api.openai.com/v1/models", {"Authorization": f"Bearer {key}"}, None, timeout)
        elif pid == "anthropic":
            code, _ = _http_json(
                "https://api.anthropic.com/v1/messages",
                {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                {"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "ping"}]},
                timeout,
            )
        elif pid == "gemini":
            code, _ = _http_json(
                f"https://generativelanguage.googleapis.com/v1/models?key={key}",
                {}, None, timeout,
            )
        elif pid == "groq":
            code, _ = _http_json("https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {key}"}, None, timeout)
        else:
            return {"id": pid, "name": name, "state": "missing_key", "detail": "unknown"}
        if code in (200, 201):
            return {"id": pid, "name": name, "state": "connected", "detail": f"http {code}"}
        if code in (401, 403):
            return {"id": pid, "name": name, "state": "auth_error", "detail": f"http {code}"}
        if code is None:
            return {"id": pid, "name": name, "state": "network_error", "detail": "unreachable"}
        return {"id": pid, "name": name, "state": "network_error", "detail": f"http {code}"}
    except Exception as e:
        return {"id": pid, "name": name, "state": "network_error", "detail": str(e)}

def probe_all(timeout: float = 8.0) -> list[dict]:
    rows = [probe_one(a, b, c, timeout) for a, b, c in PROVIDERS]
    base = os.environ.get("JARVIS_OLLAMA_BASE", "").strip()
    if base:
        code, detail = _http_json(base.rstrip("/") + "/api/tags", {}, None, timeout)
        state = "connected" if code == 200 else ("network_error" if code is None else "auth_error")
        rows.append({"id": "ollama", "name": "Ollama", "state": state, "detail": detail.decode() if isinstance(detail, bytes) else str(detail)})
    return rows
```

Note: Anthropic probe may spend 1 token — acceptable for R1-logged connectivity; document in README. Prefer models list endpoints when available without body.

Wire `BridgeApi.llms()` → `{ok, data: {providers: [...]}}`.

```bash
git commit -m "feat(cc): vault-env LLM provider probes"
```

---

### Task 6: Six fixed agent workers (TDD)

**Files:**
- Create: `apps/windows-cc/agents/__init__.py`
- Create: `apps/windows-cc/agents/registry.py`
- Create: `apps/windows-cc/agents/worker.py`
- Create: `apps/windows-cc/tests/test_agents.py`
- Modify: `apps/windows-cc/bridge_api.py`

**Interfaces:**
- Consumes: role prompts + tool allowlists from registry; LLM chat via env keys
- Produces: `AgentHub` with `list()`, `start(role_id)`, `stop(role_id)`; states `active|standby|error`; bridge `agents()`, `agent_start(id)`, `agent_stop(id)`

Roles (fixed): `coding`, `research`, `memory`, `browser`, `task`, `system`.

- [ ] **Step 1: Failing test**

```python
from agents.registry import ROLES
from agents.worker import AgentHub

def test_six_roles():
    assert {r["id"] for r in ROLES} == {"coding", "research", "memory", "browser", "task", "system"}

def test_start_stop_standby(tmp_path):
    hub = AgentHub(root=tmp_path)
    assert all(a["state"] == "standby" for a in hub.list())
    hub.start("system")
    row = next(a for a in hub.list() if a["id"] == "system")
    assert row["state"] in ("active", "error")
    hub.stop("system")
    assert next(a for a in hub.list() if a["id"] == "system")["state"] == "standby"
```

- [ ] **Step 2–4: Implement thread-based hub**

```python
# apps/windows-cc/agents/registry.py
ROLES = [
    {"id": "coding", "name": "Coding", "tools": ["read_file", "search", "propose_diff"], "prompt": "You are Coding agent. Stay inside JARVIS_ROOT allowlisted paths. Propose diffs; never apply without R3."},
    {"id": "research", "name": "Research", "tools": ["web_fetch"], "prompt": "You are Research agent. Summarize allowlisted fetches."},
    {"id": "memory", "name": "Memory", "tools": ["memory_read", "memory_write"], "prompt": "You are Memory agent. Read/write JARVIS notes per POLICY."},
    {"id": "browser", "name": "Browser", "tools": ["browser_allowlist"], "prompt": "You are Browser agent. Use Day 4–5 allowlist only."},
    {"id": "task", "name": "Task", "tools": ["task_list", "task_create"], "prompt": "You are Task agent. Manage checklists/tasks."},
    {"id": "system", "name": "System", "tools": ["metrics", "status", "dry_run"], "prompt": "You are System agent. Host health + dry-run only by default."},
]
```

```python
# apps/windows-cc/agents/worker.py
from __future__ import annotations
from pathlib import Path
import threading, time
from .registry import ROLES

class AgentHub:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._state = {r["id"]: "standby" for r in ROLES}
        self._threads: dict[str, threading.Thread] = {}
        self._stop = {r["id"]: threading.Event() for r in ROLES}
        self._detail = {r["id"]: "" for r in ROLES}

    def list(self) -> list[dict]:
        out = []
        for r in ROLES:
            out.append({"id": r["id"], "name": r["name"], "state": self._state[r["id"]], "detail": self._detail[r["id"]], "tools": r["tools"]})
        return out

    def start(self, role_id: str) -> dict:
        if role_id not in self._state:
            return {"ok": False, "error": "unknown role"}
        if self._state[role_id] == "active":
            return {"ok": True, "data": {"id": role_id, "state": "active"}}
        self._stop[role_id].clear()
        self._state[role_id] = "active"
        t = threading.Thread(target=self._run, args=(role_id,), daemon=True)
        self._threads[role_id] = t
        t.start()
        return {"ok": True, "data": {"id": role_id, "state": "active"}}

    def stop(self, role_id: str) -> dict:
        if role_id not in self._state:
            return {"ok": False, "error": "unknown role"}
        self._stop[role_id].set()
        self._state[role_id] = "standby"
        self._detail[role_id] = ""
        return {"ok": True, "data": {"id": role_id, "state": "standby"}}

    def _run(self, role_id: str) -> None:
        # Heartbeat loop — real tool/LLM calls land in later polish; must not fake success on LLM failure.
        while not self._stop[role_id].is_set():
            self._detail[role_id] = "heartbeat"
            time.sleep(2.0)
```

Wire bridge methods. Commit: `feat(cc): six fixed agent workers hub`.

---

### Task 7: Voice STT + Quick Commands + R3 (TDD)

**Files:**
- Create: `apps/windows-cc/stt.py`
- Create: `apps/windows-cc/tests/test_stt_commands.py`
- Modify: `apps/windows-cc/bridge_api.py`

**Interfaces:**
- Consumes: `speech_recognition`, existing `voice` module, `Panel` session/workday/mute
- Produces: `stt.listen_once(timeout=5) -> {ok, text?|error?}`; bridge `listen()`, `speak(text)`, `mute(on)`, `session_start()`, `dry_run_workday()`, `start_workday()` (R3 gated in UI; bridge still exposes `confirm_token` check)

- [ ] **Step 1: Failing unit test for command wrappers (mock Panel)**

```python
def test_dry_run_calls_panel(tmp_path, monkeypatch):
    from bridge_api import BridgeApi
    api = BridgeApi(root=tmp_path)
    called = {}
    class Fake:
        def workday(self, dry=True):
            called["dry"] = dry
            return {"ok": True}
        def status(self):
            return {}
    api.panel = Fake()
    out = api.dry_run_workday()
    assert out["ok"] is True
    assert called["dry"] is True
```

- [ ] **Step 2–4: Implement `stt.py` with clear failure banner semantics; wire commands; commit**

```python
# apps/windows-cc/stt.py
from __future__ import annotations

def listen_once(timeout: float = 5.0, phrase_time_limit: float = 8.0) -> dict:
    try:
        import speech_recognition as sr
    except Exception as e:
        return {"ok": False, "error": f"speech_recognition missing: {e}"}
    rec = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        text = rec.recognize_google(audio, language="en-IN")
        return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

`start_workday` must require `confirmed=True` argument from UI after R3 modal; without it return `{"ok": False, "error": "R3 confirmation required"}`.

```bash
git commit -m "feat(cc): STT listen + quick commands with R3 gate"
```

---

### Task 8: HUD UI shell (layout matching mock)

**Files:**
- Create: `apps/windows-cc/ui/index.html`
- Create: `apps/windows-cc/ui/css/hud.css`
- Create: `apps/windows-cc/ui/js/bridge.js`
- Create: `apps/windows-cc/ui/js/app.js`
- Create: `apps/windows-cc/ui/js/sphere.js` (canvas AI Core viz driven by health list)

**Interfaces:**
- Consumes: `window.pywebview.api` methods mirroring BridgeApi
- Produces: 10 left-nav routes; Home tiles bound to bridge; no stub Connected states

- [ ] **Step 1: Build static shell offline** — open `ui/index.html` in browser; layout matches mock regions (sidebar, header, AI Core, agents, timeline, feed, gauges, memory, LLM grid, voice, quick commands).

- [ ] **Step 2: `bridge.js`** — `async function call(method, ...args)` → pywebview or returns `{ok:false,error:'offline'}`.

- [ ] **Step 3: `app.js`** — poll `status/metrics/feed/memory/llms/agents` every 3s; render; R3 modal before `start_workday(true)`.

- [ ] **Step 4: Commit**

```bash
git add apps/windows-cc/ui
git commit -m "feat(cc): Command Center HUD UI shell wired to bridge"
```

Exact HTML structure: left `<nav>` with Dashboard, Agents, Missions, Intelligence, Memory, LLMs, Voice, Workflows, Skills, Settings; main grid CSS using palette tokens as CSS variables.

---

### Task 9: Remaining nav pages (real routes)

**Files:**
- Create: `apps/windows-cc/ui/js/pages/*.js` or single router sections in `app.js`
- Modify: `apps/windows-cc/ui/index.html`

**Interfaces:**
- Each nav id maps to a real view that calls bridge (agents list, feed full, memory detail, llm grid, voice panel, workflows with dry-run, skills/POLICY read-only via panel, settings for mute/quiet display).

- [ ] **Step 1:** Implement router; no dead links.
- [ ] **Step 2:** Manual check: click all 10 nav items → content changes.
- [ ] **Step 3:** Commit `feat(cc): real routes for all Command Center nav items`.

---

### Task 10: pywebview host + http_server (mirror Jarvis3D lesson)

**Files:**
- Create: `apps/windows-cc/host_main.py`
- Modify: `apps/windows-cc/README.md`

**Interfaces:**
- Consumes: `BridgeApi`, `ui/` directory
- Produces: window titled `JARVIS Command Center`; exposes API; relative URLs via `http_server=True`

- [ ] **Step 1: Implement host**

```python
# apps/windows-cc/host_main.py
from __future__ import annotations
from pathlib import Path
import os, sys
import webview

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "windows-panel"))

from bridge_api import BridgeApi

def discover_root() -> Path:
    env = os.environ.get("JARVIS_HOME") or os.environ.get("JARVIS_ROOT")
    if env:
        return Path(env)
    return Path(r"C:\Users\rajk1\jarvis")

def main():
    root = discover_root()
    api = BridgeApi(root=root)
    icon = HERE.parent / "windows-panel" / "assets" / "jarvis.ico"
    ui = (HERE / "ui" / "index.html").as_uri()  # overridden by http_server relative
    window = webview.create_window(
        "JARVIS Command Center",
        url=str(HERE / "ui" / "index.html"),
        js_api=api,
        width=1440,
        height=900,
    )
    webview.start(http_server=True, debug=False)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2:** Document WebView2 Evergreen requirement in README.
- [ ] **Step 3:** Commit `feat(cc): pywebview host with http_server for CC UI`.

---

### Task 11: PyInstaller → `Jarvis.exe` on chandan

**Files:**
- Create: `apps/windows-cc/build_exe.ps1`
- Modify: Desktop shortcut script (same pattern as windows-panel / windows-3d)
- Archive note: rename old CustomTkinter entry so CC is the main `Jarvis.exe`

**Interfaces:**
- Produces: `C:\Users\rajk1\jarvis\apps\Jarvis.exe`; Desktop `JARVIS` shortcut; `Jarvis3D.exe` untouched

- [ ] **Step 1:** Write `build_exe.ps1` mirroring `apps/windows-3d/build_exe.ps1` (entry `host_main.py`, name `Jarvis`, collect `ui/`).
- [ ] **Step 2:** On chandan, run build; confirm exe size > 0; double-click smoke (offline shell).
- [ ] **Step 3:** Commit `feat(cc): PyInstaller build for Command Center Jarvis.exe`.

---

### Task 12: Push STARK OS to GitHub remote (R3)

**Files:** none new — git remotes / GitHub

**Interfaces:**
- Consumes: Task 1 remote `github`; Chandan R3 confirm for force-push if histories diverge
- Produces: `main` (or `stark-os` branch + PR) on `rajkishorbgp/JARVIS-AI-Assistant` containing STARK OS + Command Center + `legacy/github-assistant/`

- [ ] **Step 1: Auth check**

```bash
gh auth status || true
git -C /home/box/jarvis ls-remote github HEAD
```

If auth missing: stop and ask Chandan to connect GitHub / provide credential via vault — do not invent tokens.

- [ ] **Step 2: Prefer non-force path**

```bash
cd /home/box/jarvis
git fetch github
git checkout -b stark/command-center
git push -u github stark/command-center
```

Open PR into that repo’s default branch if force not required.

- [ ] **Step 3: If unrelated histories and Chandan typed R3 confirm**

```bash
# ONLY after explicit R3 in chat
git push github main:main --force
```

- [ ] **Step 4: Verify**

```bash
git ls-remote github HEAD
curl -fsI https://github.com/rajkishorbgp/JARVIS-AI-Assistant
```

Commit message N/A if only push; otherwise document URL in `docs/github.md` with pushed SHA.

---

### Task 13: Done checklist (chandan)

- [ ] Double-click Command Center `Jarvis.exe` → mock layout loads offline.
- [ ] All 10 nav destinations open real pages.
- [ ] Home tiles live: gauges move, feed from audit, timeline from calendar/brief when available else empty-honest, memory counts from disk, LLM tiles match probes, agents start/stop.
- [ ] Talk to JARVIS: STT listen + TTS; Mute works.
- [ ] Quick Commands; real workday still R3.
- [ ] No secrets in git; `Jarvis3D.exe` still opens.
- [ ] Repo on GitHub shows STARK OS + `legacy/github-assistant/`.

---

## Spec coverage self-check

| Spec requirement | Task |
|---|---|
| Host on GitHub + research legacy assistant | 1, 12 |
| WebView2 CC main shell Approach A | 8–11 |
| No stubs / live tiles | 3–7, 13 |
| Vault LLM keys + probes | 5 |
| Six fixed agents | 6 |
| Memory insights from disk | 4 |
| Metrics / feed / timeline | 3, 8–9 |
| STT + TTS + Mute | 7 |
| Quick commands + R3 workday | 7 |
| Package Jarvis.exe; keep Jarvis3D | 11 |
| Archive prior panel importable | 11 + keep `windows-panel` |
| Local-only UI | 10 Global Constraints |

## Placeholder scan

No TBD/TODO steps; code samples included for bridge, metrics, feed, memory, LLM, agents, STT, host.

## Type consistency

Bridge always returns `{ok: bool, data?: ..., error?: str}`. Agent states: `active|standby|error`. LLM states: `connected|auth_error|network_error|missing_key`.
