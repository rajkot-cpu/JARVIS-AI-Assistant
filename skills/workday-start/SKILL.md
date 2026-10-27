# workday-start (FRIDAY)
Run `scripts/workday_start.sh` (or `--dry`). Before it, refresh agenda cache per scripts/refresh_agenda_cache.md.
Does: session_start → enriched brief (reports/YYYY-MM-DD.md) → ready receipt (report path, next decision, quiet hours).
Writes only reports/ + one audit line. Sends nothing; missing connectors = UNAVAILABLE sections.
