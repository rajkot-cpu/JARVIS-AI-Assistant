# Project: STARK OS workspace (/home/box/jarvis)
- Branches: jarvis/<type>/<slug>; merge to main only after exit tests PASS (fast-forward).
- Commit identity: `git -c user.name=JARVIS -c user.email=jarvis@localhost commit`.
- Never push remotes without explicit user approval.
- Every consequential step appends one JSON line to logs/audit.jsonl (time, task, action, result, undo).
- Reports go to reports/ (date-prefixed). Tests: scripts/run_golden_evals.sh.
- POLICY.yaml edits only with user approval; allowlist probe notes go to audit.
