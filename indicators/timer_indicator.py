import customtkinter as ctk
from datetime import datetime, timedelta


TIMER_STRINGS = {
    "English": {
        "start": "START",
        "stop":  "STOP",
        "reset": "RESET",
    },
    "Türkçe": {
        "start": "BAŞLAT",
        "stop":  "DURDUR",
        "reset": "SIFIRLA",
    },
}


class TimerIndicator(ctk.CTkFrame):
    def __init__(self, master, language="English", **kwargs):
        super().__init__(master, width=270, height=155, **kwargs)
        self.pack_propagate(False)

        self.language  = language
        self.running   = False
        self.start_time = None
        self.elapsed   = timedelta(0)
        self.after_id  = None

        self._build_ui()

    # ── public ────────────────────────────────

    def set_language(self, language):
        self.language = language
        s = TIMER_STRINGS[language]
        
        if self.running:
            self.control_button.configure(text=s["stop"])
        else:
            self.control_button.configure(text=s["start"])
        self.reset_button.configure(text=s["reset"])

    # ── private ───────────────────────────────

    def _s(self, key):
        return TIMER_STRINGS[self.language][key]

    def _build_ui(self):
        self.timer_label = ctk.CTkLabel(
            self,
            text="00:00,00",
            font=("Arial", 24, "bold")
        )
        self.timer_label.pack(pady=(20, 10))

        self.control_button = ctk.CTkButton(
            self,
            text=self._s("start"),
            font=("Arial", 17, "bold"),
            width=150,
            height=35,
            fg_color="#00AA55",
            hover_color="#008844",
            command=self.toggle_timer
        )
        self.control_button.pack(pady=5)

        self.reset_button = ctk.CTkButton(
            self,
            text=self._s("reset"),
            font=("Arial", 17, "bold"),
            width=150,
            height=35,
            fg_color="#444444",
            hover_color="#333333",
            command=self.reset_timer
        )
        self.reset_button.pack(pady=(0, 15))

    def toggle_timer(self):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.running    = True
        self.start_time = datetime.now()
        self.control_button.configure(
            text=self._s("stop"),
            fg_color="#AA0000",
            hover_color="#880000"
        )
        self._update_timer()

    def stop_timer(self):
        self.running = False
        if self.start_time:
            self.elapsed += datetime.now() - self.start_time
        if self.after_id:
            self.after_cancel(self.after_id)
        self.control_button.configure(
            text=self._s("start"),
            fg_color="#00AA55",
            hover_color="#008844"
        )

    def reset_timer(self):
        self.running    = False
        self.start_time = None
        self.elapsed    = timedelta(0)
        if self.after_id:
            self.after_cancel(self.after_id)
        self.timer_label.configure(text="00:00,00")
        self.control_button.configure(
            text=self._s("start"),
            fg_color="#00AA55",
            hover_color="#008844"
        )

    def _update_timer(self):
        if not self.running:
            return
        current_elapsed = self.elapsed + (datetime.now() - self.start_time)
        total_seconds   = current_elapsed.total_seconds()
        minutes         = int(total_seconds // 60)
        seconds         = int(total_seconds % 60)
        centiseconds    = int((total_seconds * 100) % 100)
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d},{centiseconds:02d}")
        self.after_id = self.after(50, self._update_timer)