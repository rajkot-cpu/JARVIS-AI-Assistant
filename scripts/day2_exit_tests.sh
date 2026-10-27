#!/usr/bin/env bash
set -uo pipefail
J=/home/box/jarvis; cd "$J"; FS=skills/file-search/scripts/find_in_scope.sh; SM=skills/summarize-doc/scripts/summarize.sh
D=$(date +%F); R="reports/$D-day2-exit.md"; P=0; F=0; LOG=$(mktemp)
t(){ if eval "$2" >>"$LOG" 2>&1; then echo "PASS  $1"; P=$((P+1)); else echo "FAIL  $1"; F=$((F+1)); fi; }
FILES=(STATE.md POLICY.yaml CLAUDE.md README.md SPEC.md)
BEFORE=$(sha256sum "${FILES[@]}"); GIT_BEFORE=$(git status --porcelain -- . ':!reports')
{
echo "# Day 2–3 exit tests — $(date '+%F %H:%M %Z')"; echo '```'
for f in "${FILES[@]}"; do
  t "find $f" "$FS --name '$f' | grep -x '$J/$f'"
  t "summarize $f" "$SM '$J/$f' --lines 3 | grep -A20 '^== $f =='"
done
t "content search finds POLICY 'restricted:'" "$FS --content '^restricted:' | grep POLICY.yaml"
t "checksums unchanged (5 files)" "[ \"\$(sha256sum ${FILES[*]})\" = \"\$BEFORE\" ]"
t "refuse find in /home/box/.ssh" "$FS --root /home/box/.ssh; [ \$? -eq 2 ]"
t "refuse summarize /home/box/.ssh/config" "$SM /home/box/.ssh/config; [ \$? -eq 2 ]"
t "refuse out-of-scope /etc/hostname" "$SM /etc/hostname; [ \$? -eq 3 ]"
t "no workspace writes outside reports/" "[ \"\$(git status --porcelain -- . ':!reports')\" = \"\$GIT_BEFORE\" ]"
echo "RESULT: $P passed, $F failed"; echo '```'
echo; echo "## Summaries / tool output"; echo '```'; cat "$LOG"; echo '```'
} | tee "$R.tmp"
mv "$R.tmp" "$R"; rm -f "$LOG"; [ $F -eq 0 ]
