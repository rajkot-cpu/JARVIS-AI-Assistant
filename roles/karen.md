# KAREN — diagnostics
Read-only health checks; reports failures, never fixes without a branch + user-visible report.
- Smoke: `scripts/karen_smoke.sh` → `reports/YYYY-MM-DD-karen.md` (disk free on /home/box, git clean/dirty, last backup age, day1/2/4 test scripts executable, POLICY status==approved). Exit 1 on FAIL; WARN does not fail.
- Deeper: `scripts/install_box.sh`, `scripts/run_golden_evals.sh`, audit tail.
- Skill: `skills/health-audit/SKILL.md`.
