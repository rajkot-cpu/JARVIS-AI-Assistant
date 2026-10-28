import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))


class TestMetricsFeed(unittest.TestCase):
    def test_metrics_snapshot_keys(self):
        from metrics import snapshot

        m = snapshot()
        self.assertTrue({"cpu_pct", "ram_pct", "disk_pct"} <= set(m))
        self.assertGreaterEqual(m["cpu_pct"], 0.0)
        self.assertLessEqual(m["cpu_pct"], 100.0)

    def test_feed_tail_reads_jsonl(self):
        from feed import tail

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "logs").mkdir()
            (root / "logs" / "audit.jsonl").write_text(
                json.dumps({"t": "1", "msg": "hi"}) + "\n", encoding="utf-8"
            )
            rows = tail(root, n=10)
            self.assertEqual(rows[0]["msg"], "hi")


if __name__ == "__main__":
    unittest.main()
