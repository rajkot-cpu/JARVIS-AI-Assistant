#!/usr/bin/env bash
# Shared scope helpers: read scopes.read and restricted from POLICY.yaml (read-only).
JARVIS_HOME="${JARVIS_HOME:-/home/box/jarvis}"
POLICY="$JARVIS_HOME/POLICY.yaml"
read_roots() {
  local line; line=$(grep -E '^[ \t]*read:[ \t]*\[' "$POLICY" 2>/dev/null | head -1)
  if [ -n "$line" ]; then echo "$line" | sed 's/#.*//; s/.*\[//; s/\].*//' | tr ',' '\n' | sed 's/^ *//; s/ *$//' | grep -v '^$'
  else echo "$JARVIS_HOME"; fi
}
restricted_list() {
  awk '/^restricted:/{f=1;next} f&&/^[a-z]/{f=0} f&&/^[ \t]*-/{sub(/^[ \t]*-[ \t]*/,"");sub(/[ \t]*#.*/,"");print}' "$POLICY" | sed "s|^~|$HOME|" | grep -v PLACEHOLDER
  echo "$HOME/.ssh"; echo "$HOME/.gnupg"
}
# returns 0 if path allowed; 2 restricted; 3 out of scope
check_path() {
  local p; p=$(realpath -m -- "$1")
  local r; while read -r r; do [ -z "$r" ] && continue; r=$(realpath -m -- "$r")
    case "$p/" in "$r"/*) echo "REFUSED: restricted path ($p)" >&2; return 2;; esac; done < <(restricted_list)
  case "$p" in *.env|*/.env|*id_rsa*|*id_ed25519*|*.pem|*.key|*secret*|*credential*) echo "REFUSED: secrets-like path ($p)" >&2; return 2;; esac
  while read -r r; do r=$(realpath -m -- "$r"); case "$p/" in "$r"/*) return 0;; esac; done < <(read_roots)
  echo "REFUSED: outside POLICY read scope ($p)" >&2; return 3
}
