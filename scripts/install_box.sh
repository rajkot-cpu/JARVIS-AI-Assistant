#!/usr/bin/env bash
# Idempotent install/health check of STARK OS on this Grok Bot box.
set -euo pipefail
J=/home/box/jarvis; cd "$J" || exit 1
R="reports/install-$(date +%F).md"; ok=0
{
  echo "# Install on box — $(date '+%F %H:%M %Z')"
  echo '```'
  for d in memory memory/projects skills roles logs reports evals scripts host fixtures backups .githooks; do mkdir -p "$d"; done
  for f in CLAUDE.md JARVIS.md SPEC.md STATE.md POLICY.yaml README.md logs/audit.jsonl scripts/session_start.sh scripts/kill_switch.md; do
    [ -f "$f" ] && echo "ok   $f" || { echo "MISSING $f"; ok=1; }
  done
  find scripts skills -name '*.sh' -exec chmod +x {} + 2>/dev/null || true
  [ -f .githooks/pre-commit ] && chmod +x .githooks/pre-commit
  # ensure hooks path for this repo only
  git config core.hooksPath .githooks
  echo "hooksPath: $(git config core.hooksPath)"
  echo "git: $(git branch --show-current) @ $(git rev-parse --short HEAD), dirty files: $(git status --porcelain | wc -l)"
  bash scripts/precommit_smoke.sh >/dev/null 2>&1 && echo "precommit_smoke: PASS" || { echo "precommit_smoke: FAIL"; ok=1; }
  bash scripts/day1_exit_tests.sh >/dev/null 2>&1 && echo "day1: PASS" || { echo "day1: FAIL"; ok=1; }
  bash scripts/day2_exit_tests.sh >/dev/null 2>&1 && echo "day2: PASS" || { echo "day2: FAIL"; ok=1; }
  if [ -f scripts/day4_exit_tests.sh ]; then
    bash scripts/day4_exit_tests.sh >/dev/null 2>&1 && echo "day4: PASS" || { echo "day4: FAIL"; ok=1; }
  fi
  bash scripts/edith_scan.sh >/dev/null 2>&1 && echo "edith: PASS" || { echo "edith: FAIL"; ok=1; }
  bash scripts/karen_smoke.sh >/dev/null 2>&1 && echo "karen: PASS" || { echo "karen: FAIL"; ok=1; }
  echo "INSTALL: $([ $ok = 0 ] && echo OK || echo PROBLEMS)"
  echo '```'
} | tee "$R"
exit $ok
