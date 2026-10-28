# apps/windows-cc/tests/test_bridge_status.py
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))
sys.path.insert(0, str(ROOT / "scripts" / "win"))


def _make_root(tmp: Path, *, approved: bool = True) -> Path:
    (tmp / "STATE.md").write_text("# STATE\n", encoding="utf-8")
    status = "approved" if approved else "draft"
    (tmp / "POLICY.yaml").write_text(
        f"status: {status}\nschedule:\n  quiet_hours: \"00:00-00:00\"\n",
        encoding="utf-8",
    )
    (tmp / "reports").mkdir(exist_ok=True)
    (tmp / "logs").mkdir(exist_ok=True)
    return tmp


class TestBridgeStatus(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = _make_root(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_status_ok_shape(self):
        from bridge_api import BridgeApi

        api = BridgeApi(root=self.root)
        out = api.status()
        self.assertTrue(out["ok"])
        self.assertIn("data", out)
        d = out["data"]
        self.assertIn("system_status", d)
        self.assertIn("quiet_hours", d)
        self.assertIn("muted", d)
        self.assertEqual(d["system_status"], "SYSTEMS NOMINAL")

    def test_status_policy_not_approved(self):
        from bridge_api import BridgeApi

        root = _make_root(Path(tempfile.mkdtemp()), approved=False)
        api = BridgeApi(root=root)
        self.assertEqual(api.status()["data"]["system_status"], "POLICY NOT APPROVED")


if __name__ == "__main__":
    unittest.main()
