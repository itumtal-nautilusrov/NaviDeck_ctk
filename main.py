import customtkinter as ctk
import ctypes
from PIL import Image
import cv2 as cv
import datetime
from indicators.battery_indicator import BatteryIndicator
from indicators.warning_indicator import WarningIndicator
from indicators.timer_indicator import TimerIndicator
from indicators.hud_indicator import HUDIndicator
from indicators.stats_indicator import StatsIndicator

from settings import SettingsPanel, LANGUAGES

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NaviDeck.app")


LANGUAGES["English"].update({
    "selected":    "Selected",
    "footage1":    "Footage 1\nN25",
    "footage2":    "Footage 2\nMini ROV",
})
LANGUAGES["Türkçe"].update({
    "selected":    "Seçili",
    "footage1":    "Görüntü 1\nN25",
    "footage2":    "Görüntü 2\nMini ROV",
})


class NaviDeck(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.language = "Türkçe"   # LANG

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
            self.top_bar,
            width=75,
            image=self.more_img,
            text="",
            fg_color="transparent",
            hover=False,
            command=self.open_settings
        )
        self.more_button.pack(side="right", padx=20, pady=20)
        self.more_button.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.more_button.bind("<Leave>", lambda e: self.config(cursor=""))

        ctk.CTkFrame(self.top_bar, fg_color="#393939", height=70, width=2).pack(side="right", padx=5, pady=22)

        self.battery = BatteryIndicator(
            self.top_bar,
            battery_percent=88,
            minutes_left=95,
            icons_dir="./_icons/main",
            language=self.language,
            fg_color="transparent",
            border_width=2,
            border_color="#3a3a3a",
            corner_radius=12,
        )
        self.battery.pack(side="right", anchor="center", padx=20, pady=22)

        self.warning = WarningIndicator(
            self.top_bar,
            warning_key="flawless",
            language=self.language,
            corner_radius=12
        )
        self.warning.pack(side="left", anchor="center", padx=20, pady=25)

# _____ MAIN FRAME ___________________________________

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

# _____ RIGHT BAR ___________________________________

        self.curr_footage = "N25"
        self.footage_buttons = {}

        self.right_bar = ctk.CTkFrame(self.main_frame, width=206, fg_color="#0f0f14", corner_radius=0)
        self.right_bar.pack(side="right", fill="y")
        self.right_bar.pack_propagate(False)

        ctk.CTkFrame(self.right_bar, fg_color="#393939", height=2, width=186).pack(side="top")

        self.clock_lbl = ctk.CTkLabel(self.right_bar, text="00:00", font=("Arial", 27, "bold"))
        self.clock_lbl.pack(side="top", pady=10)

        self.timer = TimerIndicator(
            self.right_bar,
            language=self.language,
            corner_radius=0,
            border_width=0,
            border_color="#393939",
            fg_color="transparent"
        )
        self.timer.pack(side="top", pady=10)

        ctk.CTkFrame(self.right_bar, fg_color="#393939", height=2, width=186).pack(side="top", pady=5)        

        # Mini ROV
        self.footage_btn2 = ctk.CTkButton(
            self.right_bar,
            text=self._s("footage2"),
            font=("Arial", 20, "bold"),
            fg_color="#171616",
            hover=False,
            width=186, height=120,
            corner_radius=10,
            border_width=3,
            border_color="#00FFAA" if self.curr_footage == "Mini ROV" else "#393939",
            command=lambda: self.select_footage("Mini ROV")
        )
        self.footage_btn2.pack(side="bottom", pady=15)

        # N25
        self.footage_btn1 = ctk.CTkButton(
            self.right_bar,
            text=self._s("footage1"),
            font=("Arial", 20, "bold"),
            fg_color="#171616",
            hover=False,
            width=186, height=120,
            corner_radius=10,
            border_width=3,
            border_color="#00FFAA" if self.curr_footage == "N25" else "#393939",
            command=lambda: self.select_footage("N25")
        )
        self.footage_btn1.pack(side="bottom", pady=7)

        self.footage_lbl = ctk.CTkLabel(
            self.right_bar,
            text=f"{self._s('selected')}: {self.curr_footage}",
            font=("Arial", 20, "bold")
        )
        self.footage_lbl.pack(side="bottom", pady=7, padx=10, anchor="w")

        self.footage_buttons["Mini ROV"] = self.footage_btn2
        self.footage_buttons["N25"]      = self.footage_btn1

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

# _____ CAM FRAME ___________________________________

        self.cam_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cam_frame.pack(side="left", fill="both", expand=True)

        self.no_cam_img = ctk.CTkImage(
            light_image=Image.open("./_icons/main/nocam.png"),
            size=(350, 350)
        )

        self.cam_label = ctk.CTkLabel(
            self.cam_frame, text="",
            bg_color="transparent", fg_color="transparent"
        )
        self.cam_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.cam_running = True

        if not self.cam_running:
            self.cam_label.configure(image=self.no_cam_img)
        else:
            frame = cv.imread("./_footage/3.webp")
            self.after(50, lambda: self.update_footage(frame))

# _____ LAST CALLS ___________________________________

        self.update_clock()
        self.control_warnings()

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

        self.footage_btn1.configure(text=self._s("footage1"))
        self.footage_btn2.configure(text=self._s("footage2"))
        self.footage_lbl.configure(text=f"{self._s('selected')}: {self.curr_footage}")

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
                on_language_change=self.apply_language
            )

        self.settings_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self.settings_panel.lift()

    # ─── Footage ─────────────────────────────────────────────────────────────

    def select_footage(self, name):
        if not hasattr(self, "footage_lbl"):
            return
        self.curr_footage = name
        self.footage_lbl.configure(text=f"{self._s('selected')}: {self.curr_footage}")
        for key, btn in self.footage_buttons.items():
            btn.configure(border_color="#00FFAA" if key == name else "#393939")

    # ─── Camera ──────────────────────────────────────────────────────────────

    def update_footage(self, frame):
        if frame is None:
            print("Frame okunamadı.")
            return

        frame_h, frame_w = frame.shape[:2]
        display_w = self.cam_frame.winfo_width()
        display_h = self.cam_frame.winfo_height()

        if display_w < 10 or display_h < 10:
            self.after(50, lambda: self.update_footage(frame))
            return

        # 1) Önce frame'i resize et
        scale = min(display_w / frame_w, display_h / frame_h)
        new_w = int(frame_w * scale)
        new_h = int(frame_h * scale)

        resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)

        # 2) Sonra HUD'u resize edilmiş frame üzerine çiz
        resized = self.stats.draw_roll(resized, self.roll)

        resized = cv.cvtColor(resized, cv.COLOR_BGR2RGB)
        img     = Image.fromarray(resized)
        ctk_img = ctk.CTkImage(light_image=img, size=(new_w, new_h))

        self.cam_label.configure(image=ctk_img)
        self.cam_label.image = ctk_img

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