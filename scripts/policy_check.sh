#!/usr/bin/env bash
# Usage: policy_check.sh <op> <path>   op: read|write|delete
# Exit 0 = allowed, 1 = refused. Deterministic gate; no model involved.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
op="${1:-}"; p="${2:-}"
[ -z "$op" ] || [ -z "$p" ] && { echo "REFUSED: usage"; exit 1; }
abs="$(realpath -m -- "$p")"
for r in "$HOME/.ssh" "$HOME/.gnupg" "$HOME/patients" "$HOME/finance"; do
  case "$abs/" in "$r"/*) echo "REFUSED: restricted path $abs"; exit 1;; esac
done
case "$op" in
  read|write) case "$abs/" in "$ROOT"/*) echo "ALLOWED: $op $abs"; exit 0;; esac ;;
  delete) case "$abs" in "$ROOT"/fixtures/*) echo "ALLOWED: delete $abs"; exit 0;; esac ;;
esac
echo "REFUSED: $op outside allowed scope: $abs"; exit 1
