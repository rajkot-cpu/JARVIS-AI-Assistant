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
