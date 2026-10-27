#!/usr/bin/env python3
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_jarvis import jarvis_home

def main():
    if len(sys.argv) != 2:
        print("Usage: block_delete.py <path>"); sys.exit(2)
    target = Path(sys.argv[1]).resolve()
    fixtures = (jarvis_home() / "fixtures").resolve()
    allow = os.environ.get("JARVIS_ALLOW_DELETE") == "1"
    in_fix = False
    try:
        target.relative_to(fixtures)
        in_fix = True
    except ValueError:
        pass
    if not allow:
        print(f"BLOCKED: JARVIS_ALLOW_DELETE not set (approval missing) for {sys.argv[1]}"); sys.exit(1)
    if not in_fix:
        print(f"BLOCKED: {sys.argv[1]} is outside fixtures/"); sys.exit(1)
    if target.exists():
        target.unlink()
        print(f"DELETED: {sys.argv[1]}")
    else:
        print(f"MISSING: {sys.argv[1]}"); sys.exit(1)

if __name__ == "__main__":
    main()
