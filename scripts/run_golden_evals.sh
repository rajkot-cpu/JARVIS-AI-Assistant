#!/usr/bin/env bash
J=/home/box/jarvis; cd "$J"; R="reports/$(date +%F)-evals.md"; ALL=0
{ echo "# Golden evals — $(date '+%F %H:%M %Z')"; echo "| Suite | Result |"; echo "|---|---|"; } > "$R"
for s in day1 day2 day4; do if bash scripts/${s}_exit_tests.sh >/dev/null 2>&1; then r=PASS; else r=FAIL; ALL=1; fi
  echo "| ${s}_exit_tests | $r |" >> "$R"; echo "$s: $r"; done
echo "Evals mapped: 01,02 → day2; 04,08 → day1; app allowlist → day4" >> "$R"; exit $ALL
