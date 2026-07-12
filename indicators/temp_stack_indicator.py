import customtkinter as ctk


class TempStackIndicator(ctk.CTkFrame):
    def __init__(self, master, language="English", width=170, row_height=34, **kwargs):
        self.gap = 2
        total_height = (row_height * 2) + self.gap
        super().__init__(
            master,
            fg_color="transparent",
            bg_color="transparent",
            width=width,
            height=total_height,
            **kwargs,
        )
        self.language = language
        self.row_height = row_height
        self.pack_propagate(False)

        self.electronic_value = 0.0
        self.battery_value = 0.0

        self._build_ui(width)
        self._refresh_labels()

    def _build_ui(self, width):
        self.electronic_box = ctk.CTkFrame(
            self,
            width=width,
            height=self.row_height,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#303030",
            corner_radius=10,
        )
        self.electronic_box.pack(fill="x", pady=(0, self.gap))
        self.electronic_box.pack_propagate(False)
        self.electronic_box.grid_columnconfigure(0, weight=1)
        self.electronic_box.grid_columnconfigure(1, weight=0)

        self.electronic_title_lbl = ctk.CTkLabel(
            self.electronic_box,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#cbd5e1",
            anchor="w",
        )
        self.electronic_title_lbl.grid(row=0, column=0, sticky="w", padx=(10, 4))

        self.electronic_value_lbl = ctk.CTkLabel(
            self.electronic_box,
            text="",
            font=("Courier New", 12, "bold"),
            text_color="#cbd5e1",
            anchor="e",
        )
        self.electronic_value_lbl.grid(row=0, column=1, sticky="e", padx=(4, 10))

        self.battery_box = ctk.CTkFrame(
            self,
            width=width,
            height=self.row_height,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#303030",
            corner_radius=10,
        )
        self.battery_box.pack(fill="x")
        self.battery_box.pack_propagate(False)
        self.battery_box.grid_columnconfigure(0, weight=1)
        self.battery_box.grid_columnconfigure(1, weight=0)

        self.battery_title_lbl = ctk.CTkLabel(
            self.battery_box,
            text="",
            font=("Arial", 12, "bold"),
            text_color="#cbd5e1",
            anchor="w",
        )
        self.battery_title_lbl.grid(row=0, column=0, sticky="w", padx=(10, 4))

        self.battery_value_lbl = ctk.CTkLabel(
            self.battery_box,
            text="",
            font=("Courier New", 12, "bold"),
            text_color="#cbd5e1",
            anchor="e",
        )
        self.battery_value_lbl.grid(row=0, column=1, sticky="e", padx=(4, 10))

    def set_values(self, temp_electroic, temp_battery):
        try:
            self.electronic_value = float(temp_electroic)
        except (TypeError, ValueError):
            self.electronic_value = 0.0

        try:
            self.battery_value = float(temp_battery)
        except (TypeError, ValueError):
            self.battery_value = 0.0

        self._refresh_labels()

    def set_language(self, language):
        self.language = language
        self._refresh_labels()

    def _refresh_labels(self):
        elec_color = self._temp_color(self.electronic_value)
        batt_color = self._temp_color(self.battery_value)
        top_label, bottom_label = self._tube_labels()

        self.electronic_box.configure(
            fg_color=self._card_bg(elec_color),
            border_color=elec_color,
        )
        self.battery_box.configure(
            fg_color=self._card_bg(batt_color),
            border_color=batt_color,
        )

        self.electronic_title_lbl.configure(text=top_label)
        self.battery_title_lbl.configure(text=bottom_label)

        self.electronic_value_lbl.configure(text=f"{self.electronic_value:.1f} C")
        self.battery_value_lbl.configure(text=f"{self.battery_value:.1f} C")

        self.electronic_title_lbl.configure(text_color=elec_color)
        self.electronic_value_lbl.configure(text_color=elec_color)
        self.battery_title_lbl.configure(text_color=batt_color)
        self.battery_value_lbl.configure(text_color=batt_color)

    def _tube_labels(self):
        if self.language == "Türkçe":
            return "Üst Tüp", "Alt Tüp"
        return "Top Tube", "Bottom Tube"

    def _temp_color(self, value):
        if value >= 40:
            return "#ef4444"
        if value >= 35:
            return "#f97316"
        if value >= 28:
            return "#facc15"
        return "#22c55e"

    def _card_bg(self, color):
        if color == "#ef4444":
            return "#3a1414"
        if color == "#f97316":
            return "#3a2412"
        if color == "#facc15":
            return "#3a3412"
        return "#15301f"
