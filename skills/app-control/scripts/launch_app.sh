#!/usr/bin/env bash
# Usage: launch_app.sh [--dry-run] <app|--set work>. Only allowlisted apps.
. "$(dirname "$0")/../lib_apps.sh"
DRY=0; [ "${1:-}" = --dry-run ] && { DRY=1; shift; }
if [ "${1:-}" = --set ]; then names=${WORKSETS[${2:-}]:-}; [ -z "$names" ] && { echo "REFUSED: unknown work set '${2:-}'"; exit 2; }
else [ $# -eq 1 ] || { echo "REFUSED: exactly one app name, no arguments"; exit 2; }; names=$1; fi
rc=0
for a in $names; do b=$(app_bin "$a") || { echo "REFUSED: '$a' is not allowlisted (allowed: ${!APP_BIN[*]})"; rc=2; continue; }
  if [ $DRY = 1 ]; then echo "DRY-RUN: would start $b"; else nohup "$b" >/dev/null 2>&1 & echo "started $a ($b) pid $!"; fi
done; exit $rc
