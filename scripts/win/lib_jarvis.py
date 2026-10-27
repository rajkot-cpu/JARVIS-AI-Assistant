from __future__ import annotations
import json, os, re, sys
from datetime import datetime, time, timezone, timedelta
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

def fix_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

fix_stdout()

def jarvis_home() -> Path:
    env = os.environ.get("JARVIS_HOME", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return Path(r"C:\Users\rajk1\jarvis")

def now_ist() -> datetime:
    return datetime.now(IST)

def section(md: str, heading: str) -> str:
    pat = rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    m = re.search(pat, md)
    text = (m.group(1).strip() if m else "")
    # Windows cp1252-safe-ish: replace common unicode arrows
    return text.replace("→", "->").replace("—", "-").replace("–", "-")

def append_audit(task: str, action: str, result: str, undo: str) -> None:
    p = jarvis_home() / "logs" / "audit.jsonl"
    e = {
        "time": now_ist().isoformat(timespec="seconds"),
        "task": task,
        "action": action,
        "result": result,
        "undo": undo,
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

def quiet_hours_active(policy_text: str | None = None) -> bool:
    start, end = time(22, 0), time(7, 0)
    if policy_text:
        m = re.search(r'quiet_hours:\s*"?(\d{2}):(\d{2})-(\d{2}):(\d{2})', policy_text)
        if m:
            start = time(int(m.group(1)), int(m.group(2)))
            end = time(int(m.group(3)), int(m.group(4)))
    t = now_ist().time()
    if start > end:
        return t >= start or t < end
    return start <= t < end

def load_policy() -> str:
    return (jarvis_home() / "POLICY.yaml").read_text(encoding="utf-8")
