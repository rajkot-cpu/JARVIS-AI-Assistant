# STARK OS — JARVIS workspace (Grok Bot box)
Installed on the Grok Bot box at /home/box/jarvis. **Not yet installed on the user's computer** (deferred until packaging).

## Start a session
`scripts/session_start.sh` (read-only: tools, STATE status/next, last 5 audit lines). Health/install: `scripts/install_box.sh`. All tests: `scripts/run_golden_evals.sh`.

## Risk rules
- POLICY.yaml is law; only the user edits it. Reads/writes limited to this workspace; restricted paths refused.
- Delete only in fixtures/ with JARVIS_ALLOW_DELETE=1. Quit apps only with JARVIS_ALLOW_QUIT=1 after user OK.
- Launch only allowlisted apps (chrome, terminal). No pushes, emails, or posts without explicit approval.
- Every consequential step → logs/audit.jsonl. Stop: scripts/kill_switch.md.

## Verified vs not
Verified on box: day1 (13), day2 (16), day4 (13) exit tests; install check; daily brief routine `jarvis-daily-brief-07-30` (draft-only, 07:30 IST).
Not verified: real GUI launch on a visible desktop, user-machine install, real restricted paths (placeholders), intake answers.

## Layout
skills/ (file-search, summarize-doc, daily-brief-draft, app-control) · roles/ (edith, friday, karen stub) · evals/ · reports/ · memory/ · host/ · scripts/

## Polish pass (2026-10-28)
- Quiet hours 22:00–07:00 Asia/Calcutta (POLICY `schedule.quiet_hours`); check with `scripts/in_quiet_hours.sh` (exit 0 = quiet). 07:30 brief unchanged.
- Pre-commit hook `.githooks/pre-commit` → `scripts/precommit_smoke.sh` (EDITH scan, day1/2/4, evals 03/05/07; ~2s). Enable: `git config core.hooksPath .githooks`.
- Evals 03/05/06/07 runnable (`scripts/eval_0*.sh`), included in `run_golden_evals.sh`.
- KAREN: `scripts/karen_smoke.sh`; EDITH: `scripts/edith_scan.sh`; helpers `branch_name.sh`, `retry_guard.sh`.
