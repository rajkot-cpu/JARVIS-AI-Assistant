"""Skills tab: list skills/*, show SKILL.md, Run with R3 confirm for write-risk skills."""
import tkinter as tk
import customtkinter as ctk
from theme import COLORS
from ui import confirm

STUB_BANNER = "skill runner: windows stub — see SKILL.md"


class SkillsFrame(ctk.CTkFrame):
    def __init__(self, master, app, panel):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.panel = panel
        self.skills: list[dict] = []
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkLabel(top, text="SKILLS", text_color=COLORS["cyan"]).pack(side="left")
        ctk.CTkButton(top, text="Refresh", fg_color=COLORS["panel"], text_color=COLORS["cyan"],
                      border_color=COLORS["cyan"], border_width=1, hover_color=COLORS["bg"],
                      command=self.refresh).pack(side="right")
        self.run_btn = ctk.CTkButton(top, text="Run", fg_color=COLORS["cyan"], text_color=COLORS["bg"],
                                     hover_color=COLORS["cyan_hover"], command=self.run_selected)
        self.run_btn.pack(side="right", padx=8)

        self.listbox = tk.Listbox(self, bg=COLORS["bg"], fg=COLORS["text"], selectbackground=COLORS["cyan"],
                                  selectforeground=COLORS["bg"], highlightthickness=0, borderwidth=0,
                                  exportselection=False, width=28)
        self.listbox.grid(row=1, column=0, sticky="ns", padx=(12, 6), pady=(6, 12))
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.show_selected())

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(6, 12))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        self.summary = ctk.CTkLabel(right, text="", text_color=COLORS["cyan"], anchor="w",
                                    justify="left", wraplength=600)
        self.summary.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.box = ctk.CTkTextbox(right, fg_color=COLORS["bg"], text_color=COLORS["text"])
        self.box.grid(row=1, column=0, sticky="nsew")
        self.refresh()

    def refresh(self):
        self.skills = self.panel.list_skills()
        self.listbox.delete(0, "end")
        for s in self.skills:
            tag = " [W]" if s["risk"] == "write" else ""
            self.listbox.insert("end", s["name"] + tag)
        if self.skills:
            self.listbox.selection_set(0)
            self.show_selected()
        else:
            self.summary.configure(text="(no skills/ found)")
            self._set_text("")

    def _selected(self):
        sel = self.listbox.curselection()
        return self.skills[sel[0]] if sel and sel[0] < len(self.skills) else None

    def _set_text(self, text: str):
        self.box.configure(state="normal")
        self.box.delete("1.0", "end")
        self.box.insert("1.0", text)
        self.box.configure(state="disabled")

    def _skill_md(self, s) -> str:
        return self.panel.read_text(f"skills/{s['name']}/SKILL.md") or "(SKILL.md missing)"

    def show_selected(self):
        s = self._selected()
        if not s:
            return
        self.summary.configure(text=f"{s['name']}  //  risk={s['risk']}\n{s['summary']}")
        self._set_text(self._skill_md(s))

    def _report(self, label: str, rc: int, out: str, err: str):
        self.app.set_banner(f"{label}: {'OK' if rc == 0 else f'FAILED rc={rc}'} {err.strip()[:120]}",
                            error=rc != 0)
        self._set_text((out or "") + ("\n--- stderr ---\n" + err if err else ""))

    def run_selected(self):
        s = self._selected()
        if not s:
            return
        name = s["name"]
        if s["risk"] == "write":
            if "workday" in name:
                if not confirm.ask(self, "Run skill", f"Run '{name}' (non-dry workday start)?"):
                    self.panel.audit("skill_run", name, "cancelled")
                    self.app.set_banner(f"{name}: cancelled")
                    return
                self._report(name, *self.panel.workday(dry=False))
                return
            if "app-control" in name:
                apps = self.panel.parse_policy().get("apps_allowlist") or []
                dlg = ctk.CTkInputDialog(title="app-control",
                                         text=f"App to launch (allowlist: {', '.join(map(str, apps)) or 'none'}):")
                app_name = (dlg.get_input() or "").strip()
                if not app_name:
                    return
                if not confirm.ask(self, "Launch app", f"Launch allowlisted app '{app_name}'?"):
                    self.panel.audit("skill_run", f"{name}:{app_name}", "cancelled")
                    self.app.set_banner(f"{name}: cancelled")
                    return
                self._report(f"launch {app_name}", *self.panel.launch_app(app_name))
                return
            if not confirm.ask(self, "Run skill", f"Run write-risk skill '{name}'?"):
                self.panel.audit("skill_run", name, "cancelled")
                return
        self.app.set_banner(f"{name}: {STUB_BANNER}")
        self._set_text(self._skill_md(s))
