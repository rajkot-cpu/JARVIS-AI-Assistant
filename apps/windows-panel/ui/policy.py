"""POLICY tab: view/edit POLICY.yaml (R3 confirm + backup on save), view host permission rules."""
import customtkinter as ctk
from theme import COLORS
from ui import confirm

RULES_REL = "host/permission-rules.md"


class PolicyFrame(ctk.CTkFrame):
    def __init__(self, master, app, panel):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.panel = panel
        self.editing = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ctk.CTkLabel(top, text="POLICY", text_color=COLORS["cyan"]).pack(side="left")
        btn = dict(fg_color=COLORS["panel"], text_color=COLORS["cyan"], border_color=COLORS["cyan"],
                   border_width=1, hover_color=COLORS["bg"])
        self.cancel_btn = ctk.CTkButton(top, text="Cancel", command=self.cancel, **btn)
        self.save_btn = ctk.CTkButton(top, text="Save", fg_color=COLORS["cyan"], text_color=COLORS["bg"],
                                      hover_color=COLORS["cyan_hover"], command=self.save)
        self.edit_btn = ctk.CTkButton(top, text="Edit", command=self.start_edit, **btn)
        for b in (self.cancel_btn, self.save_btn, self.edit_btn):
            b.pack(side="right", padx=4)

        tabs = ctk.CTkTabview(self, fg_color=COLORS["bg"], segmented_button_selected_color=COLORS["cyan"],
                              text_color=COLORS["text"])
        tabs.grid(row=1, column=0, sticky="nsew", padx=12, pady=(6, 12))
        for t in ("POLICY.yaml", "Host rules"):
            tabs.add(t)
            tabs.tab(t).grid_columnconfigure(0, weight=1)
            tabs.tab(t).grid_rowconfigure(0, weight=1)
        self.policy_box = ctk.CTkTextbox(tabs.tab("POLICY.yaml"), fg_color=COLORS["bg"], text_color=COLORS["text"])
        self.policy_box.grid(row=0, column=0, sticky="nsew")
        self.rules_box = ctk.CTkTextbox(tabs.tab("Host rules"), fg_color=COLORS["bg"], text_color=COLORS["text"])
        self.rules_box.grid(row=0, column=0, sticky="nsew")
        self.load()

    @staticmethod
    def _fill(box, text: str, editable: bool):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="normal" if editable else "disabled")

    def _set_mode(self, editing: bool):
        self.editing = editing
        self.policy_box.configure(state="normal" if editing else "disabled")
        self.edit_btn.configure(state="disabled" if editing else "normal")
        self.save_btn.configure(state="normal" if editing else "disabled")
        self.cancel_btn.configure(state="normal" if editing else "disabled")

    def load(self):
        self._fill(self.policy_box, self.panel.read_text("POLICY.yaml") or "", False)
        self._fill(self.rules_box, self.panel.read_text(RULES_REL) or f"({RULES_REL} missing)", False)
        self._set_mode(False)

    def refresh(self):
        if not self.editing:
            self.load()

    def start_edit(self):
        self._set_mode(True)
        self.app.set_banner("POLICY: editing — Save requires R3 confirm")

    def cancel(self):
        self.load()
        self.app.set_banner("POLICY: edit cancelled, reloaded from disk")

    def save(self):
        text = self.policy_box.get("1.0", "end-1c")
        if not confirm.ask(self, "Save POLICY", "Overwrite POLICY.yaml? A backup goes to logs/policy-backups/."):
            self.panel.audit("save_policy", "POLICY.yaml", "cancelled")
            self.app.set_banner("POLICY: save cancelled — nothing written")
            return
        try:
            self.panel.save_policy(text)
        except ValueError as e:
            self.app.set_banner(f"POLICY: {e}", error=True)
            return
        self.app.set_banner("POLICY: saved (backup in logs/policy-backups/)")
        self.load()
