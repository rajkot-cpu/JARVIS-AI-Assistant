#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_jarvis import jarvis_home, section, quiet_hours_active, load_policy, now_ist

def main():
    J = jarvis_home()
    state = (J / "STATE.md").read_text(encoding="utf-8")
    policy = load_policy()
    print("JARVIS tools here: files + Python. Bash skills need Git Bash/WSL. Live calendar/mail: Grok Bot chat.")
    print(f"Time: {now_ist().strftime('%Y-%m-%d %H:%M %Z')} | quiet_hours: {'YES' if quiet_hours_active(policy) else 'no'}")
    print(f"Root: {J}")
    print(f"POLICY: {'approved' if 'status: approved' in policy else 'unknown'}")
    print("\n## Status")
    print(section(state, "Status") or "(empty)")
    print("\n## Next steps")
    print(section(state, "Next steps") or "(empty)")
    print("\n## Last audit")
    audit = J / "logs" / "audit.jsonl"
    if audit.exists():
        for ln in audit.read_text(encoding="utf-8").strip().splitlines()[-5:]:
            print(ln)
    else:
        print("(no audit)")

if __name__ == "__main__":
    main()
