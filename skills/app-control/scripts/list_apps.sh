#!/usr/bin/env bash
# List running processes for allowlisted apps only.
. "$(dirname "$0")/../lib_apps.sh"
for a in "${!APP_BIN[@]}"; do b=${APP_BIN[$a]}
  pids=$(pgrep -x "$b" -d, 2>/dev/null || pgrep -f "/$b( |$)" -d, 2>/dev/null)
  echo "$a ($b): ${pids:-not running}"; done
