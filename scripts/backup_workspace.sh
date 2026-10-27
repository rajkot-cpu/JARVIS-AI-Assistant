#!/usr/bin/env bash
# Backup /home/box/jarvis to backups/ (excluded from git). Restore test extracts STATE.md.
set -euo pipefail
J="${JARVIS_HOME:-/home/box/jarvis}"
mkdir -p "$J/backups"
TS=$(date +%Y%m%d-%H%M%S)
OUT="$J/backups/jarvis-backup-$TS.tar.gz"
tar -czf "$OUT" --exclude='backups' -C "$(dirname "$J")" "$(basename "$J")"
sha256sum "$OUT" | tee "$J/backups/jarvis-backup-$TS.sha256"
tmpdir=$(mktemp -d)
tar -xzf "$OUT" -C "$tmpdir" "$(basename "$J")/STATE.md"
test -s "$tmpdir/$(basename "$J")/STATE.md"
rm -rf "$tmpdir"
echo "BACKUP_OK $OUT"
