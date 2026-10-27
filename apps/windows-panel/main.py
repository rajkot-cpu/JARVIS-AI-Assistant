import sys
from pathlib import Path
import customtkinter as ctk
from panel_api import discover_root, Panel
from ui.app import JarvisApp


def main() -> int:
    exe_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    root = discover_root(exe_dir=exe_dir)
    if root is None:
        from tkinter import filedialog, messagebox
        from panel_api import is_valid_root
        ctk.set_appearance_mode("dark")
        pick = filedialog.askdirectory(title="Select JARVIS root")
        if not pick:
            messagebox.showerror("JARVIS", "No valid JARVIS_ROOT selected.")
            return 2
        root = Path(pick)
        if not is_valid_root(root):
            messagebox.showerror("JARVIS", "Folder missing STATE.md or POLICY.yaml.")
            return 2
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = JarvisApp(Panel(root))
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
