#!/usr/bin/env bash
# Usage: retry_guard.sh <cmd...>  — runs up to 3 times; after 3 failures STOP (exit 4) and log to audit.
J=/home/box/jarvis
for i in 1 2 3; do "$@" && exit 0; echo "attempt $i failed" >&2; done
[ "${JARVIS_NO_AUDIT:-0}" = 1 ] || printf '{"time": "%s", "task": "retry_guard", "action": "stop_after_3_failures", "result": "%s", "undo": "n/a"}\n' "$(date -Iseconds)" "$(echo "$1"|tr -d '"\\')" >> "$J/logs/audit.jsonl"
echo "STOP: failed 3 times — escalate to user, do not retry"; exit 4
