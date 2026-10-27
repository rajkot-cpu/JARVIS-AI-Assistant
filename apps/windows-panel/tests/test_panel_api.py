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



class TestReads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "STATE.md").write_text("# STATE\n## Status\nok\n", encoding="utf-8")
        (self.root / "POLICY.yaml").write_text(
            'status: approved\napps_allowlist: [chrome, terminal]\n'
            'restricted: ["~/patients"]\n'
            'schedule:\n  quiet_hours: "22:00-07:00"\n',
            encoding="utf-8",
        )
        (self.root / "reports").mkdir()
        (self.root / "logs").mkdir()
        (self.root / "skills" / "file-search").mkdir(parents=True)
        (self.root / "skills" / "file-search" / "SKILL.md").write_text(
            "# Skill: file-search\nFind files under jarvis.\n", encoding="utf-8"
        )
        (self.root / "skills" / "app-control").mkdir(parents=True)
        (self.root / "skills" / "app-control" / "SKILL.md").write_text(
            "# Skill: app-control\nLaunch allowlisted apps.\n", encoding="utf-8"
        )
        self.panel = panel_api.Panel(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_skills(self):
        skills = {s["name"]: s for s in self.panel.list_skills()}
        self.assertEqual(skills["file-search"]["risk"], "read")
        self.assertEqual(skills["app-control"]["risk"], "write")
        self.assertIn("Find files", skills["file-search"]["summary"])

    def test_list_apps_and_restricted(self):
        apps = self.panel.list_apps()
        names = {a["name"] for a in apps}
        self.assertEqual(names, {"chrome", "terminal"})
        self.assertEqual(self.panel.list_restricted(), ["~/patients"])

    def test_today_brief_empty_then_present(self):
        self.assertEqual(self.panel.today_brief(), "")
        day = self.panel.status_strip()["today"]
        (self.root / "reports" / f"{day}.md").write_text("hello brief", encoding="utf-8")
        self.assertEqual(self.panel.today_brief(), "hello brief")


class TestActions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "STATE.md").write_text("# STATE\n", encoding="utf-8")
        (self.root / "POLICY.yaml").write_text(
            "status: approved\napps_allowlist: [chrome]\nrestricted: []\n",
            encoding="utf-8",
        )
        (self.root / "logs").mkdir()
        (self.root / "reports").mkdir()
        (self.root / "scripts" / "win").mkdir(parents=True)
        (self.root / "scripts" / "win" / "block_delete.py").write_text(
            "import sys\nfrom pathlib import Path\n"
            "p=Path(sys.argv[1])\n"
            "print('REFUSED' if p.name=='STATE.md' else 'OK')\n"
            "sys.exit(2 if p.name=='STATE.md' else 0)\n",
            encoding="utf-8",
        )
        self.panel = panel_api.Panel(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_audit_line(self):
        self.panel.audit("test", "STATE.md", "ok", "detail")
        lines = (self.root / "logs" / "audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("windows-panel", lines[0])

    def test_save_policy_backup_and_reject_bad_yaml(self):
        with self.assertRaises(ValueError):
            self.panel.save_policy(":\n  bad")
        path = self.panel.save_policy("status: approved\napps_allowlist: [chrome]\n")
        self.assertTrue(path.is_file())
        backups = list((self.root / "logs" / "policy-backups").glob("POLICY-*.yaml"))
        self.assertTrue(backups)

    def test_launch_unknown_refused(self):
        code, out, err = self.panel.launch_app("not-an-app")
        self.assertNotEqual(code, 0)

    def test_block_delete_refuses_state(self):
        code, out, err = self.panel.block_delete(self.root / "STATE.md")
        self.assertEqual(code, 2)
        self.assertIn("REFUSED", out)

    def test_run_script_in_process_frozen_path(self):
        code, out, err = self.panel.run_script("block_delete", [str(self.root / "STATE.md")], in_process=True)
        self.assertEqual(code, 2)
        self.assertIn("REFUSED", out)
        code, out, err = self.panel.run_script("block_delete", [str(self.root / "x.txt")], in_process=True)
        self.assertEqual(code, 0)

    def test_run_script_uses_in_process_when_frozen(self):
        sys.frozen = True
        try:
            code, out, err = self.panel.block_delete(self.root / "STATE.md")
        finally:
            del sys.frozen
        self.assertEqual(code, 2)
        self.assertIn("REFUSED", out)

if __name__ == "__main__":
    unittest.main()
