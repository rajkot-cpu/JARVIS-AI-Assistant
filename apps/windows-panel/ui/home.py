"""Home tab: status strip, today's brief preview, workday actions."""
import customtkinter as ctk
from theme import COLORS
from ui import confirm


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, app, panel):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.panel = panel
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        strip = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        strip.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        self.status_labels = {}
        for i, key in enumerate(["today", "policy", "quiet", "root"]):
            lbl = ctk.CTkLabel(strip, text="", text_color=COLORS["cyan"], anchor="w")
            lbl.grid(row=0, column=i, padx=10, pady=6, sticky="w")
            self.status_labels[key] = lbl

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        for text, cmd in [("Session Start", self.on_session_start),
                          ("Dry-run Workday", self.on_dry_workday),
                          ("Start Workday", self.on_workday),
                          ("Regenerate Brief", self.on_write_brief)]:
            ctk.CTkButton(btns, text=text, fg_color=COLORS["panel"], text_color=COLORS["cyan"],
                          border_color=COLORS["cyan"], border_width=1,
                          hover_color=COLORS["bg"], command=cmd).pack(side="left", padx=6)

        self.brief = ctk.CTkTextbox(self, fg_color=COLORS["bg"], text_color=COLORS["text"])
        self.brief.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))
        self.refresh()

    def refresh(self):
        s = self.panel.status_strip()
        self.status_labels["today"].configure(text=f"DATE {s.get('today', '?')}")
        ok = s.get("policy_ok")
        self.status_labels["policy"].configure(
            text=f"POLICY {'APPROVED' if ok else 'NOT APPROVED'}",
            text_color=COLORS["ok"] if ok else COLORS["danger"])
        self.status_labels["quiet"].configure(
            text=f"QUIET {'ON' if s.get('quiet_hours') else 'OFF'}", text_color=COLORS["gold"])
        self.status_labels["root"].configure(text=f"ROOT {s.get('root', '')}", text_color=COLORS["muted"])
        text = self.panel.today_brief() or "(no brief for today yet — Regenerate Brief)"
        self.brief.configure(state="normal")
        self.brief.delete("1.0", "end")
        self.brief.insert("1.0", text)
        self.brief.configure(state="disabled")

    def _report(self, label, result):
        code, out, err = result
        if code == 0:
            self.app.set_banner(f"{label}: OK")
        else:
            msg = (err or out or "").strip().splitlines()
            self.app.set_banner(f"{label} FAILED (exit {code}): {msg[-1] if msg else ''}", error=True)
        self.refresh()

    def on_session_start(self):
        self._report("Session Start", self.panel.session_start())

    def on_dry_workday(self):
        self._report("Dry-run Workday", self.panel.workday(dry=True))

    def on_workday(self):
        if not confirm.ask(self.app, "Start Workday", "Run workday_start (writes STATE/reports, audited)?"):
            self.app.set_banner("Start Workday cancelled")
            return
        self._report("Start Workday", self.panel.workday(dry=False))

    def on_write_brief(self):
        if not confirm.ask(self.app, "Regenerate Brief", "Overwrite today's brief in reports/?"):
            self.app.set_banner("Regenerate Brief cancelled")
            return
        self._report("Regenerate Brief", self.panel.write_brief())
