#!/usr/bin/env bash
# Usage: JARVIS_ALLOW_QUIT=1 quit_app.sh [--dry-run] <app>. Needs approval flag; allowlisted only.
. "$(dirname "$0")/../lib_apps.sh"
DRY=0; [ "${1:-}" = --dry-run ] && { DRY=1; shift; }
[ "${JARVIS_ALLOW_QUIT:-0}" = 1 ] || { echo "REFUSED: quitting needs approval (JARVIS_ALLOW_QUIT=1)"; exit 3; }
b=$(app_bin "${1:-}") || { echo "REFUSED: '${1:-}' is not allowlisted"; exit 2; }
for p in $(pgrep -x "$b"); do
  [ "$p" -le 1 ] && continue; [ "$(ps -o comm= -p "$p")" = sshd ] && continue
  if [ $DRY = 1 ]; then echo "DRY-RUN: would SIGTERM $p ($b)"; else kill -TERM "$p" && echo "stopped $p"; fi
done; echo "done: $1"
