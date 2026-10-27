#!/usr/bin/env bash
# FRIDAY workday start: session info + enriched brief + ready receipt. Writes reports/ + audit only.
set -uo pipefail
J="${JARVIS_HOME:-/home/box/jarvis}"; cd "$J" || exit 1; D=$(TZ=Asia/Kolkata date +%F)
DRY=0; [ "${1:-}" = "--dry" ] && DRY=1
scripts/session_start.sh; echo
if [ $DRY = 1 ]; then python3 skills/daily-brief-draft/scripts/assemble_brief.py >/dev/null && echo "brief: dry OK"
else python3 skills/daily-brief-draft/scripts/assemble_brief.py --write-report || { echo "enriched failed; offline brief"; skills/daily-brief-draft/scripts/brief.sh --write-report; }
  printf '{"time": "%s", "task": "workday-start", "action": "write_brief", "result": "reports/%s.md", "undo": "git checkout reports/%s.md"}\n' "$(TZ=Asia/Kolkata date -Iseconds)" "$D" "$D" >> logs/audit.jsonl; fi
echo "=== READY ==="; echo "report: reports/$D.md"
echo "next decision: $(awk '/^## Decisions owed/{f=1;next} /^## /{f=0} f&&NF{print;exit}' STATE.md)"
echo "quiet hours: $(scripts/in_quiet_hours.sh)"
