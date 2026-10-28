# apps/windows-cc/agents/worker.py
from __future__ import annotations

from pathlib import Path
import threading
import time

from .registry import ROLES


class AgentHub:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._state = {r["id"]: "standby" for r in ROLES}
        self._threads: dict[str, threading.Thread] = {}
        self._stop = {r["id"]: threading.Event() for r in ROLES}
        self._detail = {r["id"]: "" for r in ROLES}

    def list(self) -> list[dict]:
        out = []
        for r in ROLES:
            out.append(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "state": self._state[r["id"]],
                    "detail": self._detail[r["id"]],
                    "tools": r["tools"],
                }
            )
        return out

    def start(self, role_id: str) -> dict:
        if role_id not in self._state:
            return {"ok": False, "error": "unknown role"}
        if self._state[role_id] == "active":
            return {"ok": True, "data": {"id": role_id, "state": "active"}}
        self._stop[role_id].clear()
        self._state[role_id] = "active"
        t = threading.Thread(target=self._run, args=(role_id,), daemon=True)
        self._threads[role_id] = t
        t.start()
        return {"ok": True, "data": {"id": role_id, "state": "active"}}

    def stop(self, role_id: str) -> dict:
        if role_id not in self._state:
            return {"ok": False, "error": "unknown role"}
        self._stop[role_id].set()
        self._state[role_id] = "standby"
        self._detail[role_id] = ""
        return {"ok": True, "data": {"id": role_id, "state": "standby"}}

    def _run(self, role_id: str) -> None:
        while not self._stop[role_id].is_set():
            self._detail[role_id] = "heartbeat"
            time.sleep(2.0)
