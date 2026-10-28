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
    out: list[dict] = []
    for line in lines[-n:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"raw": line})
    return out
