import os, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # /home/box/jarvis or C:\Users\rajk1\jarvis
sys.path.insert(0, str(ROOT / "apps" / "windows-panel"))
sys.path.insert(0, str(ROOT / "scripts" / "win"))

import panel_api


class TestRoot(unittest.TestCase):
    def test_is_valid_root_requires_state_and_policy(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self.assertFalse(panel_api.is_valid_root(p))
            (p / "STATE.md").write_text("#", encoding="utf-8")
            self.assertFalse(panel_api.is_valid_root(p))
            (p / "POLICY.yaml").write_text("status: approved\n", encoding="utf-8")
            self.assertTrue(panel_api.is_valid_root(p))

    def test_discover_root_prefers_exe_dir_when_valid(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "STATE.md").write_text("#", encoding="utf-8")
            (p / "POLICY.yaml").write_text("status: approved\n", encoding="utf-8")
            found = panel_api.discover_root(exe_dir=p, default=Path("/nonexistent"))
            self.assertEqual(found, p.resolve())

    def test_jarvis_home_env_override(self):
        import lib_jarvis
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            old = os.environ.get("JARVIS_HOME")
            os.environ["JARVIS_HOME"] = str(p)
            try:
                self.assertEqual(lib_jarvis.jarvis_home(), p.resolve())
            finally:
                if old is None:
                    os.environ.pop("JARVIS_HOME", None)
                else:
                    os.environ["JARVIS_HOME"] = old


if __name__ == "__main__":
    unittest.main()
