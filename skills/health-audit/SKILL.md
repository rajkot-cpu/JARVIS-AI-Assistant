# Skill: health-audit (KAREN)
When: session start, before merges, or on request "health check".
Run: `scripts/karen_smoke.sh` (read-only; writes only its report). Then `scripts/precommit_smoke.sh` for test status.
Report FAIL rows to the user; do not auto-fix. WARN (dirty tree, old/no backup) → suggest `scripts/backup_workspace.sh` or commit.
