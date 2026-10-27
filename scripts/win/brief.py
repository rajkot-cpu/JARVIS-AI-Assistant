#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_jarvis import jarvis_home, section, now_ist, append_audit

def build() -> str:
    J = jarvis_home()
    D = now_ist().strftime("%Y-%m-%d")
    state = (J / "STATE.md").read_text(encoding="utf-8")
    lines = [
        f"# Daily brief (DRAFT) — {D} (Asia/Calcutta)", "",
        "## Status [verified: STATE.md]", section(state, "Status") or "(empty)", "",
        "## Next steps [verified: STATE.md]", section(state, "Next steps") or "(empty)", "",
        "## Decisions owed [verified: STATE.md]", section(state, "Decisions owed") or "(empty)", "",
        "## Calendar [unavailable on Windows local — refresh via Grok Bot JARVIS]",
        "_Use the Grok Bot session for live calendar._", "",
        "## Mail [unavailable on Windows local — refresh via Grok Bot JARVIS]",
        "_Use the Grok Bot session for live mail._", "",
        "## Audit today [verified: logs/audit.jsonl]",
    ]
    audit = J / "logs" / "audit.jsonl"
    if audit.exists():
        for ln in audit.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(ln)
                if D in e.get("time", ""):
                    lines.append(f"- {e.get('time','')[11:19]} {e.get('task')}: {e.get('action')} -> {e.get('result')}")
            except Exception:
                pass
    lines += ["", "## Recommended next step",
              "Continue day-to-day via Grok Bot JARVIS chat; keep this folder as the local mirror.",
              "", "_Draft only — nothing sent._"]
    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    text = build()
    if args.write:
        J = jarvis_home()
        D = now_ist().strftime("%Y-%m-%d")
        out = J / "reports" / f"{D}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        append_audit("daily-brief", "win_brief_write", str(out), f"delete {out}")
        print(f"wrote {out}")
    else:
        print(text)

if __name__ == "__main__":
    main()
