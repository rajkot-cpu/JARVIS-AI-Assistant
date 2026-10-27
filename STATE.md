# STATE — read first, updated last
Last updated: 2026-10-28 (Asia/Calcutta)

## Goals
- Build STARK OS Day-1 MVP on the Grok Bot box, test it, then package an install for Dr Chandan kumar's computer.

## Status
- Day 1: workspace, Kernel (CLAUDE.md/JARVIS.md), SPEC.md, STATE.md, draft POLICY.yaml, audit log, capability report, delete guard — COMPLETE (see reports/2026-10-28-day1-exit.md).
- Day 2–3 (read-only skills): PENDING.
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
1. User reviews/approves POLICY.yaml and host/permission-rules.md.
2. Day 2–3: build read-only skills (file find/summarize, daily brief draft) on box; run evals 01, 02, 08.
3. Package installer for user's computer after box tests pass.

## Decisions owed by user
- Intake answers: OS/version, daily apps, three tasks to automate first (skipped 2026-10-28).
- Restricted folder paths, quiet hours, daily brief time, apps allowlist, autonomy levels.
