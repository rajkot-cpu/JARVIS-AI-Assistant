"""STATE tab: read-only view of STATE.md."""
import customtkinter as ctk
from theme import COLORS


class StateFrame(ctk.CTkFrame):
    def __init__(self, master, app, panel):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.panel = panel
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkLabel(top, text="STATE.md  (read-only)", text_color=COLORS["gold"]).pack(side="left")
        ctk.CTkButton(top, text="Refresh", fg_color=COLORS["panel"], text_color=COLORS["cyan"],
                      border_color=COLORS["cyan"], border_width=1, hover_color=COLORS["bg"],
                      command=self.refresh).pack(side="right")
        self.box = ctk.CTkTextbox(self, fg_color=COLORS["bg"], text_color=COLORS["text"])
        self.box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6, 12))
        self.refresh()

    def refresh(self):
        text = self.panel.read_text("STATE.md") or "(STATE.md missing)"
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.insert("1.0", text)
        self.box.configure(state="disabled")
