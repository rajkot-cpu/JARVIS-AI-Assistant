# apps/windows-3d/tests/test_bridge_api.py
import sys, tempfile, unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))
sys.path.insert(0, str(ROOT / "apps" / "windows-3d"))
sys.path.insert(0, str(ROOT / "scripts" / "win"))

import panel_api
import bridge_api


def _make_root(tmp: Path, *, approved: bool = True, quiet: str = "22:00-07:00") -> Path:
    (tmp / "STATE.md").write_text("# STATE\n", encoding="utf-8")
    status = "approved" if approved else "draft"
    (tmp / "POLICY.yaml").write_text(
        f"status: {status}\nschedule:\n  quiet_hours: \"{quiet}\"\n",
        encoding="utf-8",
    )
    (tmp / "reports").mkdir()
    (tmp / "logs").mkdir()
    return tmp


class TestBridgeReads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # 00:00-00:00 = never quiet, so the test is clock-independent
        self.root = _make_root(Path(self.tmp.name), approved=True, quiet="00:00-00:00")
        self.bridge = bridge_api.Bridge(panel_api.Panel(self.root))

    def tearDown(self):
        self.tmp.cleanup()

    def test_get_status_ok_shape(self):
        r = self.bridge.get_status()
        self.assertTrue(r["ok"])
        d = r["data"]
        self.assertIn("today", d)
        self.assertTrue(d["policy_ok"])
        self.assertEqual(d["headline"], "SYSTEMS NOMINAL")
        self.assertEqual(d["root"], str(self.root.resolve()))

    def test_headline_policy_not_approved(self):
        root = _make_root(Path(tempfile.mkdtemp()), approved=False)
        b = bridge_api.Bridge(panel_api.Panel(root))
        self.assertEqual(b.get_status()["data"]["headline"], "POLICY NOT APPROVED")

    def test_headline_quiet_hours(self):
        import lib_jarvis
        with mock.patch.object(lib_jarvis, "quiet_hours_active", return_value=True):
            self.assertEqual(self.bridge.get_status()["data"]["headline"], "QUIET HOURS")

    def test_get_brief_empty_then_text(self):
        r = self.bridge.get_brief()
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["text"], "")
        day = self.bridge.get_status()["data"]["today"]
        (self.root / "reports" / f"{day}.md").write_text("# Brief\nHello\n", encoding="utf-8")
        self.assertIn("Hello", self.bridge.get_brief()["data"]["text"])


class TestBridgeActions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = _make_root(Path(self.tmp.name))
        self.panel = panel_api.Panel(self.root)
        self.bridge = bridge_api.Bridge(self.panel)
        # voice prefs path
        import voice
        voice.load_prefs(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_mute_roundtrip(self):
        import voice
        self.assertFalse(self.bridge.get_mute()["data"]["muted"])
        self.bridge.set_mute(True)
        self.assertTrue(voice.is_muted())
        self.assertTrue(self.bridge.get_mute()["data"]["muted"])

    def test_mute_errors_return_ok_false(self):
        import voice
        with mock.patch.object(voice, "is_muted", side_effect=RuntimeError("boom")):
            r = self.bridge.get_mute()
            self.assertFalse(r["ok"]); self.assertIn("boom", r["error"])
        with mock.patch.object(voice, "set_muted", side_effect=RuntimeError("boom2")):
            r = self.bridge.set_mute(True)
            self.assertFalse(r["ok"]); self.assertIn("boom2", r["error"])

    def test_workday_dry_returns_dict(self):
        # May fail scripts on Linux box — assert shape only; mock Panel.workday
        self.panel.workday = lambda dry=False: (0, "ok", "")
        r = self.bridge.workday(dry=True)
        self.assertTrue(r["ok"])
        self.assertEqual(r["code"], 0)

    def test_session_start_shape(self):
        self.panel.session_start = lambda: (0, "ok", "")
        r = self.bridge.session_start()
        self.assertTrue(r["ok"])


if __name__ == "__main__":
    unittest.main()
