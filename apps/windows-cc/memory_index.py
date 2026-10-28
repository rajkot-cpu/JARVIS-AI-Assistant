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
