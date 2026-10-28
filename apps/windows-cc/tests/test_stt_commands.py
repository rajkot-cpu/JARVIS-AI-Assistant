import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))
sys.path.insert(0, str(ROOT / "scripts" / "win"))


def _make_root(tmp: Path) -> Path:
    (tmp / "STATE.md").write_text("# STATE\n", encoding="utf-8")
    (tmp / "POLICY.yaml").write_text(
        'status: approved\nschedule:\n  quiet_hours: "00:00-00:00"\n',
        encoding="utf-8",
    )
    (tmp / "reports").mkdir(exist_ok=True)
    (tmp / "logs").mkdir(exist_ok=True)
    return tmp


class TestCommands(unittest.TestCase):
    def test_dry_run_calls_panel(self):
        from bridge_api import BridgeApi

        with tempfile.TemporaryDirectory() as td:
            root = _make_root(Path(td))
            api = BridgeApi(root=root)
            called = {}

            class Fake:
                def workday(self, dry=True):
                    called["dry"] = dry
                    return 0, "ok", ""

                def status_strip(self):
                    return {"policy_ok": True, "quiet_hours": False, "today": "2026-10-28", "root": str(root)}

            api.panel = Fake()
            out = api.dry_run_workday()
            self.assertTrue(out["ok"])
            self.assertTrue(called["dry"] is True)

    def test_start_workday_requires_r3(self):
        from bridge_api import BridgeApi

        with tempfile.TemporaryDirectory() as td:
            api = BridgeApi(root=_make_root(Path(td)))
            out = api.start_workday(confirmed=False)
            self.assertFalse(out["ok"])
            self.assertIn("R3", out["error"])


if __name__ == "__main__":
    unittest.main()
