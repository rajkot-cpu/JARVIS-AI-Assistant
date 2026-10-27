# apps/windows-3d/host_main.py
from __future__ import annotations
import os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PANEL_DIR = HERE.parent / "windows-panel"
sys.path.insert(0, str(PANEL_DIR))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "scripts" / "win"))

import panel_api
import bridge_api
import voice


class Api:
    def __init__(self, bridge: bridge_api.Bridge):
        self._b = bridge

    def getStatus(self):
        return self._b.get_status()

    def getBrief(self):
        return self._b.get_brief()

    def sessionStart(self):
        return self._b.session_start()

    def workday(self, dry: bool = True):
        return self._b.workday(dry=bool(dry))

    def getMute(self):
        return self._b.get_mute()

    def setMute(self, muted: bool = False):
        return self._b.set_mute(bool(muted))


def main() -> int:
    exe_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else HERE
    root = None
    env = os.environ.get("JARVIS_HOME")
    if env:
        cand = Path(env)
        if panel_api.is_valid_root(cand):
            root = cand.resolve()
    if root is None:
        root = panel_api.discover_root(exe_dir=exe_dir)
    if root is None:
        print("JARVIS_ROOT not found", file=sys.stderr)
        return 2
    voice.load_prefs(root)
    bridge = bridge_api.Bridge(panel_api.Panel(root))
    # Serve ui/ via pywebview's local HTTP server (127.0.0.1) instead of file://,
    # so WebView2 allows ES module imports (Three.js). Relative URL resolves from HERE.
    import os
    os.chdir(HERE)
    import webview
    window = webview.create_window(
        "JARVIS 3D // STARK OS",
        url="ui/index.html",
        js_api=Api(bridge),
        width=1280,
        height=800,
        background_color="#04070b",
    )
    webview.start(gui="edgechromium", http_server=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
