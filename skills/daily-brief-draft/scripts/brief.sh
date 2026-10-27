#!/usr/bin/env bash
# DRAFT daily brief from STATE.md + logs/audit.jsonl. Read-only unless --write-report.
set -euo pipefail
J="${JARVIS_HOME:-/home/box/jarvis}"; D=$(date +%F)
out() {
  echo "# Daily brief (DRAFT) — $D (Asia/Calcutta)"; echo
  echo "## Status (from STATE.md)"; awk '/^## Status/{f=1;next} /^## /{f=0} f' "$J/STATE.md"; echo
  echo "## Next steps"; awk '/^## Next steps/{f=1;next} /^## /{f=0} f' "$J/STATE.md"; echo
  echo "## Decisions owed"; awk '/^## Decisions owed/{f=1;next} /^## /{f=0} f' "$J/STATE.md"; echo
  echo "## Audit today"; { grep "\"$D" "$J/logs/audit.jsonl" || true; } | python3 -c 'import sys,json
for l in sys.stdin:
  try:
    e=json.loads(l); print("- %s %s: %s -> %s" % (e["time"][11:16], e["task"], e["action"], e["result"]))
  except Exception: pass'
  echo; echo "_Draft only — nothing sent._"
}
if [ "${1:-}" = "--write-report" ]; then out > "$J/reports/$D.md"; echo "wrote reports/$D.md"; else out; fi
