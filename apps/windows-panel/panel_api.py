from __future__ import annotations
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

_WIN_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "win"
if _WIN_SCRIPTS.is_dir() and str(_WIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_WIN_SCRIPTS))

IST = timezone(timedelta(hours=5, minutes=30))

WIN_APP_MAP = {
    "chrome": ["chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
    "terminal": ["wt.exe", "powershell.exe"],
}

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

    # ---- reads ----
    def read_text(self, rel: str) -> str:
        p = (self.root / rel).resolve()
        if p != self.root and self.root not in p.parents:
            raise ValueError(f"path outside JARVIS_ROOT: {rel}")
        return p.read_text(encoding="utf-8") if p.is_file() else ""

    def parse_policy(self) -> dict:
        try:
            data = yaml.safe_load(self.read_text("POLICY.yaml"))
        except yaml.YAMLError:
            return {}
        return data if isinstance(data, dict) else {}

    def _today(self) -> str:
        return datetime.now(IST).strftime("%Y-%m-%d")

    def status_strip(self) -> dict:
        text = self.read_text("POLICY.yaml")
        pol = self.parse_policy()
        try:
            import lib_jarvis
            quiet = bool(lib_jarvis.quiet_hours_active(text))
        except Exception:
            quiet = False
        return {
            "root": str(self.root),
            "policy_ok": pol.get("status") == "approved",
            "quiet_hours": quiet,
            "today": self._today(),
        }

    def today_brief(self) -> str:
        return self.read_text(f"reports/{self._today()}.md")

    def list_skills(self) -> list[dict]:
        out: list[dict] = []
        sd = self.root / "skills"
        if not sd.is_dir():
            return out
        for d in sorted(p for p in sd.iterdir() if p.is_dir()):
            md = d / "SKILL.md"
            summary = ""
            if md.is_file():
                lines = [l.strip() for l in md.read_text(encoding="utf-8").splitlines()]
                lines = [l for l in lines if l]
                if lines and lines[0].startswith("#"):
                    lines = lines[1:]
                summary = (lines[0] if lines else "")[:160]
            risk = "write" if ("app-control" in d.name or "workday" in d.name) else "read"
            out.append({"name": d.name, "path": d, "summary": summary, "risk": risk})
        return out

    def list_log_files(self) -> list[Path]:
        ld = self.root / "logs"
        if not ld.is_dir():
            return []
        files = [p for p in ld.rglob("*") if p.is_file()]
        return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    def tail_log(self, path: Path, max_lines: int = 200) -> str:
        p = Path(path).resolve()
        if self.root not in p.parents or not p.is_file():
            return ""
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-max_lines:])

    def list_apps(self) -> list[dict]:
        allow = self.parse_policy().get("apps_allowlist") or []
        return [{"name": n, "command": WIN_APP_MAP[n]} for n in allow if n in WIN_APP_MAP]

    def list_restricted(self) -> list[str]:
        r = self.parse_policy().get("restricted") or []
        return [str(x) for x in r] if isinstance(r, list) else []

    # ---- actions ----
    def audit(self, action: str, path: str, result: str, detail: str = "") -> None:
        import json
        now = datetime.now(timezone.utc)
        rec = {
            "ts_utc": now.isoformat(),
            "ts_ist": now.astimezone(IST).isoformat(),
            "actor": "windows-panel",
            "action": action,
            "path": str(path),
            "result": result,
            "detail": detail,
        }
        ld = self.root / "logs"
        ld.mkdir(exist_ok=True)
        with (ld / "audit.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def run_script(self, name: str, args: list[str] | None = None) -> tuple[int, str, str]:
        import os, subprocess
        script = self.root / "scripts" / "win" / f"{name}.py"
        if not script.is_file():
            return 1, "", f"script not found: {script}"
        env = os.environ | {"JARVIS_HOME": str(self.root)}
        try:
            cp = subprocess.run([sys.executable, str(script), *(args or [])],
                                capture_output=True, text=True, env=env,
                                cwd=str(self.root), timeout=300)
        except Exception as e:
            return 1, "", str(e)
        return cp.returncode, cp.stdout, cp.stderr

    def _run_audited(self, name: str, args: list[str] | None = None) -> tuple[int, str, str]:
        code, out, err = self.run_script(name, args)
        self.audit(name, f"scripts/win/{name}.py", "ok" if code == 0 else "error",
                   " ".join(args or []) + (f" rc={code}" if code else ""))
        return code, out, err

    def session_start(self) -> tuple[int, str, str]:
        return self._run_audited("session_start")

    def workday(self, dry: bool = False) -> tuple[int, str, str]:
        return self._run_audited("workday_start", ["--dry"] if dry else [])

    def write_brief(self) -> tuple[int, str, str]:
        return self._run_audited("brief", ["--write"])

    def save_policy(self, new_text: str) -> Path:
        try:
            data = yaml.safe_load(new_text)
        except yaml.YAMLError as e:
            self.audit("save_policy", "POLICY.yaml", "refused", f"bad yaml: {e}")
            raise ValueError(f"POLICY.yaml does not parse: {e}") from e
        if not isinstance(data, dict):
            self.audit("save_policy", "POLICY.yaml", "refused", "not a mapping")
            raise ValueError("POLICY.yaml must be a YAML mapping")
        pol = self.root / "POLICY.yaml"
        bdir = self.root / "logs" / "policy-backups"
        bdir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(IST).strftime("%Y%m%d-%H%M%S")
        backup = bdir / f"POLICY-{stamp}.yaml"
        n = 1
        while backup.exists():
            backup = bdir / f"POLICY-{stamp}-{n}.yaml"; n += 1
        backup.write_text(pol.read_text(encoding="utf-8") if pol.is_file() else "", encoding="utf-8")
        pol.write_text(new_text, encoding="utf-8")
        self.audit("save_policy", "POLICY.yaml", "ok", f"backup={backup.name}")
        return pol

    def block_delete(self, target: Path) -> tuple[int, str, str]:
        code, out, err = self.run_script("block_delete", [str(target)])
        self.audit("block_delete", str(target), "allowed" if code == 0 else "refused", f"rc={code}")
        return code, out, err

    def launch_app(self, name: str) -> tuple[int, str, str]:
        import shutil, subprocess
        allow = self.parse_policy().get("apps_allowlist") or []
        if name not in allow or name not in WIN_APP_MAP:
            self.audit("launch_app", name, "refused", "not in allowlist")
            return 1, "", f"app not allowlisted: {name}"
        for cmd in WIN_APP_MAP[name]:
            exe = shutil.which(cmd) or (cmd if Path(cmd).is_absolute() and Path(cmd).is_file() else None)
            if not exe:
                continue
            try:
                subprocess.Popen([exe], close_fds=True)
            except Exception as e:
                self.audit("launch_app", name, "error", str(e))
                return 1, "", str(e)
            self.audit("launch_app", name, "ok", exe)
            return 0, f"launched {exe}", ""
        self.audit("launch_app", name, "refused", "app binary not found")
        return 1, "", "app binary not found"
