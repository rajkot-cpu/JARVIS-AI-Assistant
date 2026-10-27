#!/usr/bin/env bash
J=/home/box/jarvis; cd "$J"; f=0
c(){ if eval "$2" >/dev/null 2>&1; then echo "PASS $1"; else echo "FAIL $1"; f=1; fi; }
c "POLICY approved" "grep -q '^status: approved' POLICY.yaml"
c "offline brief" "skills/daily-brief-draft/scripts/brief.sh"
c "enriched brief (no cache)" "JARVIS_CACHE_TEST=1 python3 skills/daily-brief-draft/scripts/assemble_brief.py"
c "workday_start --dry" "scripts/workday_start.sh --dry"
c "karen_smoke" "scripts/karen_smoke.sh"
c "precommit_smoke" "scripts/precommit_smoke.sh"
c "routine prompt" "test -s scripts/routine-prompts/daily-brief-0730.md"
c "cache gitignored" "git check-ignore -q reports/_cache/x.json"
[ -f reports/_cache/calendar.json ] && echo "INFO agenda cache present" || echo "INFO agenda cache absent (optional)"
exit $f
