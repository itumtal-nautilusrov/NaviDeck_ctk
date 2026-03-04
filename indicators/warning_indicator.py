import customtkinter as ctk
from PIL import Image
import os
import threading

try:
    import pygame
    pygame.mixer.init()
    _PYGAME = True
except ImportError:
    _PYGAME = False
    import subprocess, sys

COLOR = {
    1: "#2DDE3C",  # green
    2: "#d17e17",  # orange
    3: "#c31212",  # red
}

# ── Warning messages ──────────────────────────────────────────────────────────
WARNINGS = {
    # level 1
    "flawless":         (1, "Flawless",                    "Kusursuz"),
    "autonomous":       (1, "Autonomous mode",             "Otonom mod"),
    # level 2
    "low_battery":      (2, "Battery charge under 25%",    "Batarya şarjı %25'in altında"),
    "imu_not_cal":      (2, "IMU is not calibrated",       "IMU kalibre edilmedi"),
    # level 3
    "water_leak":       (3, "WATER LEAKING",               "SU SIZINTISI"),
}
# (level, english_text, turkish_text)


FLASH_ON  = "#c31212"
FLASH_OFF = "#6b0000"


class WarningIndicator(ctk.CTkFrame):
    def __init__(
        self,
        master,
        warning_key=None,
        text="Warning",
        level=2,
        language="English",
        sound="./_sounds/warning.mp3",
        **kwargs,
    ):
        kwargs.setdefault("width", 340)
        kwargs.setdefault("height", 65)
        kwargs.setdefault("corner_radius", 6)
        super().__init__(master, **kwargs)
        self.grid_propagate(False)
        self.pack_propagate(False)

        self.language     = language
        self.warning_key  = warning_key
        self.sound        = sound

        self._flashing     = False
        self._flash_state  = True
        self._flash_job    = None
        self._sound_thread = None

        if warning_key and warning_key in WARNINGS:
            lvl, en, tr = WARNINGS[warning_key]
            self.level = lvl
            self.text  = en if language == "English" else tr
        else:
            self.text  = text
            self.level = level

        self._build()
        self._refresh()

    # ── public ────────────────────────────────────────────────────────────────

    def set_language(self, language):
        self.language = language
        if self.warning_key and self.warning_key in WARNINGS:
            lvl, en, tr = WARNINGS[self.warning_key]
            self.text = en if language == "English" else tr
            self.text_lbl.configure(text=self.text)

    def set_warning(self, warning_key):
        if warning_key not in WARNINGS:
            return
        self.warning_key = warning_key
        lvl, en, tr = WARNINGS[warning_key]
        self.level = lvl
        self.text  = en if self.language == "English" else tr
        self.text_lbl.configure(text=self.text)
        self._refresh()

    def update(self, text=None, level=None):
        if text is not None:
            self.text = text
            self.warning_key = None
        if level is not None:
            self.level = max(1, min(3, int(level)))
        self.text_lbl.configure(text=self.text)
        self._refresh()

    # ── private ───────────────────────────────────────────────────────────────

    def _color(self):
        return COLOR.get(self.level, COLOR[2])

    def _build(self):
        self.grid_columnconfigure(0, minsize=48)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.badge = ctk.CTkFrame(self, width=48, corner_radius=10)
        self.badge.grid(row=0, column=0, padx=(6, 0), pady=3)
        self.badge.grid_propagate(False)
        self.badge.grid_rowconfigure(0, weight=1)
        self.badge.grid_columnconfigure(0, weight=1)

        self.level_lbl = ctk.CTkLabel(
            self.badge,
            text=str(self.level),
            font=("Arial", 16, "bold"),
            text_color="white",
            corner_radius=10
        )
        self.level_lbl.grid(row=0, column=0)

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=6, pady=3)
        right.grid_columnconfigure(1, weight=1)
        right.grid_rowconfigure(0, weight=1)

        self.text_lbl = ctk.CTkLabel(
            right,
            text=self.text,
            font=("Arial", 17, "bold"),
            text_color="white",
            anchor="w",
            wraplength=240,
        )
        self.text_lbl.grid(row=0, column=0, padx=10, sticky="ew")

    def _refresh(self):
        color = self._color()
        self.configure(fg_color=color)
        self.badge.configure(fg_color=self._darken(color))
        self.level_lbl.configure(text=str(self.level))

        if self.level == 3:
            self._start_flash()
            self._play_sound()
        else:
            self._stop_flash()

    def _darken(self, hex_color: str) -> str:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r, g, b = int(r * 0.7), int(g * 0.7), int(b * 0.7)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Flash ─────────────────────────────────────────────────────────────────

    def _start_flash(self):
        if not self._flashing:
            self._flashing = True
            self._do_flash()

    def _stop_flash(self):
        self._flashing = False
        if self._flash_job:
            self.after_cancel(self._flash_job)
            self._flash_job = None

    def _do_flash(self):
        if not self._flashing:
            return
        if self._flash_state:
            self.configure(fg_color=FLASH_ON)
            self.badge.configure(fg_color=self._darken(FLASH_ON))
        else:
            self.configure(fg_color=FLASH_OFF)
            self.badge.configure(fg_color=self._darken(FLASH_OFF))
        self._flash_state = not self._flash_state
        self._flash_job = self.after(400, self._do_flash)

    # ── Sound ─────────────────────────────────────────────────────────────────

    def _play_sound(self):
        if not os.path.exists(self.sound):
            return
        if self._sound_thread and self._sound_thread.is_alive():
            return
        self._sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self._sound_thread.start()

    def _sound_worker(self):
        try:
            if _PYGAME:
                pygame.mixer.music.load(self.sound)
                pygame.mixer.music.play(-1)
            else:
                if sys.platform == "win32":
                    import winsound
                    winsound.PlaySound(self.sound, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["aplay", "-l", self.sound],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif sys.platform == "darwin":
                    subprocess.Popen(["afplay", "-t", "0", self.sound])
        except Exception as e:
            print(f"[WarningIndicator] Ses çalınamadı: {e}")


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("Warning Indicator Demo")
    app.geometry("420x340")

    frame = ctk.CTkFrame(app)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    lang = "English"

    w1 = WarningIndicator(frame, warning_key="flawless",   language=lang)
    w1.pack(pady=8)

    w2 = WarningIndicator(frame, warning_key="low_battery", language=lang)
    w2.pack(pady=8)

    w3 = WarningIndicator(frame, warning_key="water_leak",  language=lang)
    w3.pack(pady=8)

    def toggle_lang():
        global lang
        lang = "Türkçe" if lang == "English" else "English"
        for w in (w1, w2, w3):
            w.set_language(lang)

    ctk.CTkButton(frame, text="Toggle Language", command=toggle_lang).pack(pady=8)

    def cycle():
        keys = list(WARNINGS.keys())
        idx  = keys.index(w2.warning_key) if w2.warning_key in keys else 0
        w2.set_warning(keys[(idx + 1) % len(keys)])

    ctk.CTkButton(frame, text="Cycle Warning (w2)", command=cycle).pack(pady=4)

    app.mainloop()