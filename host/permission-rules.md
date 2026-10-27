# Host permission rules — DRAFT (pending_user_approval)

## This host: Grok Bot box (Debian 13)
- Workspace: /home/box/jarvis (~/jarvis). Reads/writes only here unless POLICY.yaml grants more.
- Deletion: only via scripts/block_delete.sh (fixtures/ + JARVIS_ALLOW_DELETE=1). All other deletes = R3 approval card.
- No sudo, no package installs without approval (R3).
- Never read ~/.ssh, ~/.gnupg, browser profiles/credential stores, or restricted paths in POLICY.yaml.
- No git push / remote changes without approval (R3); no merge to main (R4).
- Sending email/messages: drafts only; send = R3.
- Note: on this host the deterministic gate is the platform's Auto-review + these scripts; prompts are not a boundary.

## Portable sketch for the user's computer (Claude Code `.claude/settings.json`)
```json
{
  "permissions": {
    "allow": ["Read(~/jarvis/**)", "Edit(~/jarvis/**)", "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
              "Bash(git checkout -b jarvis/*)", "Bash(./scripts/*.sh:*)"],
    "ask":   ["Bash(git push:*)", "Bash(git merge:*)", "Bash(npm install:*)", "Bash(pip install:*)", "WebFetch"],
    "deny":  ["Bash(rm:*)", "Bash(sudo:*)", "Bash(shred:*)", "Bash(dd:*)", "Bash(mkfs:*)", "Bash(git reset --hard:*)",
              "Bash(git push --force:*)", "Bash(chmod -R:*)", "Bash(curl * | sh)",
              "Read(~/.ssh/**)", "Read(~/.gnupg/**)", "Read(~/.aws/**)", "Read(**/.env)",
              "Read(~/patients/**)", "Read(~/finance/**)",
              "Edit(~/jarvis/POLICY.yaml)", "Edit(~/jarvis/CLAUDE.md)", "Edit(~/jarvis/logs/**)", "Edit(~/jarvis/.claude/**)"]
  }
}
```
Verify current Claude Code permission syntax against its docs before installing (Kernel: check current documentation).
