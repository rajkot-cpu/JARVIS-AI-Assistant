# apps/windows-cc/bridge_api.py
from __future__ import annotations

from pathlib import Path
import sys

_PANEL = Path(__file__).resolve().parents[1] / "windows-panel"
_WIN = Path(__file__).resolve().parents[2] / "scripts" / "win"
for p in (_PANEL, _WIN, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import panel_api  # noqa: E402


def _system_status(status: dict) -> str:
    if not status.get("policy_ok"):
        return "POLICY NOT APPROVED"
    if status.get("quiet_hours"):
        return "QUIET HOURS"
    return "SYSTEMS NOMINAL"


class BridgeApi:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.panel = panel_api.Panel(self.root)
        self._hub = None

    def status(self) -> dict:
        try:
            s = self.panel.status_strip()
            muted = False
            try:
                import voice

                muted = bool(voice.is_muted())
            except Exception:
                muted = False
            return {
                "ok": True,
                "data": {
                    "system_status": _system_status(s),
                    "quiet_hours": bool(s.get("quiet_hours", False)),
                    "muted": muted,
                    "policy_ok": bool(s.get("policy_ok")),
                    "today": s.get("today"),
                    "root": s.get("root"),
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def metrics(self) -> dict:
        try:
            from metrics import snapshot

            return {"ok": True, "data": snapshot()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def feed(self, limit: int = 50) -> dict:
        try:
            from feed import tail

            return {"ok": True, "data": {"items": tail(self.root, n=int(limit))}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def memory(self) -> dict:
        try:
            from memory_index import build

            return {"ok": True, "data": build(self.root)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def llms(self) -> dict:
        try:
            from llm_providers import probe_all

            return {"ok": True, "data": {"providers": probe_all()}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _agents_hub(self):
        if self._hub is None:
            from agents.worker import AgentHub

            self._hub = AgentHub(root=self.root)
        return self._hub

    def agents(self) -> dict:
        try:
            return {"ok": True, "data": {"agents": self._agents_hub().list()}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def agent_start(self, role_id: str) -> dict:
        try:
            return self._agents_hub().start(str(role_id))
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def agent_stop(self, role_id: str) -> dict:
        try:
            return self._agents_hub().stop(str(role_id))
        except Exception as e:
            return {"ok": False, "error": str(e)}
