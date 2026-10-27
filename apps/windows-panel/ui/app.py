"""JARVIS main shell window: left nav + swappable content frames."""
import sys
from pathlib import Path
import customtkinter as ctk
import voice
from theme import COLORS
from ui.home import HomeFrame
from ui.state_view import StateFrame
from ui.skills import SkillsFrame
from ui.policy import PolicyFrame
from ui.logs import LogsFrame
from ui.apps import AppsFrame

TABS = ["Home", "Skills", "POLICY", "Logs", "Apps", "STATE"]


class JarvisApp(ctk.CTk):
    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        self.title("JARVIS // STARK OS")
        self.geometry("1100x700")
        self.configure(fg_color=COLORS["bg"])
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
            ico = base / "assets" / "jarvis.ico"
            if ico.exists():
                self.iconbitmap(str(ico))
        except Exception:
            pass
        voice.load_prefs(panel.root)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.banner = ctk.CTkLabel(self, text="", text_color=COLORS["cyan"], anchor="w")
        self.banner.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 0))

        nav = ctk.CTkFrame(self, fg_color=COLORS["panel"], width=180)
        nav.grid(row=1, column=0, sticky="ns", padx=(12, 6), pady=12)
        ctk.CTkLabel(nav, text="J.A.R.V.I.S", text_color=COLORS["gold"],
                     font=ctk.CTkFont(size=18, weight="bold")).pack(padx=16, pady=(16, 12))

        self.content = ctk.CTkFrame(self, fg_color=COLORS["panel"])
        self.content.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=12)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.frames = {}
        for name in TABS:
            btn = ctk.CTkButton(nav, text=name, fg_color="transparent", text_color=COLORS["text"],
                                hover_color=COLORS["bg"], anchor="w",
                                command=lambda n=name: self.show(n))
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[name] = btn
            if name == "Home":
                frame = HomeFrame(self.content, self, panel)
            elif name == "Skills":
                frame = SkillsFrame(self.content, self, panel)
            elif name == "POLICY":
                frame = PolicyFrame(self.content, self, panel)
            elif name == "Logs":
                frame = LogsFrame(self.content, self, panel)
            elif name == "Apps":
                frame = AppsFrame(self.content, self, panel)
            elif name == "STATE":
                frame = StateFrame(self.content, self, panel)
            else:
                frame = ctk.CTkFrame(self.content, fg_color="transparent")
                ctk.CTkLabel(frame, text=f"{name} — coming soon", text_color=COLORS["muted"]).pack(pady=40)
            self.frames[name] = frame
        self.current = None
        self.show("Home")
        self.after(600, lambda: voice.speak("JARVIS online. Systems nominal."))

    def show(self, name: str):
        if self.current:
            self.frames[self.current].grid_forget()
            self.nav_buttons[self.current].configure(text_color=COLORS["text"])
        self.frames[name].grid(row=0, column=0, sticky="nsew")
        self.nav_buttons[name].configure(text_color=COLORS["cyan"])
        self.current = name
        if hasattr(self.frames[name], "refresh"):
            self.frames[name].refresh()

    def set_banner(self, text: str, error: bool = False):
        self.banner.configure(text=text, text_color=COLORS["danger"] if error else COLORS["cyan"])
        if error:
            voice.speak("Attention. " + text[:80])
