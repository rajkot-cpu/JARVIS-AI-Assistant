#!/usr/bin/env bash
# Read-only summary of a text/md/pdf file within scope. Usage: summarize.sh FILE [--lines N]
set -eu
. "$(dirname "$0")/../../lib_scope.sh"
F="${1:?usage: summarize.sh FILE [--lines N]}"; N=5; [ "${2:-}" = "--lines" ] && N="${3:-5}"
check_path "$F" || exit $?
[ -f "$F" ] || { echo "REFUSED: not a regular file" >&2; exit 4; }
case "$F" in
  *.pdf) command -v pdftotext >/dev/null || { echo "pdftotext unavailable" >&2; exit 5; }
         TEXT=$(pdftotext -q "$F" - 2>/dev/null);;
  *) grep -Iq . "$F" || [ ! -s "$F" ] || { echo "REFUSED: binary file" >&2; exit 4; }; TEXT=$(cat -- "$F");;
esac
echo "== $(basename "$F") =="
echo "path: $(realpath "$F")"
echo "stats: $(printf '%s\n' "$TEXT" | wc -l) lines, $(printf '%s' "$TEXT" | wc -w) words"
HEAD=$(printf '%s\n' "$TEXT" | grep -E '^#{1,3} ' | head -6 | sed 's/^#* *//' | paste -sd ';' - || true)
[ -n "$HEAD" ] && echo "headings: $HEAD"
echo "excerpt:"; printf '%s\n' "$TEXT" | grep -v '^\s*$' | head -"$N" | cut -c1-160 | sed 's/^/  /'
