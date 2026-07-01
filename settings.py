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
        
        "map_dl_title": "Offline Map Downloader (Google Sat)",
        "map_dl_desc":  "Pan and zoom to your mission area, then click 'Select Current View'.",
        "map_dl_get":   "📍 Select Current View",
        "map_dl_tl":    "Top Left (Lat, Lng):",
        "map_dl_br":    "Bottom Right (Lat, Lng):",
        "map_dl_offline": "✔ Use ONLY Offline Map (Zero Lag)",
        "map_dl_btn":   "⬇ Download Map",
        "map_dl_wait":  "Status: Waiting",
        "map_dl_ing":   "Status: Downloading...",
        "map_dl_ok":    "Status: Success! Saved. You can use it instantly.",
        "map_dl_err":   "Status: Error!",
        "map_dl_inv":   "Status: Invalid coordinate format!"
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
        
        "map_dl_title": "Çevrimdışı Harita İndirici (Google Uydu)",
        "map_dl_desc":  "Haritayı görev yapacağınız bölgeye kaydırın ve 'Şu Anki Görünümü Seç'e tıklayın.",
        "map_dl_get":   "📍 Şu Anki Görünümü Seç",
        "map_dl_tl":    "Sol Üst (Lat, Lng):",
        "map_dl_br":    "Sağ Alt (Lat, Lng):",
        "map_dl_offline": "✔ SADECE Çevrimdışı (Offline) Haritayı Kullan",
        "map_dl_btn":   "⬇ Haritayı İndir",
        "map_dl_wait":  "Durum: Bekleniyor",
        "map_dl_ing":   "Durum: İndiriliyor...",
        "map_dl_ok":    "Durum: Başarılı! İndirildi, anında kullanabilirsiniz.",
        "map_dl_err":   "Durum: Hata oluştu!",
        "map_dl_inv":   "Durum: Geçersiz koordinat formatı!"
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
# HARİTA İNDİRİCİ ARAYÜZÜ
# ==========================================
class MapDownloaderFrame(ctk.CTkFrame):
    def __init__(self, master, language="Türkçe", **kwargs):
        super().__init__(master, fg_color="#1A1A1A", corner_radius=16, **kwargs)
        
        self.language = language
        self.selection_polygon = None 

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 0))
        
        self.title_lbl = ctk.CTkLabel(self.header_frame, text=self._s("map_dl_title"), font=("Segoe UI", 24, "bold"), text_color="#FFFFFF")
        self.title_lbl.pack(anchor="w")
        self.desc_lbl = ctk.CTkLabel(self.header_frame, text=self._s("map_dl_desc"), font=("Segoe UI", 16), text_color="#AAAAAA")
        self.desc_lbl.pack(anchor="w")

        # MAP WIDGET BAĞLANTISI (Aynı DB'yi kullanıyoruz ki senkronize olsun)
        save_dir = os.path.join(os.getcwd(), "data", "map")
        os.makedirs(save_dir, exist_ok=True)
        db_path = os.path.join(save_dir, "offline_map_data.db")

        self.map_widget = tkintermapview.TkinterMapView(self, corner_radius=12, database_path=db_path)
        self.map_widget.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", max_zoom=19)
        self.map_widget.set_position(41.0082, 28.9784) 
        self.map_widget.set_zoom(12)

        self.controls_frame = ctk.CTkFrame(self, fg_color="#242424", corner_radius=12)
        self.controls_frame.grid(row=1, column=1, padx=(10, 20), pady=20, sticky="n")

        self.get_view_btn = ctk.CTkButton(
            self.controls_frame, text=self._s("map_dl_get"), font=("Segoe UI", 16, "bold"),
            fg_color="#0088FF", hover_color="#0066CC", height=45, command=self.select_current_view
        )
        self.get_view_btn.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkFrame(self.controls_frame, height=2, fg_color="#3A3A3A").pack(fill="x", padx=20, pady=10)

        self.tl_label = ctk.CTkLabel(self.controls_frame, text=self._s("map_dl_tl"), font=("Segoe UI", 14))
        self.tl_label.pack(anchor="w", padx=20, pady=(5, 0))
        self.tl_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.tl_frame.pack(fill="x", padx=20)
        self.top_left_lat = ctk.CTkEntry(self.tl_frame, width=90, placeholder_text="Lat")
        self.top_left_lat.pack(side="left", padx=(0,5), pady=5)
        self.top_left_lng = ctk.CTkEntry(self.tl_frame, width=90, placeholder_text="Lng")
        self.top_left_lng.pack(side="left", padx=5, pady=5)

        self.br_label = ctk.CTkLabel(self.controls_frame, text=self._s("map_dl_br"), font=("Segoe UI", 14))
        self.br_label.pack(anchor="w", padx=20, pady=(15, 0))
        self.br_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.br_frame.pack(fill="x", padx=20)
        self.bot_right_lat = ctk.CTkEntry(self.br_frame, width=90, placeholder_text="Lat")
        self.bot_right_lat.pack(side="left", padx=(0,5), pady=5)
        self.bot_right_lng = ctk.CTkEntry(self.br_frame, width=90, placeholder_text="Lng")
        self.bot_right_lng.pack(side="left", padx=5, pady=5)

        ctk.CTkFrame(self.controls_frame, height=2, fg_color="#3A3A3A").pack(fill="x", padx=20, pady=(20,10))

        # SADECE OFFLINE CHECKBOX'I
        self.offline_var = ctk.BooleanVar(value=False)
        self.offline_cb = ctk.CTkCheckBox(
            self.controls_frame, text=self._s("map_dl_offline"), font=("Segoe UI", 14),
            variable=self.offline_var, command=self.toggle_offline
        )
        self.offline_cb.pack(padx=20, pady=(0, 15), anchor="w")

        self.download_btn = ctk.CTkButton(
            self.controls_frame, text=self._s("map_dl_btn"), font=("Segoe UI", 16, "bold"), height=45,
            fg_color="#00FFAA", text_color="#000000", hover_color="#00CC88", command=self.start_download
        )
        self.download_btn.pack(fill="x", padx=20, pady=(10, 5))

        self.status_lbl = ctk.CTkLabel(self.controls_frame, text=self._s("map_dl_wait"), font=("Segoe UI", 14), text_color="#888888")
        self.status_lbl.pack(padx=20, pady=(0, 20))

        self.top_left_lat.bind("<KeyRelease>", self.update_polygon_from_entry)
        self.top_left_lng.bind("<KeyRelease>", self.update_polygon_from_entry)
        self.bot_right_lat.bind("<KeyRelease>", self.update_polygon_from_entry)
        self.bot_right_lng.bind("<KeyRelease>", self.update_polygon_from_entry)

        # Başlangıçta ana penceredeki offline mod neyse onu Checkbox'a yansıt
        self.after(200, self.init_checkbox)

    def _s(self, key):
        return LANGUAGES[self.language][key]

    def init_checkbox(self):
        app = self.winfo_toplevel() # Ana NaviDeck penceresine erişim
        if hasattr(app, "minimap"):
            # Varsayılan durumu ana haritadan çek (Karma mod ise False gelir)
            self.offline_var.set(app.minimap.map_widget.use_database_only)
            self.map_widget.use_database_only = app.minimap.map_widget.use_database_only

    def toggle_offline(self):
        """Kullanıcı Karma veya Sadece Offline geçişi yapınca çalışır."""
        is_offline = self.offline_var.get()
        app = self.winfo_toplevel()
        if hasattr(app, "minimap"):
            app.minimap.set_offline_mode(is_offline) # Ana ekrandaki (MiniMap) modu değiştirir
        
        # Ayarlar sayfasındaki bu haritayı da aynı moda al
        self.map_widget.use_database_only = is_offline
        self.map_widget.set_zoom(self.map_widget.zoom)

    def select_current_view(self):
        tl_lat, tl_lng = self.map_widget.convert_canvas_coords_to_decimal_coords(0, 0)
        w, h = self.map_widget.winfo_width(), self.map_widget.winfo_height()
        br_lat, br_lng = self.map_widget.convert_canvas_coords_to_decimal_coords(w, h)

        self.top_left_lat.delete(0, 'end')
        self.top_left_lat.insert(0, f"{tl_lat:.6f}")
        self.top_left_lng.delete(0, 'end')
        self.top_left_lng.insert(0, f"{tl_lng:.6f}")
        self.bot_right_lat.delete(0, 'end')
        self.bot_right_lat.insert(0, f"{br_lat:.6f}")
        self.bot_right_lng.delete(0, 'end')
        self.bot_right_lng.insert(0, f"{br_lng:.6f}")

        self.draw_selection_box(tl_lat, tl_lng, br_lat, br_lng)

    def update_polygon_from_entry(self, event=None):
        try:
            tl_lat = float(self.top_left_lat.get())
            tl_lng = float(self.top_left_lng.get())
            br_lat = float(self.bot_right_lat.get())
            br_lng = float(self.bot_right_lng.get())
            self.draw_selection_box(tl_lat, tl_lng, br_lat, br_lng)
        except ValueError:
            pass 

    def draw_selection_box(self, tl_lat, tl_lng, br_lat, br_lng):
        if self.selection_polygon:
            self.selection_polygon.delete()
        path = [(tl_lat, tl_lng), (tl_lat, br_lng), (br_lat, br_lng), (br_lat, tl_lng)]
        self.selection_polygon = self.map_widget.set_polygon(path, outline_color="#FF0044", border_width=3, fill_color=None)

    def start_download(self):
        try:
            tl_lat = float(self.top_left_lat.get())
            tl_lng = float(self.top_left_lng.get())
            br_lat = float(self.bot_right_lat.get())
            br_lng = float(self.bot_right_lng.get())
            
            top_left = (tl_lat, tl_lng)
            bottom_right = (br_lat, br_lng)

            self.download_btn.configure(state="disabled")
            self.status_lbl.configure(text=self._s("map_dl_ing"), text_color="#FFAA00")

            threading.Thread(target=self.download_process, args=(top_left, bottom_right), daemon=True).start()

        except ValueError:
            self.status_lbl.configure(text=self._s("map_dl_inv"), text_color="#FF4444")

    def download_process(self, top_left, bottom_right):
        
        # Yüzdeyi/Durumu Güncelleyen Fonksiyon (Tkinter Main Thread'de çalıştırılır)
        def update_ui_status(text):
            self.status_lbl.after(0, lambda: self.status_lbl.configure(text=text, text_color="#FFAA00"))

        capture = PrintCapture(update_ui_status)
        sys.stdout = capture # Terminale yazılan her şeyi bizim yakalayıcıya yönlendir
        
        try:
            save_dir = os.path.join(os.getcwd(), "data", "map")
            db_path = os.path.join(save_dir, "offline_map_data.db")
            
            loader = tkintermapview.OfflineLoader(
                path=db_path,
                tile_server="https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
            )
            
            # İndirme İşlemi Başlıyor!
            loader.save_offline_tiles(top_left, bottom_right, 10, 16)
            
            # Bitti
            self.status_lbl.after(0, lambda: self.status_lbl.configure(text=self._s("map_dl_ok"), text_color="#00FFAA"))
        except Exception as e:
            print(f"Hata: {e}")
            self.status_lbl.after(0, lambda: self.status_lbl.configure(text=self._s("map_dl_err"), text_color="#FF4444"))
        finally:
            sys.stdout = capture.stdout # Print yakalamayı bırak, orjinaline dön
            self.download_btn.after(0, lambda: self.download_btn.configure(state="normal"))
            # MiniMap ve güncel haritayı yeniden çizmek için tetikle ki inenler anında görünsün
            self.after(0, lambda: self.map_widget.set_zoom(self.map_widget.zoom))
            app = self.winfo_toplevel()
            if hasattr(app, "minimap"):
                self.after(0, lambda: app.minimap.map_widget.set_zoom(app.minimap.map_widget.zoom))


# ==========================================
# ANA AYARLAR PANELİ
# ==========================================
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
        self._clear_main()
        self.map_downloader = MapDownloaderFrame(self.main_frame, language=self.language)
        self.map_downloader.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_placeholder(self, key):
        self._clear_main()
        ctk.CTkLabel(self.main_frame, text=self._strings[key], font=("Segoe UI", 36, "bold"), text_color="#444444").place(relx=0.5, rely=0.5, anchor="center")

    def _change_language(self, lang):
        if lang == self.language: return
        self.language = lang
        if self.on_language_change: self.on_language_change(lang)

    def close_panel(self):
        self.place_forget()