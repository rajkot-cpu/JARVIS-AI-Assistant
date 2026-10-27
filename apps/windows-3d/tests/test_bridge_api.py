# apps/windows-3d/tests/test_bridge_api.py
import sys, tempfile, unittest
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
        self.root = _make_root(Path(self.tmp.name), approved=True)
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

    def test_get_brief_empty_then_text(self):
        r = self.bridge.get_brief()
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["text"], "")
        day = self.bridge.get_status()["data"]["today"]
        (self.root / "reports" / f"{day}.md").write_text("# Brief\nHello\n", encoding="utf-8")
        self.assertIn("Hello", self.bridge.get_brief()["data"]["text"])


if __name__ == "__main__":
    unittest.main()
