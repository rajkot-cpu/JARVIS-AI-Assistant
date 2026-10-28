import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "windows-cc"))

from llm_providers import probe_all


class TestLlmProviders(unittest.TestCase):
    def test_probe_missing_keys(self):
        saved = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("JARVIS_") and k.endswith("_API_KEY")}
        ollama = os.environ.pop("JARVIS_OLLAMA_BASE", None)
        try:
            rows = probe_all(timeout=1)
            ids = {r["id"] for r in rows}
            self.assertTrue({"anthropic", "openai", "gemini", "groq"} <= ids)
            for r in rows:
                if r["id"] != "ollama":
                    self.assertEqual(r["state"], "missing_key")
        finally:
            os.environ.update(saved)
            if ollama is not None:
                os.environ["JARVIS_OLLAMA_BASE"] = ollama


if __name__ == "__main__":
    unittest.main()
