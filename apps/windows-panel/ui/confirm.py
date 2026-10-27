"""R3 confirm dialog: returns True only on explicit Confirm."""
import customtkinter as ctk
from theme import COLORS


def ask(parent, title: str, body: str) -> bool:
    result = {"ok": False}
    win = ctk.CTkToplevel(parent)
    win.title(title)
    win.configure(fg_color=COLORS["bg"])
    win.resizable(False, False)
    ctk.CTkLabel(win, text=f"R3 // {title}", text_color=COLORS["gold"],
                 font=ctk.CTkFont(size=16, weight="bold")).pack(padx=20, pady=(16, 6))
    ctk.CTkLabel(win, text=body, text_color=COLORS["text"], wraplength=420,
                 justify="left").pack(padx=20, pady=6)
    row = ctk.CTkFrame(win, fg_color="transparent")
    row.pack(pady=(8, 16))

    def done(val: bool):
        result["ok"] = val
        win.grab_release()
        win.destroy()

    ctk.CTkButton(row, text="Confirm", fg_color=COLORS["cyan"], text_color=COLORS["bg"],
                  hover_color=COLORS["gold"], command=lambda: done(True)).pack(side="left", padx=8)
    ctk.CTkButton(row, text="Cancel", fg_color=COLORS["panel"], text_color=COLORS["text"],
                  border_color=COLORS["muted"], border_width=1,
                  command=lambda: done(False)).pack(side="left", padx=8)
    win.protocol("WM_DELETE_WINDOW", lambda: done(False))
    win.transient(parent)
    win.after(10, win.grab_set)
    parent.wait_window(win)
    return result["ok"]
