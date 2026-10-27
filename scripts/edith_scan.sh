#!/usr/bin/env bash
# EDITH: fail if private-key / AWS key patterns appear in skills/ scripts/ roles/ (fixtures/ excluded).
cd /home/box/jarvis
P='-----BEGIN ([A-Z]+ )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}|aws_secret_access_key\s*=\s*[A-Za-z0-9/+]{30,}'
H=$(grep -rEnI -e "$P" skills scripts roles host .githooks 2>/dev/null | grep -v '^scripts/edith_scan.sh:')
[ -z "$H" ] && { echo "EDITH: clean"; exit 0; }; echo "EDITH: SECRET PATTERN FOUND"; echo "$H" | cut -d: -f1,2; exit 1
