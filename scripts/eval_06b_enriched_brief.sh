#!/usr/bin/env bash
# today's report must have Status, Calendar, Mail, Next headings (verified or UNAVAILABLE).
J=/home/box/jarvis; R="$J/reports/$(TZ=Asia/Kolkata date +%F).md"; f=0
[ -f "$R" ] || { echo "FAIL no report"; exit 1; }
for h in "^## Status" "^## Calendar \[(verified|UNAVAILABLE)" "^## Mail \[(verified|UNAVAILABLE)" "^## Next"; do grep -Eq "$h" "$R" && echo "PASS $h" || { echo "FAIL $h"; f=1; }; done
grep -q "nothing sent" "$R" && echo "PASS draft marker" || { echo "FAIL draft marker"; f=1; }
exit $f
