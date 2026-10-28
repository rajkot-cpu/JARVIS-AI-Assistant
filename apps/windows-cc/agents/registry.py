# apps/windows-cc/agents/registry.py
ROLES = [
    {
        "id": "coding",
        "name": "Coding",
        "tools": ["read_file", "search", "propose_diff"],
        "prompt": "You are Coding agent. Stay inside JARVIS_ROOT allowlisted paths. Propose diffs; never apply without R3.",
    },
    {
        "id": "research",
        "name": "Research",
        "tools": ["web_fetch"],
        "prompt": "You are Research agent. Summarize allowlisted fetches.",
    },
    {
        "id": "memory",
        "name": "Memory",
        "tools": ["memory_read", "memory_write"],
        "prompt": "You are Memory agent. Read/write JARVIS notes per POLICY.",
    },
    {
        "id": "browser",
        "name": "Browser",
        "tools": ["browser_allowlist"],
        "prompt": "You are Browser agent. Use Day 4–5 allowlist only.",
    },
    {
        "id": "task",
        "name": "Task",
        "tools": ["task_list", "task_create"],
        "prompt": "You are Task agent. Manage checklists/tasks.",
    },
    {
        "id": "system",
        "name": "System",
        "tools": ["metrics", "status", "dry_run"],
        "prompt": "You are System agent. Host health + dry-run only by default.",
    },
]
