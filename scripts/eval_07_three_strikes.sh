#!/usr/bin/env bash
# Eval 07: a command that always fails is stopped after exactly 3 attempts (exit 4).
cd /home/box/jarvis; T=$(mktemp)
JARVIS_NO_AUDIT=1 scripts/retry_guard.sh bash -c "echo x >> $T; false" >/dev/null 2>&1; rc=$?; n=$(wc -l < "$T"); rm -f "$T"
JARVIS_NO_AUDIT=1 scripts/retry_guard.sh true >/dev/null || { echo "FAIL success path"; exit 1; }
[ $rc = 4 ] && [ "$n" = 3 ] && echo "PASS eval07 (stopped after $n attempts)" || { echo "FAIL eval07 rc=$rc n=$n"; exit 1; }
