#!/usr/bin/env bash
# Idempotent install/health check of STARK OS on this Grok Bot box.
J=/home/box/jarvis; cd "$J" || exit 1; R="reports/install-$(date +%F).md"; ok=0
{ echo "# Install on box — $(date '+%F %H:%M %Z')"; echo '```'
for d in memory memory/projects skills roles logs reports evals scripts host fixtures; do mkdir -p "$d"; done
for f in CLAUDE.md JARVIS.md SPEC.md STATE.md POLICY.yaml README.md logs/audit.jsonl; do [ -f "$f" ] && echo "ok   $f" || { echo "MISSING $f"; ok=1; }; done
find scripts skills -name '*.sh' -exec chmod +x {} +; echo "chmod +x on scripts done"
echo "git: $(git branch --show-current) @ $(git rev-parse --short HEAD), dirty files: $(git status --porcelain | wc -l)"
bash scripts/day1_exit_tests.sh >/dev/null 2>&1 && echo "day1: PASS" || { echo "day1: FAIL"; ok=1; }
bash scripts/day2_exit_tests.sh >/dev/null 2>&1 && echo "day2: PASS" || { echo "day2: FAIL"; ok=1; }
echo "INSTALL: $([ $ok = 0 ] && echo OK || echo PROBLEMS)"; echo '```'; } | tee "$R"; exit $ok
