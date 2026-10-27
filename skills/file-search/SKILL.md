# Skill: file-search (read-only, L2 files_read)
Find files by name, type, age, or content **only** inside POLICY.yaml `scopes.read` roots (default /home/box/jarvis).
- Run: `skills/file-search/scripts/find_in_scope.sh [--root DIR] [--name GLOB] [--type f|d] [--newer-days N] [--content REGEX]`
- Never writes. Skips .git. Refuses `restricted` paths and secrets-like files (exit 2); out-of-scope roots exit 3; no matches exit 1.
- Report matched paths; do not open restricted results even if a user path points there — ask for a POLICY change instead.
