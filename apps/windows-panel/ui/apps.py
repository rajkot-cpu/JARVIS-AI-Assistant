"""Apps tab: allowlisted apps (R3 confirm to launch) + read-only restricted paths."""
import tkinter as tk
import customtkinter as ctk
from theme import COLORS
from ui import confirm


class AppsFrame(ctk.CTkFrame):
    def __init__(self, master, app, panel):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.panel = panel
        self.apps: list[dict] = []
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkLabel(top, text="APPS", text_color=COLORS["cyan"]).pack(side="left")
        ctk.CTkButton(top, text="Refresh", fg_color=COLORS["panel"], text_color=COLORS["cyan"],
                      border_color=COLORS["cyan"], border_width=1, hover_color=COLORS["bg"],
                      command=self.refresh).pack(side="right")
        ctk.CTkButton(top, text="Launch", fg_color=COLORS["cyan"], text_color=COLORS["bg"],
                      hover_color=COLORS["cyan_hover"], command=self.launch_selected).pack(side="right", padx=8)

        ctk.CTkLabel(self, text="Allowlisted (POLICY apps_allowlist)", text_color=COLORS["cyan"],
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=12)
        ctk.CTkLabel(self, text="Restricted (read-only)", text_color=COLORS["danger"],
                     anchor="w").grid(row=1, column=1, sticky="ew", padx=12)
        self.listbox = tk.Listbox(self, bg=COLORS["bg"], fg=COLORS["text"], selectbackground=COLORS["cyan"],
                                  selectforeground=COLORS["bg"], highlightthickness=0, borderwidth=0,
                                  exportselection=False)
        self.listbox.grid(row=2, column=0, sticky="nsew", padx=(12, 6), pady=(6, 12))
        self.restricted = ctk.CTkTextbox(self, fg_color=COLORS["bg"], text_color=COLORS["muted"])
        self.restricted.grid(row=2, column=1, sticky="nsew", padx=(6, 12), pady=(6, 12))
        self.refresh()

    def refresh(self):
        self.apps = self.panel.list_apps()
        self.listbox.delete(0, "end")
        for a in self.apps:
            self.listbox.insert("end", f"{a['name']}  ->  {' | '.join(map(str, a['command']))}")
        if not self.apps:
            self.listbox.insert("end", "(no allowlisted apps)")
        else:
            self.listbox.selection_set(0)
        self.restricted.configure(state="normal")
        self.restricted.delete("1.0", "end")
        self.restricted.insert("1.0", "\n".join(self.panel.list_restricted()) or "(none)")
        self.restricted.configure(state="disabled")

    def launch_selected(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] >= len(self.apps):
            self.app.set_banner("launch: no allowlisted app selected", error=True)
            return
        name = self.apps[sel[0]]["name"]
        if not confirm.ask(self, "Launch app", f"Launch allowlisted app '{name}'?"):
            self.panel.audit("launch_app", name, "cancelled")
            self.app.set_banner(f"launch {name}: cancelled")
            return
        rc, out, err = self.panel.launch_app(name)
        msg = "OK" if rc == 0 else f"REFUSED/FAILED rc={rc} {err.strip()[:120]}"
        self.app.set_banner(f"launch {name}: {msg}", error=rc != 0)
