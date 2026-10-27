# Skill: app-control (Day 4–5, adapted to Grok Bot box)
"Apps" = allowlisted local GUI binaries on this Debian box (POLICY.yaml apps_allowlist):
chrome → google-chrome, terminal → xfce4-terminal. Map lives in lib_apps.sh.
- List: `scripts/list_apps.sh` (allowlisted processes only).
- Launch: `scripts/launch_app.sh <app>` or `--set work` (chrome + terminal). `--dry-run` previews. Anything else (rm, sudo, bash -c, args) is REFUSED, exit 2.
- Quit: requires user approval → `JARVIS_ALLOW_QUIT=1 scripts/quit_app.sh <app>`; never PID 1 or sshd. Without the flag: exit 3.
Browser automation itself goes through Grok Bot's browser subagent, not these scripts.
