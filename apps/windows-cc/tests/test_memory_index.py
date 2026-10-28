import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))


class TestMemoryIndex(unittest.TestCase):
    def test_memory_index_counts(self):
        from memory_index import build

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "STATE.md").write_text("hello\n", encoding="utf-8")
            (root / "journal").mkdir()
            (root / "journal" / "a.md").write_text("note\n", encoding="utf-8")
            data = build(root)
            self.assertGreaterEqual(data["nodes"], 2)
            self.assertIn("STATE.md", data["sources"])


if __name__ == "__main__":
    unittest.main()
