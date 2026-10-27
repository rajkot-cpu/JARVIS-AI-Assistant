#!/usr/bin/env bash
# Eval 06: a daily brief report exists for today or yesterday (Asia/Calcutta) and is non-empty.
cd /home/box/jarvis
for d in "$(date +%F)" "$(date -d yesterday +%F)"; do [ -s "reports/$d.md" ] && { echo "brief found: reports/$d.md"; echo "PASS eval06"; exit 0; }; done
echo "FAIL eval06: no brief for today/yesterday"; exit 1
