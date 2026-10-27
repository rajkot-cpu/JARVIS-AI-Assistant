"""Logs tab: browse logs/ + reports/, tail selected file, filter by date substring."""
import tkinter as tk
from pathlib import Path
import customtkinter as ctk
from theme import COLORS


class LogsFrame(ctk.CTkFrame):
    def __init__(self, master, app, panel):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.panel = panel
        self.files: list[Path] = []
        self.shown: list[Path] = []
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkLabel(top, text="LOGS // REPORTS", text_color=COLORS["cyan"]).pack(side="left")
        ctk.CTkButton(top, text="Refresh", fg_color=COLORS["panel"], text_color=COLORS["cyan"],
                      border_color=COLORS["cyan"], border_width=1, hover_color=COLORS["bg"],
                      command=self.refresh).pack(side="right")
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *a: self._apply_filter())
        ctk.CTkEntry(top, textvariable=self.filter_var, placeholder_text="filter (e.g. 2026-10-28)",
                     width=220, fg_color=COLORS["bg"], text_color=COLORS["text"],
                     border_color=COLORS["cyan"]).pack(side="right", padx=8)

        self.listbox = tk.Listbox(self, bg=COLORS["bg"], fg=COLORS["text"], selectbackground=COLORS["cyan"],
                                  selectforeground=COLORS["bg"], highlightthickness=0, borderwidth=0,
                                  exportselection=False, width=40)
        self.listbox.grid(row=1, column=0, sticky="ns", padx=(12, 6), pady=(6, 12))
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.show_selected())

        self.box = ctk.CTkTextbox(self, fg_color=COLORS["bg"], text_color=COLORS["text"])
        self.box.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(6, 12))
        self.refresh()

    def _rel(self, p: Path) -> str:
        try:
            return str(Path(p).relative_to(self.panel.root))
        except ValueError:
            return str(p)

    def refresh(self):
        files = list(self.panel.list_log_files())
        rd = self.panel.root / "reports"
        if rd.is_dir():
            files += sorted((p for p in rd.rglob("*") if p.is_file()),
                            key=lambda p: p.stat().st_mtime, reverse=True)
        self.files = files
        self._apply_filter()

    def _apply_filter(self):
        q = self.filter_var.get().strip()
        self.shown = [p for p in self.files if q in self._rel(p)] if q else list(self.files)
        self.listbox.delete(0, "end")
        for p in self.shown:
            self.listbox.insert("end", self._rel(p))
        if self.shown:
            self.listbox.selection_set(0)
            self.show_selected()
        else:
            self._set_text("(no matching log or report files)")

    def _set_text(self, text: str):
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.insert("1.0", text)
        self.box.configure(state="disabled")

    def show_selected(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] >= len(self.shown):
            return
        self._set_text(self.panel.tail_log(self.shown[sel[0]]) or "(empty or unreadable)")
