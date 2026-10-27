# STATE — read first, updated last
Last updated: 2026-10-28 ~02:23 (Asia/Calcutta)

## Goals
- Build STARK OS on the Grok Bot box, test it, then package an install for Dr Chandan kumar's computer.
- Day-1 MVP and Day 2–3 read-only skills are complete on this host.

## Status
- Day 1: complete (exit tests PASS). POLICY.yaml and host/permission-rules.md approved 2026-10-28 by Dr Chandan kumar.
- Day 2–3: complete (16/16 exit tests PASS). Merged `jarvis/feat/day2-readonly-skills` into `main` at `60112fa` (user OK t2s7).
- Draft-only Daily Brief routine saved: every day around 07:30 Asia/Calcutta → writes `reports/YYYY-MM-DD.md` and posts a short receipt in this chat; skips quietly if today's report already exists.
- Install on user computer: not started.
- Desktop `chandan` still disconnected; OnePlus connected; Docker unavailable.

## Next steps
1. Let morning brief run (or run `skills/daily-brief-draft/scripts/brief.sh --write-report` for a manual dry run).
2. Optionally fill intake (OS, daily apps, top three tasks) and real restricted-folder paths in POLICY.
3. Day 4–5 app control still deferred; package install for user computer after more box testing.

## Decisions owed
- Real paths for restricted folders (patient / banking / tax placeholders remain).
- Optional intake answers (skipped earlier).
- When to start packaging install for the user's computer / connect desktop `chandan`.

## Host capabilities
- Files + shell on box (Debian 13): verified
- Git + gh; GitHub connector: verified
- Browser + network: verified
- Live connectors: Gmail, Calendar, Notion, Docs/Slides, X, TubeAlfred, MagicPath, Clay, Wonder, Origin
- Needs auth: Composio, Read.ai, GitLab, Finance
- OnePlus 13: connected; desktop `chandan`: disconnected; Docker: unavailable
- OS backups on user machines: unknown
