import os
import sys
import threading
import customtkinter as ctk
from PIL import Image
import tkintermapview

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
        "connection_log_title": "CONNECTION LOG",
        "server_connect": "Connect",
        "server_disconnect": "Disconnect"
    },
    "Türkçe": {
        "settings_title": "Ayarlar",
        "general":  "Genel",
        "camera":   "Kamera",
        "map":      "Harita",
        "media":    "Medya",
        "sound":    "Ses",
        "credits":  "Katkıda Bulunanlar",
        "language_title": "Dil",
        "language_subtitle": "Uygulamanın görüntüleme dilini seçin.",
        "connection_log_title": "BAĞLANTI KAYDI",
        "server_connect": "Bağlan",
        "server_disconnect": "Bağlantıyı Kes"
    },
}

RESOLUTIONS = ["4K", "1080p", "720p", "480p"]

# ==========================================
# TERMİNAL (STDOUT) YAKALAYICI (YÜZDE GÖSTERMEK İÇİN)
# ==========================================
class PrintCapture:
    def __init__(self, callback):
        self.callback = callback
        self.stdout = sys.stdout
        
    def write(self, text):
        self.stdout.write(text) # Konsola yazmaya devam et
        # tkintermapview "tile ... / ..." şeklinde yazdırır, onu yakalıyoruz
        if "tile" in text.lower() or "/" in text:
            self.callback(text.strip())
            
    def flush(self):
        self.stdout.flush()


