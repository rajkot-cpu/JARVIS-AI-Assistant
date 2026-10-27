#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_jarvis import jarvis_home, section, quiet_hours_active, load_policy, now_ist, append_audit
import session_start, brief

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    J = jarvis_home()
    print("=== session_start ===")
    session_start.main()
    print("\n=== brief ===")
    text = brief.build()
    D = now_ist().strftime("%Y-%m-%d")
    out = J / "reports" / f"{D}.md"
    if args.dry:
        print("[dry] would write", out)
        print(text[:400], "...")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        append_audit("workday-start", "win_workday_start", str(out), f"delete {out}")
        print("wrote", out)
    state = (J / "STATE.md").read_text(encoding="utf-8")
    decisions = [ln.strip()[2:] for ln in section(state, "Decisions owed").splitlines() if ln.strip().startswith("-")]
    next_d = decisions[0] if decisions else "(none)"
    q = "quiet" if quiet_hours_active(load_policy()) else "active hours"
    print("\n=== ready ===")
    print(f"report: {out if not args.dry else '(dry)'}")
    print(f"next decision: {next_d}")
    print(f"hours: {q}")

if __name__ == "__main__":
    main()
