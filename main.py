import sys
import json
import customtkinter as ctk
import ctypes
from PIL import Image
import cv2 as cv
import datetime
from threading import Thread

from indicators.battery_indicator import BatteryIndicator
from indicators.warning_indicator import WarningIndicator
from indicators.timer_indicator import TimerIndicator
from indicators.hud_indicator import HUDIndicator
from indicators.stats_indicator import StatsIndicator
from indicators.cam_indicator import CameraSelector
from indicators.map_indicator import MiniMapIndicator
from indicators.temp_stack_indicator import TempStackIndicator

from client.ui_handler import UIHandler
from client.main_client import TelemetryClient
from client.serial_handler import SerialHandler
from settings import SettingsPanel, LANGUAGES

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NaviDeck.app")

LANGUAGES["English"].update({
    "selected":    "Selected",
    "map_dl_title": "Offline Map Downloader (Google Sat)",
    "map_dl_tl":    "Top Left (Lat, Lng):",
    "map_dl_br":    "Bottom Right (Lat, Lng):",
    "map_dl_btn":   "Download Map",
    "map_dl_wait":  "Status: Waiting",
    "map_dl_ing":   "Status: Downloading... (No lag)",
    "map_dl_ok":    "Status: Success! Saved.",
    "map_dl_err":   "Status: Error!",
    "map_dl_inv":   "Status: Invalid numbers!"
})

LANGUAGES["Türkçe"].update({
    "selected":    "Seçili",
    "map_dl_title": "Çevrimdışı Harita İndirici (Google Uydu)",
    "map_dl_tl":    "Sol Üst (Lat, Lng):",
    "map_dl_br":    "Sağ Alt (Lat, Lng):",
    "map_dl_btn":   "Haritayı İndir",
    "map_dl_wait":  "Durum: Bekleniyor",
    "map_dl_ing":   "Durum: İndiriliyor... (Arayüz kasmaz)",
    "map_dl_ok":    "Durum: Başarılı! Kaydedildi.",
    "map_dl_err":   "Durum: Hata oluştu!",
    "map_dl_inv":   "Durum: Geçersiz sayı formatı!"
})


