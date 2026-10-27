#!/usr/bin/env bash
# Fast (<30s) smoke: EDITH scan, day1/day2/day4 tests, evals 03/05/07. Restores reports it rewrites.
J=/home/box/jarvis; cd "$J"; pre=$(git diff --name-only -- reports/); rc=0
for t in scripts/edith_scan.sh scripts/day1_exit_tests.sh scripts/day2_exit_tests.sh scripts/day4_exit_tests.sh \
         scripts/eval_03_injection.sh scripts/eval_05_branch_dry.sh scripts/eval_07_three_strikes.sh; do
  [ -f "$t" ] || continue; if bash "$t" >/dev/null 2>&1; then echo "PASS $t"; else echo "FAIL $t"; rc=1; fi; done
for f in $(git diff --name-only -- reports/); do echo "$pre" | grep -qx "$f" || git checkout -q -- "$f"; done
exit $rc
