#!/usr/bin/env bash
# Read-only file search within POLICY scopes. Usage:
#   find_in_scope.sh [--root DIR] [--name GLOB] [--type f|d] [--newer-days N] [--content REGEX]
set -euo pipefail
. "$(dirname "$0")/../../lib_scope.sh"
ROOT=""; NAME="*"; TYPE="f"; DAYS=""; CONTENT=""
while [ $# -gt 0 ]; do case "$1" in
  --root) ROOT="$2"; shift 2;; --name) NAME="$2"; shift 2;; --type) TYPE="$2"; shift 2;;
  --newer-days) DAYS="$2"; shift 2;; --content) CONTENT="$2"; shift 2;;
  *) NAME="$1"; shift;; esac; done
roots=(); if [ -n "$ROOT" ]; then check_path "$ROOT" || exit $?; roots=("$(realpath -m "$ROOT")"); else mapfile -t roots < <(read_roots); fi
args=(-type "$TYPE" -name "$NAME" -not -path '*/.git/*')
[ -n "$DAYS" ] && args+=(-mtime "-$DAYS")
found=0
while IFS= read -r f; do
  check_path "$f" 2>/dev/null || continue
  if [ -n "$CONTENT" ]; then grep -Iqs -E -- "$CONTENT" "$f" || continue; fi
  echo "$f"; found=1
done < <(find "${roots[@]}" "${args[@]}" 2>/dev/null | sort)
[ $found -eq 1 ] || { echo "no matches" >&2; exit 1; }
