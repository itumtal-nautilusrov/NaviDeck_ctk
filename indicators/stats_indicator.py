import customtkinter as ctk

# ── Dot colors ──────────────────────────────────────────────────────
DOT_GREEN = "#22c55e"   # Normal / active
DOT_RED   = "#ef4444"   # Error / alert
DOT_GRAY  = "#4b5563"   # Inactive / no signal

# ── Label translations per language ──────────────────────────────────────────
LABEL_TRANSLATIONS = {
    "English": {
        "DEPHT":    "DEPHT",
        "VELOCITY": "VELOCITY",
        "YAW":      "YAW",
        "ROLL":     "ROLL",
        "PITCH":    "PITCH",
    },
    "Türkçe": {
        "DEPHT":    "DERİNLİK",
        "VELOCITY": "HIZ",
        "YAW":      "YAW",
        "ROLL":     "ROLL",
        "PITCH":    "PITCH",
    },
}


class StatsIndicator(ctk.CTkFrame):
    def __init__(
        self,
        master,
        label: str = "LABEL",
        value: float = 0.0,
        unit: str = "",
        dot_color: str = DOT_GREEN,
        width: int = 170,
        height: int = 64,
        language: str = "English",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="#1a1a1a",
            width=width,
            height=height,
            corner_radius=12,
            border_width=1,
            border_color="#303030",
            **kwargs
        )
        self.pack_propagate(False)

        self._original_label = label.upper()
        self._unit = unit
        self.language = language

        self._build_ui(dot_color, value, unit)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self, dot_color, value, unit):

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=14, pady=8)

        top_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        top_row.pack(fill="x")

        self._dot = ctk.CTkLabel(
            top_row,
            text="●",
            font=("Arial", 14),
            text_color=dot_color,
            fg_color="transparent",
        )
        self._dot.pack(side="left", padx=(0, 2))

        self._label_widget = ctk.CTkLabel(
            top_row,
            text=self._get_translated_label(),
            font=("Arial", 13, "bold"),
            text_color="#BBBBBB",
            fg_color="transparent",
            anchor="w",
        )
        self._label_widget.pack(side="left", padx=5)

        bottom_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(2, 0))

        self._value_widget = ctk.CTkLabel(
            bottom_row,
            text=self._format_value(value),
            font=("Courier New", 20, "bold"),
            text_color="#f0f0f0",
            fg_color="transparent",
            anchor="w",
        )
        self._value_widget.pack(side="left", padx=5)

        if unit:
            unit_font = ("Arial", 20) if unit == "°" else ("Arial", 12)

            self._unit_widget = ctk.CTkLabel(
                bottom_row,
                text=unit,
                font=unit_font,
                text_color="#ABABAB",
                fg_color="transparent",
                anchor="w",
            )
            self._unit_widget.pack(side="left", padx=(9, 0), pady=(4, 0))


    def _get_translated_label(self) -> str:
        lang_map = LABEL_TRANSLATIONS.get(self.language, {})
        return lang_map.get(self._original_label, self._original_label)


    def _format_value(self, value) -> str:
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return str(value)

    def set_value(self, value):
        self._value_widget.configure(text=self._format_value(value))

    def set_label(self, label: str):
        self._label_widget.configure(text=label.upper())

    def set_dot(self, color: str):
        self._dot.configure(text_color=color)

    def set_language(self, lang: str):
        self.language = lang
        self._label_widget.configure(text=self._get_translated_label())


# ── Quick demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import math

    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("StatsIndicator demo")
    app.geometry("220x460")
    app.configure(fg_color="#111111")

    sensor_configs = [
        ("YAW",      0.0,   "°",   DOT_GREEN),
        ("PITCH",    0.0,   "°",   DOT_GREEN),
        ("ROLL",     0.0,   "°",   DOT_GREEN),
        ("DEPHT",  120.0,   "m",   DOT_GRAY),
        ("VELOCITY", 0.0, "m/s",   DOT_RED),
    ]

    cards = []
    for label, value, unit, dot in sensor_configs:
        card = StatsIndicator(app, label=label, value=value, unit=unit, dot_color=dot)
        card.pack(anchor="center", pady=5)
        cards.append(card)

    t = 0.0

    def animate():
        global t
        t += 0.05
        cards[0].set_value(math.degrees(math.sin(t)) * 45)
        cards[1].set_value(math.degrees(math.cos(t * 0.7)) * 30)
        cards[2].set_value(math.degrees(math.sin(t * 1.3)) * 20)
        cards[3].set_value(120 + math.sin(t * 0.3) * 5)
        cards[4].set_value(abs(math.sin(t * 0.5)) * 18)
        app.after(50, animate)

    app.after(50, animate)
    app.mainloop()