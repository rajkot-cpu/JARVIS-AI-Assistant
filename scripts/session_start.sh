#!/usr/bin/env bash
# Read-only session start: tools one-liner, STATE status/next, last 5 audit lines.
J=/home/box/jarvis; cd "$J" || exit 1
echo "Tools: files+shell (box), git/gh, browser, connectors; no user desktop, no Docker."
echo; sed -n '/^## Status/,/^## Decisions/p' STATE.md | sed '$d'
echo "## Last 5 audit entries"; tail -n 5 logs/audit.jsonl
echo; echo "git: $(git branch --show-current) @ $(git rev-parse --short HEAD); dirty: $(git status --porcelain | wc -l)"
