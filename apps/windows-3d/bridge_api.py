# apps/windows-3d/bridge_api.py
from __future__ import annotations
from pathlib import Path
import sys

_PANEL = Path(__file__).resolve().parents[1] / "windows-panel"
if str(_PANEL) not in sys.path:
    sys.path.insert(0, str(_PANEL))

import panel_api  # noqa: E402


def _headline(status: dict) -> str:
    if not status.get("policy_ok"):
        return "POLICY NOT APPROVED"
    if status.get("quiet_hours"):
        return "QUIET HOURS"
    return "SYSTEMS NOMINAL"


class Bridge:
    def __init__(self, panel: panel_api.Panel):
        self.panel = panel

    def get_status(self) -> dict:
        try:
            s = self.panel.status_strip()
            data = dict(s)
            data["headline"] = _headline(s)
            return {"ok": True, "data": data}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_brief(self) -> dict:
        try:
            return {"ok": True, "data": {"text": self.panel.today_brief() or ""}}
        except Exception as e:
            return {"ok": False, "error": str(e)}
