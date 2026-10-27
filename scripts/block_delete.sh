#!/usr/bin/env bash
# Deletion wrapper: refuses unless JARVIS_ALLOW_DELETE=1 AND path is under fixtures/.
set -u
DIR="$(cd "$(dirname "$0")" && pwd -P)"
[ $# -eq 1 ] || { echo "BLOCKED: exactly one path required"; exit 2; }
if [ "${JARVIS_ALLOW_DELETE:-0}" != "1" ]; then echo "BLOCKED: JARVIS_ALLOW_DELETE not set (approval missing) for $1"; exit 1; fi
"$DIR/policy_check.sh" delete "$1" >/dev/null || { echo "BLOCKED: $1 is outside fixtures/"; exit 1; }
[ -f "$1" ] || { echo "BLOCKED: not a regular file: $1"; exit 1; }
rm -- "$1" && echo "DELETED: $1"
