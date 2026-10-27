#!/usr/bin/env bash
# KAREN health audit (read-only except its report). Writes reports/YYYY-MM-DD-karen.md
J=/home/box/jarvis; cd "$J"; R="reports/$(date +%F)-karen.md"; rc=0; out=()
chk(){ out+=("| $1 | $2 | $3 |"); [ "$2" = FAIL ] && rc=1; }
free=$(df -Pm /home/box | awk 'NR==2{print $4}'); [ "$free" -gt 1024 ] && chk disk_free OK "${free} MB" || chk disk_free FAIL "${free} MB (<1GB)"
d=$(git status --porcelain | wc -l); chk git_status $([ $d = 0 ] && echo OK || echo WARN) "$(git branch --show-current)@$(git rev-parse --short HEAD), dirty=$d"
if ls backups/*.tar.gz >/dev/null 2>&1; then b=$(ls -t backups/*.tar.gz | head -1); age=$(( ($(date +%s)-$(stat -c %Y "$b"))/3600 ))
  chk backup_age $([ $age -le 168 ] && echo OK || echo WARN) "$(basename "$b"), ${age}h old"; else chk backup_age WARN "no backups/"; fi
for s in day1 day2 day4; do [ -x scripts/${s}_exit_tests.sh ] && chk ${s}_exec OK executable || chk ${s}_exec FAIL "not executable"; done
st=$(awk '/^status:/{print $2;exit}' POLICY.yaml); chk policy_status $([ "$st" = approved ] && echo OK || echo FAIL) "$st"
{ echo "# KAREN health audit — $(date '+%F %H:%M %Z')"; echo "| Check | Result | Detail |"; echo "|---|---|---|"; printf '%s\n' "${out[@]}"; } > "$R"
cat "$R"; exit $rc
