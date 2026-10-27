# STATE — read first, updated last
Last updated: 2026-10-28 (Asia/Calcutta)

## Goals
- Build STARK OS Day-1 MVP on the Grok Bot box, test it, then package an install for Dr Chandan kumar's computer.

## Status
- Day 1: workspace, Kernel (CLAUDE.md/JARVIS.md), SPEC.md, STATE.md, draft POLICY.yaml, audit log, capability report, delete guard — COMPLETE (see reports/2026-10-28-day1-exit.md).
- POLICY.yaml + host/permission-rules.md: APPROVED 2026-10-28 by Dr Chandan kumar (t2s3).
- Day 2–3 (read-only skills: file-search, summarize-doc, daily-brief-draft): COMPLETE on branch jarvis/feat/day2-readonly-skills (reports/2026-10-28-day2-exit.md). Merge to main awaits user sign-off.
- Install on user's computer: DEFERRED until box testing done.

## Host capabilities (2026-10-28)
- Files + shell on box (Debian 13): verified
- Git + gh: verified; GitHub connector: verified
- Browser + network: verified
- Live connectors: Gmail, Calendar, Notion, Docs/Slides, X, TubeAlfred, MagicPath, Clay, Wonder, Origin — verified
- Needs auth: Composio, Read.ai, GitLab, Finance — unavailable
- OnePlus 13: connected; desktop `chandan`: disconnected; Docker: unavailable
- OS backups on user machines: unknown (not probed)

## Next steps
1. User sign-off to merge jarvis/feat/day2-readonly-skills into main.
2. On box: daily-brief scheduler (07:30 Asia/Calcutta, draft-only) once Day 2–3 is merged.
3. Day 4–5 app control later; package installer for user's computer after box tests pass (deferred).

## Decisions owed by user
- Optional intake: OS/version, daily apps, three tasks to automate first.
- Real restricted folder paths (placeholders remain), quiet hours.
- Install on user's computer: deferred.
