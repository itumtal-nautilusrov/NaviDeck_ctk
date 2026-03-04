import customtkinter as ctk
from PIL import Image


LANGUAGES = {
    "English": {
        "settings_title": "Settings",
        "general":  "General",
        "camera":   "Camera",
        "map":      "Map",
        "media":    "Media",
        "sound":    "Sound",
        "credits":  "Credits",
        "language_title": "Language",
        "language_subtitle": "Choose the display language of the application.",
    },
    "Türkçe": {
        "settings_title": "Ayarlar",
        "general":  "Genel",
        "camera":   "Kamera",
        "map":      "Harita",
        "media":    "Medya",
        "sound":    "Ses",
        "credits":  "Krediler",
        "language_title": "Dil",
        "language_subtitle": "Uygulamanın görüntüleme dilini seçin.",
    },
}


class SettingsPanel(ctk.CTkFrame):

    def __init__(self, master, language="English", on_language_change=None):
        super().__init__(master, fg_color="#0E0E0E", corner_radius=0)

        self.language = language
        self.on_language_change = on_language_change
        self._strings = LANGUAGES[language]

        self._build_ui()
        self._show_general()

    def _build_ui(self):
        s = self._strings

# _____ TOP BAR ___________________________________

        self.top_bar = ctk.CTkFrame(
            self,
            height=300,
            fg_color="#141414",
            corner_radius=0
        )
        self.top_bar.pack(fill="x", side="top")

        self.back_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/back.png"),
            size=(60, 60)
        )

        self.back_btn = ctk.CTkButton(
            self.top_bar,
            width=60, height=60,
            text="",
            image=self.back_img,
            fg_color="transparent",
            hover=False,
            command=self.close_panel
        )
        self.back_btn.pack(side="left", padx=20)

        self.title_lbl = ctk.CTkLabel(
            self.top_bar,
            text=s["settings_title"],
            font=("Segoe UI", 50, "bold"),
            text_color="#FFFFFF"
        )
        self.title_lbl.pack(anchor="center", pady=40)

        ctk.CTkFrame(self, height=2, fg_color="#2A2A2A", corner_radius=0).pack(fill="x")

# _____ LEFT BAR ___________________________________

        self.left_bar = ctk.CTkFrame(self, width=450, fg_color="transparent", corner_radius=0)
        self.left_bar.pack(side="left", fill="y", pady=20)

        _btn = dict(
            height=75, width=450,
            font=ctk.CTkFont("Segoe UI", 28, "bold"),
            fg_color="#1A1A1A",
            hover_color="#242424",
            text_color="#E0E0E0",
            corner_radius=14,
            anchor="w",
        )

        icon_cfg = [
            ("general",  "./_icons/settings/general.png",  self._show_general),
            ("camera",   "./_icons/settings/camera.png",   lambda: self._show_placeholder("camera")),
            ("map",      "./_icons/settings/map.png",      lambda: self._show_placeholder("map")),
            ("media",    "./_icons/settings/media.png",    lambda: self._show_placeholder("media")),
            ("sound",    "./_icons/settings/sound.png",    lambda: self._show_placeholder("sound")),
            ("credits",  "./_icons/settings/credits.png",  lambda: self._show_placeholder("credits")),
        ]

        self._nav_btns = {}
        first = True
        for key, icon_path, cmd in icon_cfg:
            img = ctk.CTkImage(light_image=Image.open(icon_path), size=(40, 40))
            btn = ctk.CTkButton(
                self.left_bar,
                image=img,
                text=f"  {s[key]}",
                command=cmd,
                **_btn
            )
            btn.pack(padx=12, pady=(0 if first else 10, 0))
            self._nav_btns[key] = btn
            first = False

        ctk.CTkFrame(self, width=2, fg_color="#2A2A2A", corner_radius=0).pack(side="left", fill="y", pady=20)

# _____ MAIN FRAME ___________________________________

        self.main_frame = ctk.CTkFrame(self, fg_color="#141414", corner_radius=16)
        self.main_frame.pack(fill="both", expand=True, pady=20, padx=20)

# ─────────────────────────────────────────────────

    def _clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def _show_general(self):
        self._clear_main()
        s = self._strings

        ctk.CTkLabel(
            self.main_frame,
            text=s["language_title"],
            font=("Segoe UI", 32, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=30, pady=(28, 4))

        ctk.CTkLabel(
            self.main_frame,
            text=s["language_subtitle"],
            font=("Segoe UI", 18),
            text_color="#888888"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        toggle_frame = ctk.CTkFrame(self.main_frame, fg_color="#1A1A1A", corner_radius=16)
        toggle_frame.pack(anchor="w", padx=30)

        for lang in ("English", "Türkçe"):
            selected = lang == self.language
            btn = ctk.CTkButton(
                toggle_frame,
                text=lang,
                width=180, height=60,
                font=("Segoe UI", 22, "bold"),
                fg_color="#00FFAA" if selected else "#2A2A2A",
                text_color="#000000" if selected else "#AAAAAA",
                hover_color="#00FFAA" if selected else "#333333",
                corner_radius=12,
                command=lambda l=lang: self._change_language(l)
            )
            btn.pack(side="left", padx=8, pady=8)

    def _show_placeholder(self, key):
        self._clear_main()
        ctk.CTkLabel(
            self.main_frame,
            text=self._strings[key],
            font=("Segoe UI", 36, "bold"),
            text_color="#444444"
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _change_language(self, lang):
        if lang == self.language:
            return
        self.language = lang
        if self.on_language_change:
            self.on_language_change(lang)

    def close_panel(self):
        self.place_forget()