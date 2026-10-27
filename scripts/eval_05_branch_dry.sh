#!/usr/bin/env bash
# Eval 05: branch/PR concept dry-run, no network, no branch created.
J=/home/box/jarvis; cd "$J"; f=0
[ -x scripts/branch_name.sh ] || { echo "FAIL helper missing"; exit 1; }
[ "$(scripts/branch_name.sh feat 'Add Weekly Report!')" = jarvis/feat/add-weekly-report ] || f=1
scripts/branch_name.sh hack x >/dev/null 2>&1 && f=1
b=$(git branch --list | wc -l); scripts/branch_name.sh fix "dry run" >/dev/null; [ "$b" = "$(git branch --list | wc -l)" ] || f=1
echo "PR dry-run: would open PR from $(scripts/branch_name.sh fix 'dry run') → main (not executed; github autonomy L1)"
[ $f = 0 ] && echo "PASS eval05" || { echo "FAIL eval05"; exit 1; }
