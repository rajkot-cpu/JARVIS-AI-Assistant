import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))

from agents.registry import ROLES
from agents.worker import AgentHub


class TestAgents(unittest.TestCase):
    def test_six_roles(self):
        self.assertEqual(
            {r["id"] for r in ROLES},
            {"coding", "research", "memory", "browser", "task", "system"},
        )

    def test_start_stop_standby(self):
        with tempfile.TemporaryDirectory() as td:
            hub = AgentHub(root=Path(td))
            self.assertTrue(all(a["state"] == "standby" for a in hub.list()))
            hub.start("system")
            row = next(a for a in hub.list() if a["id"] == "system")
            self.assertIn(row["state"], ("active", "error"))
            hub.stop("system")
            self.assertEqual(
                next(a for a in hub.list() if a["id"] == "system")["state"], "standby"
            )


if __name__ == "__main__":
    unittest.main()
