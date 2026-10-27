#!/usr/bin/env bash
# Usage: branch_name.sh <feat|fix|chore> "<short description>"  -> jarvis/<type>/<slug>  (no network)
t=$1; shift; [[ "$t" =~ ^(feat|fix|chore)$ ]] || { echo "type must be feat|fix|chore" >&2; exit 2; }
s=$(echo "$*" | tr 'A-Z' 'a-z' | sed -E 's/[^a-z0-9]+/-/g;s/^-|-$//g' | cut -c1-40)
[ -n "$s" ] || { echo "empty description" >&2; exit 2; }; echo "jarvis/$t/$s"
