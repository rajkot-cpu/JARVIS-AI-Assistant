#!/usr/bin/env bash
set -uo pipefail
J=/home/box/jarvis; cd "$J"; S=skills/app-control/scripts; R="reports/$(date +%F)-day4-exit.md"; P=0; F=0
t(){ if eval "$2" >/dev/null 2>&1; then echo "PASS  $1"; P=$((P+1)); else echo "FAIL  $1"; F=$((F+1)); fi; }
{ echo "# Day 4–5 exit tests — $(date '+%F %H:%M %Z')"; echo '```'
t "work set dry-run lists only allowlisted" "$S/launch_app.sh --dry-run --set work | grep -q google-chrome"
for x in rm sudo "bash -c id" firefox /bin/sh "chrome --x"; do t "refuse launch '$x'" "$S/launch_app.sh --dry-run $x; [ \$? -eq 2 ]"; done
t "refuse unknown work set" "$S/launch_app.sh --dry-run --set evil; [ \$? -eq 2 ]"
t "list works" "$S/list_apps.sh | grep -q '^chrome'"
t "quit without flag refused" "env -u JARVIS_ALLOW_QUIT $S/quit_app.sh chrome; [ \$? -eq 3 ]"
t "quit with flag refuses non-allowlisted" "JARVIS_ALLOW_QUIT=1 $S/quit_app.sh sshd; [ \$? -eq 2 ]"
t "quit with flag allowlisted dry-run ok" "JARVIS_ALLOW_QUIT=1 $S/quit_app.sh --dry-run terminal"
t "POLICY allowlist matches lib" "grep -q 'apps_allowlist: \[chrome, terminal\]' POLICY.yaml"
echo "RESULT: $P passed, $F failed"; echo '```'; } | tee "$R"; [ $F -eq 0 ]