# ==========================================
# ANA AYARLAR PANELİ
# ==========================================
class SettingsPanel(ctk.CTkFrame):

    def __init__(self, master, language="English", on_language_change=None, on_map_offline_change=None):
        super().__init__(master, fg_color="#0E0E0E", corner_radius=0)
        self.language = language
        self.on_language_change = on_language_change
        self.on_map_offline_change = on_map_offline_change
        self._strings = LANGUAGES[language]
        self._build_ui()
        self._show_general()

    def _build_ui(self):
        s = self._strings
        self.top_bar = ctk.CTkFrame(self, height=300, fg_color="#141414", corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.back_img = ctk.CTkImage(light_image=Image.open("./_icons/settings/back.png"), size=(60, 60))
        self.back_btn = ctk.CTkButton(self.top_bar, width=60, height=60, text="", image=self.back_img, fg_color="transparent", hover=False, command=self.close_panel)
        self.back_btn.pack(side="left", padx=20)
        self.title_lbl = ctk.CTkLabel(self.top_bar, text=s["settings_title"], font=("Segoe UI", 50, "bold"), text_color="#FFFFFF")
        self.title_lbl.pack(anchor="center", pady=40)
        ctk.CTkFrame(self, height=2, fg_color="#2A2A2A", corner_radius=0).pack(fill="x")

        self.left_bar = ctk.CTkFrame(self, width=450, fg_color="transparent", corner_radius=0)
        self.left_bar.pack(side="left", fill="y", pady=20)
        _btn = dict(height=75, width=450, font=ctk.CTkFont("Segoe UI", 28, "bold"), fg_color="#1A1A1A", hover_color="#242424", text_color="#E0E0E0", corner_radius=14, anchor="w")

        icon_cfg = [
            ("general",  "./_icons/settings/general.png",  self._show_general),
            ("camera",   "./_icons/settings/camera.png",   lambda: self._show_placeholder("camera")),
            ("map",      "./_icons/settings/map.png",      self._show_map),
            ("media",    "./_icons/settings/media.png",    lambda: self._show_placeholder("media")),
            ("sound",    "./_icons/settings/sound.png",    lambda: self._show_placeholder("sound")),
            ("credits",  "./_icons/settings/credits.png",  lambda: self._show_placeholder("credits")),
        ]

        self._nav_btns = {}
        first = True
        for key, icon_path, cmd in icon_cfg:
            img = ctk.CTkImage(light_image=Image.open(icon_path), size=(40, 40))
            btn = ctk.CTkButton(self.left_bar, image=img, text=f"  {s[key]}", command=cmd, **_btn)
            btn.pack(padx=12, pady=(0 if first else 10, 0))
            self._nav_btns[key] = btn
            first = False

        ctk.CTkFrame(self, width=2, fg_color="#2A2A2A", corner_radius=0).pack(side="left", fill="y", pady=20)
        self.main_frame = ctk.CTkFrame(self, fg_color="#141414", corner_radius=16)
        self.main_frame.pack(fill="both", expand=True, pady=20, padx=20)

    def _clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def _show_general(self):
        self._clear_main()
        s = self._strings
        ctk.CTkLabel(self.main_frame, text=s["language_title"], font=("Segoe UI", 32, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(28, 4))
        ctk.CTkLabel(self.main_frame, text=s["language_subtitle"], font=("Segoe UI", 18), text_color="#888888").pack(anchor="w", padx=30, pady=(0, 20))
        toggle_frame = ctk.CTkFrame(self.main_frame, fg_color="#1A1A1A", corner_radius=16)
        toggle_frame.pack(anchor="w", padx=30)
        for lang in ("English", "Türkçe"):
            selected = lang == self.language
            btn = ctk.CTkButton(
                toggle_frame, text=lang, width=180, height=60, font=("Segoe UI", 22, "bold"),
                fg_color="#00FFAA" if selected else "#2A2A2A", text_color="#000000" if selected else "#AAAAAA",
                hover_color="#00FFAA" if selected else "#333333", corner_radius=12,
                command=lambda l=lang: self._change_language(l)
            )
            btn.pack(side="left", padx=8, pady=8)

    def _show_map(self):
        """Configure and download tiles into the map widget's local database."""
        self._clear_main()
        ctk.CTkLabel(self.main_frame, text="Offline Map", font=("Segoe UI", 32, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(28, 4))
        ctk.CTkLabel(
            self.main_frame, text="Download a bounded satellite area before going offline.",
            font=("Segoe UI", 18), text_color="#888888"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        self.offline_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self.main_frame, text="Use downloaded tiles only", variable=self.offline_var,
            command=self._set_offline_mode, font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=30, pady=(0, 18))

        form = ctk.CTkFrame(self.main_frame, fg_color="#1A1A1A", corner_radius=16)
        form.pack(anchor="w", padx=30, pady=4)
        self.map_top_left = self._map_entry(form, "Top left (lat, lng)", "41.0500, 28.9000", 0)
        self.map_bottom_right = self._map_entry(form, "Bottom right (lat, lng)", "40.9500, 29.0500", 1)
        self.map_zoom_min = self._map_entry(form, "Minimum zoom", "12", 2)
        self.map_zoom_max = self._map_entry(form, "Maximum zoom", "16", 3)
        self.map_status = ctk.CTkLabel(form, text="Ready", text_color="#9ca3af", font=("Segoe UI", 15))
        self.map_status.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=(4, 10))
        self.map_download_btn = ctk.CTkButton(form, text="Download offline area", command=self._start_map_download)
        self.map_download_btn.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        form.grid_columnconfigure(1, weight=1)

    @staticmethod
    def _map_entry(parent, label, value, row):
        ctk.CTkLabel(parent, text=label, font=("Segoe UI", 16)).grid(row=row, column=0, sticky="w", padx=20, pady=8)
        entry = ctk.CTkEntry(parent, width=260)
        entry.insert(0, value)
        entry.grid(row=row, column=1, sticky="ew", padx=(12, 20), pady=8)
        return entry

    def _set_offline_mode(self):
        if self.on_map_offline_change:
            self.on_map_offline_change(self.offline_var.get())

    @staticmethod
    def _parse_position(value):
        lat, lng = (float(part.strip()) for part in value.split(","))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("Coordinates are out of range.")
        return lat, lng

    def _start_map_download(self):
        try:
            top_left = self._parse_position(self.map_top_left.get())
            bottom_right = self._parse_position(self.map_bottom_right.get())
            zoom_min = int(self.map_zoom_min.get())
            zoom_max = int(self.map_zoom_max.get())
        except ValueError as exc:
            self.map_status.configure(text=f"Invalid input: {exc}", text_color="#ef4444")
            return

        self.map_download_btn.configure(state="disabled")
        self.map_status.configure(text="Downloading in background…", text_color="#facc15")

        def worker():
            try:
                from tools.offline_map import download_offline_area
                download_offline_area(top_left, bottom_right, zoom_min, zoom_max)
            except Exception as exc:
                self.after(0, lambda: self._finish_map_download(f"Download failed: {exc}", False))
            else:
                self.after(0, lambda: self._finish_map_download("Download completed. Offline mode enabled.", True))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_map_download(self, message, success):
        self.map_download_btn.configure(state="normal")
        self.map_status.configure(text=message, text_color="#22c55e" if success else "#ef4444")
        if success:
            self.offline_var.set(True)
            self._set_offline_mode()


    def _show_placeholder(self, key):
        self._clear_main()
        ctk.CTkLabel(self.main_frame, text=self._strings[key], font=("Segoe UI", 36, "bold"), text_color="#444444").place(relx=0.5, rely=0.5, anchor="center")

    def _change_language(self, lang):
        if lang == self.language: return
        self.language = lang
        if self.on_language_change: self.on_language_change(lang)

    def close_panel(self):
        self.place_forget()
