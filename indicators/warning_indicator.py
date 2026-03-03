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

FLASH_ON  = "#c31212"
FLASH_OFF = "#6b0000"


class WarningIndicator(ctk.CTkFrame):
    def __init__(
        self,
        master,
        text="Warning",
        level=2,
        sound="./_sounds/warning.mp3",
        **kwargs,
    ):
        kwargs.setdefault("width", 340)
        kwargs.setdefault("height", 65)
        kwargs.setdefault("corner_radius", 6)
        super().__init__(master, **kwargs)
        self.grid_propagate(False)
        self.pack_propagate(False)

        self.text  = text
        self.level = level
        self.sound = sound

        self._flashing    = False
        self._flash_state = True
        self._flash_job   = None
        self._sound_thread = None

        self._build()
        self.update(text, level)

    # ── public ────────────────────────────────────────────────────────────────

    def set_warning(self, text, level):
        self.update(text, level)

    def update(self, text=None, level=None):
        if text is not None:
            self.text = text
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
        col = 0
        self.text_lbl.grid(row=0, column=col, padx=10, sticky="ew")

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

    # ── Flash ──────────────────────────────────────────────────────────────────

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

    # ── Sound ──────────────────────────────────────────────────────────────────

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
                # Windows
                if sys.platform == "win32":
                    import winsound
                    winsound.PlaySound(self.sound, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                # Linux
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["aplay", "-l", self.sound],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # macOS
                elif sys.platform == "darwin":
                    subprocess.Popen(["afplay", "-t", "0", self.sound])
        except Exception as e:
            print(f"[WarningIndicator] Ses çalınamadı: {e}")


# ── Demo ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("Warning Indicator Demo")
    app.geometry("420x280")

    frame = ctk.CTkFrame(app)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    w1 = WarningIndicator(frame, text="All systems nominal.", level=1)
    w1.pack(pady=8)

    w2 = WarningIndicator(frame, text="Heavy Wind Velocity. Fly with caution.", level=2)
    w2.pack(pady=8)

    w3 = WarningIndicator(frame, text="CRITICAL: Return to home immediately!", level=3)
    w3.pack(pady=8)

    def cycle():
        current = w2.level
        w2.update(level=(current % 3) + 1)

    ctk.CTkButton(frame, text="Cycle Level (w2)", command=cycle).pack(pady=8)

    app.mainloop()