class NaviDeck(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.language = "Türkçe"   # LANG
        self.cams = ["Sarıca", "Mini ROV"]
        self.curr_footage = self.cams[0]

        self.iconbitmap("./_icons/main/nrt_logo.ico")
        self.title("NaviDeck")
        self.geometry("1920x1080")
        self.attributes("-fullscreen", True)

        self.stats = HUDIndicator()
        self.coords = 0
        self.depht = 0
        self.velocity = 0
        self.yaw = 0
        self.roll  = -3
        self.pitch = 0

# _____ TOP BAR ___________________________________

        self.top_bar = ctk.CTkFrame(self, height=115, fg_color="#0f0f14", corner_radius=0)
        self.top_bar.pack(anchor="n", fill="x")

        self.more_img = ctk.CTkImage(
            light_image=Image.open("./_icons/main/more.png"),
            size=(60, 60)
        )

        self.more_button = ctk.CTkButton(
            self.top_bar, width=75, image=self.more_img, text="",
            fg_color="transparent", hover=False, command=self.open_settings
        )
        self.more_button.pack(side="right", padx=20, pady=20)
        self.more_button.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.more_button.bind("<Leave>", lambda e: self.config(cursor=""))

        ctk.CTkFrame(self.top_bar, fg_color="#393939", height=70, width=2).pack(side="right", padx=5, pady=22)

        self.battery = BatteryIndicator(
            self.top_bar, battery_percent=88, minutes_left=95,
            icons_dir="./_icons/main", language=self.language,
            fg_color="transparent", border_width=2, border_color="#3a3a3a", corner_radius=12
        )
        self.battery.pack(side="right", anchor="center", padx=20, pady=22)

        self.warning = WarningIndicator(
            self.top_bar, warning_key="flawless", language=self.language, corner_radius=12
        )
        self.warning.pack(side="left", anchor="center", padx=20, pady=25)

# _____ MAIN FRAME ___________________________________

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

# _____ RIGHT BAR ___________________________________

        self.right_bar = ctk.CTkFrame(self.main_frame, width=258, fg_color="#0f0f14", corner_radius=0)
        self.right_bar.pack(side="right", fill="y")
        self.right_bar.pack_propagate(False)

        ctk.CTkFrame(self.right_bar, fg_color="#393939", height=2, width=186).pack(side="top")

        self.clock_lbl = ctk.CTkLabel(self.right_bar, text="00:00", font=("Arial", 27, "bold"))
        self.clock_lbl.pack(side="top", pady=10)

        self.timer = TimerIndicator(
            self.right_bar, language=self.language, corner_radius=0,
            border_width=0, border_color="#393939", fg_color="transparent"
        )
        self.timer.pack(side="top", pady=10)

        ctk.CTkFrame(self.right_bar, fg_color="#393939", height=2, width=186).pack(side="top", pady=5)        
        ctk.CTkFrame(self.right_bar, fg_color="#393939", width=186, height=2).pack(side="bottom", pady=5)

        self.velocity_card = StatsIndicator(self.right_bar, label="VELOCITY", value=self.velocity, unit="m/s", language=self.language)
        self.velocity_card.pack(anchor="center", pady=9)

        self.depht_card = StatsIndicator(self.right_bar, label="DEPHT", value=self.depht, unit="m", language=self.language)
        self.depht_card.pack(anchor="center", pady=5)

        self.yaw_card = StatsIndicator(self.right_bar, label="YAW", value=self.yaw, unit="°", language=self.language)
        self.yaw_card.pack(anchor="center", pady=5)

        self.roll_card = StatsIndicator(self.right_bar, label="ROLL", value=self.roll, unit="°", language=self.language)
        self.roll_card.pack(anchor="center", pady=5)

        self.pitch_card = StatsIndicator(self.right_bar, label="PITCH", value=self.pitch, unit="°", language=self.language)
        self.pitch_card.pack(anchor="center", pady=5)

        self.log_frame = ctk.CTkFrame(self.right_bar, fg_color="#121218", corner_radius=12)
        self.log_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 12))

        self.log_title = ctk.CTkLabel(self.log_frame, text="CONNECTION LOG", font=("Segoe UI", 14, "bold"), text_color="#9ca3af")
        self.log_title.pack(anchor="w", padx=10, pady=(8, 4))

        self.log_box = ctk.CTkTextbox(
            self.log_frame,
            fg_color="#09090d",
            text_color="#d1d5db",
            border_width=1,
            border_color="#2b2b35",
            corner_radius=10,
            wrap="word",
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.log_box.configure(state="disabled")

        self.server_ctl_row = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        self.server_ctl_row.pack(fill="x", padx=8, pady=(0, 8))

        self.server_connected = True

        self.server_toggle_btn = ctk.CTkButton(
            self.server_ctl_row,
            text="Connect",
            height=32,
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            command=self.toggle_server_connection,
        )
        self.server_toggle_btn.pack(side="left", fill="x", expand=True)

# _____ CAM FRAME ___________________________________

        self.cam_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cam_frame.pack(side="left", fill="both", expand=True)

        self.no_cam_img = ctk.CTkImage(
            light_image=Image.open("./_icons/main/nocam.png"), size=(350, 350)
        )

        self.cam_label = ctk.CTkLabel(self.cam_frame, text="", bg_color="transparent", fg_color="transparent")
        self.cam_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.cam_running = True

        if not self.cam_running:
            self.cam_label.configure(image=self.no_cam_img)
        else:
            frame = cv.imread("./_footage/3.webp")
            self.after(50, lambda: self.update_footage(frame))

        self.minimap = MiniMapIndicator(
            self.cam_frame,
            on_waypoints_changed=self.handle_waypoints_changed,
        )
        self.minimap.place(relx=0.99, rely=0.99, anchor="se", x=-10, y=-10)

        # Kamera değişim fonksiyonunu direkt on_change parametresi ile bağlıyoruz
        self.cam_selector = CameraSelector(
            self.cam_frame,
            cameras=self.cams,
            on_change=self.handle_camera_change 
        )
        self.cam_selector.place(relx=0.99, rely=0.99, anchor="ne", x=-270, y=-260)

        self.temp_stack = TempStackIndicator(self.cam_frame, language=self.language)
        self.temp_stack.place(relx=0.99, rely=0.99, anchor="se", x=-270, y=-10)

# _____ UI CMD _______________________________________

        self.ui = UIHandler(logger=self.log_message)
        self.serial_handler = SerialHandler()
        self.serial_connection = self.serial_handler.get_serial_connection()
        self.telemetry_client = TelemetryClient(on_sample=self.handle_telemetry_sample, log=self.log_message)

        Thread(target=self.telemetry_client.run, daemon=True).start()
        
        self.ui.ui_command(f"footage {self.curr_footage}")
        self.send_waypoints("sync")
        print(f"UI cmd sent: {self.ui.ui_cmd}")
        print(f"Serial connection: {self.serial_connection.port if self.serial_connection else 'None'}")

# _____ KEYBINDS _____________________________________

        self.bind("<Escape>", self.close_settings)

# _____ LAST CALLS ___________________________________

        self.update_clock()
        self.control_warnings()
        self._refresh_ui_labels()

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def _s(self, key):
        return LANGUAGES[self.language][key]

    # ─── Language ────────────────────────────────────────────────────────────

    def apply_language(self, lang):
        self.language = lang
        self._refresh_ui_labels()

        if hasattr(self, "settings_panel") and self.settings_panel.winfo_exists():
            self.settings_panel.destroy()
        self.open_settings()

    def _refresh_ui_labels(self):
        print(f"Refreshing UI with language: {self.language}")
        self.warning.set_language(self.language)
        self.battery.set_language(self.language)
        self.timer.set_language(self.language)
        self.temp_stack.set_language(self.language)
        self.log_title.configure(text=self._s("connection_log_title"))
        self._refresh_server_toggle_btn()

        all_cards = [self.velocity_card, self.depht_card, self.yaw_card, self.roll_card, self.pitch_card]
        for card in all_cards:
            card.set_language(self.language)

    # ─── Warning ────────────────────────────────────────────────────────────

    def control_warnings(self):
        if self.battery.percent <= 25:
            self.warning.set_warning("low_battery")
       
    # ─── Settings ────────────────────────────────────────────────────────────

    def open_settings(self):
        if not hasattr(self, "settings_panel") or not self.settings_panel.winfo_exists():
            self.settings_panel = SettingsPanel(
                self,
                language=self.language,
                on_language_change=self.apply_language,
                on_map_offline_change=self.set_map_offline_mode,
            )

        self.settings_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self.settings_panel.lift()

    def close_settings(self, event=None):
        if hasattr(self, "settings_panel") and self.settings_panel.winfo_exists():
            self.settings_panel.destroy()

    def set_map_offline_mode(self, enabled):
        self.minimap.set_offline_mode(enabled)
        self.log_message(f"[MAP] offline mode {'enabled' if enabled else 'disabled'}")

    # ─── Camera ──────────────────────────────────────────────────────────────

    def update_footage(self, frame, mode="fit"):
        if frame is None:
            print("Frame okunamadı.")
            return

        frame_h, frame_w = frame.shape[:2]
        display_w = self.cam_frame.winfo_width()
        display_h = self.cam_frame.winfo_height()

        if display_w < 10 or display_h < 10:
            self.after(50, lambda: self.update_footage(frame, mode))
            return

        if mode == "fit":
            scale = min(display_w / frame_w, display_h / frame_h)
            new_w = int(frame_w * scale)
            new_h = int(frame_h * scale)
            resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)

        elif mode == "fill":
            scale = max(display_w / frame_w, display_h / frame_h)
            new_w = int(frame_w * scale)
            new_h = int(frame_h * scale)
            resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)
            
            start_y = (new_h - display_h) // 2
            start_x = (new_w - display_w) // 2
            resized = resized[start_y:start_y + display_h, start_x:start_x + display_w]
            new_w, new_h = display_w, display_h
        else:
            resized = frame 

        if hasattr(self.stats, 'draw_roll'):
            resized = self.stats.draw_roll(resized, self.roll)

        resized_rgb = cv.cvtColor(resized, cv.COLOR_BGR2RGB)
        img = Image.fromarray(resized_rgb)
        
        ctk_img = ctk.CTkImage(light_image=img, size=(new_w, new_h))
        self.cam_label.configure(image=ctk_img)
        self.cam_label.image = ctk_img 

    def handle_camera_change(self, cam: str):
        self.curr_footage = cam
        self.ui.ui_command(f"footage {cam}")
        print(f"UI cmd sent: {self.ui.ui_cmd}")

    # ─── Map / route commands ────────────────────────────────────────────

    def handle_waypoints_changed(self, action, waypoints):
        """Receive map changes and forward the complete route to the command socket."""
        self.send_waypoints(action, waypoints)

    def send_waypoints(self, action="sync", waypoints=None):
        """Send a newline-delimited UI command understood by the command server.

        The payload is a complete route snapshot, so a reconnect or a dropped
        individual update cannot leave the remote side with stale waypoints.
        """
        if waypoints is None:
            waypoints = [
                {"number": index + 1, "lat": waypoint["lat"], "lng": waypoint["lng"]}
                for index, waypoint in enumerate(self.minimap.waypoint_data)
            ]

        payload = json.dumps(
            {"action": action, "waypoints": waypoints},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        self.ui.ui_command(f"waypoints {payload}")

    def connect_server(self):
        self.ui.set_enabled(True)
        self.telemetry_client.set_enabled(True)
        if self.ui.connect():
            self.log_message("[UI] manual connect OK")
            self.ui.ui_command(f"footage {self.curr_footage}")
            self.send_waypoints("sync")
            self.server_connected = True
        else:
            self.log_message("[UI] manual connect failed")
            self.server_connected = False

        self._refresh_server_toggle_btn()

    def disconnect_server(self):
        self.ui.set_enabled(False)
        self.ui.close()
        self.telemetry_client.set_enabled(False)
        self.log_message("[UI] manually disconnected")
        self.server_connected = False
        self._refresh_server_toggle_btn()

    def toggle_server_connection(self):
        if self.server_connected:
            self.disconnect_server()
        else:
            self.connect_server()

    def _refresh_server_toggle_btn(self):
        if self.server_connected:
            self.server_toggle_btn.configure(
                text=self._s("server_disconnect"),
                fg_color="#374151",
                hover_color="#1f2937",
            )
        else:
            self.server_toggle_btn.configure(
                text=self._s("server_connect"),
                fg_color="#0ea5e9",
                hover_color="#0284c7",
            )

    def handle_telemetry_sample(self, sample):
        def apply_sample():
            self.depht_card.set_value(sample.get("depth", sample.get("pressure", 0)))
            self.velocity_card.set_value(sample.get("velocity", 0))
            self.yaw_card.set_value(sample.get("yaw", 0))
            self.roll_card.set_value(sample.get("roll", 0))
            self.pitch_card.set_value(sample.get("pitch", 0))
            self.temp_stack.set_values(
                sample.get("temp_electroic", sample.get("temp_electroics", 0)),
                sample.get("temp_battery", 0),
            )
            self.battery.set_percent(sample.get("battery_percent", self.battery.percent))

        if self.winfo_exists():
            self.after(0, apply_sample)

    def log_message(self, message):
        if not self.winfo_exists() or not hasattr(self, "log_box"):
            return

        def append():
            if not self.winfo_exists() or not hasattr(self, "log_box"):
                return

            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")

            lines = self.log_box.get("1.0", "end-1c").splitlines()
            if len(lines) > 200:
                keep_from = len(lines) - 200 + 1
                self.log_box.delete("1.0", f"{keep_from}.0")

            self.log_box.configure(state="disabled")

        self.after(0, append)

    # ─── Clock ───────────────────────────────────────────────────────────────

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M")
        self.clock_lbl.configure(text=now)
        self.after(600, self.update_clock)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = NaviDeck()
    app.run()
