import customtkinter as ctk
from PIL import Image
import os


ICONS = [
    (75, "battery100.png"),
    (50, "battery75.png"),
    (25, "battery50.png"),
    (0,  "battery25.png"),
]


class BatteryIndicator(ctk.CTkFrame):
    def __init__(self, master, battery_percent=100, minutes_left=0, icons_dir="./_icons/main", **kwargs):
        kwargs.setdefault("width", 220)
        kwargs.setdefault("height", 72)
        super().__init__(master, **kwargs)
        self.grid_propagate(False)

        self.percent = battery_percent
        self.minutes = minutes_left
        self.icons  = self._load_icons(icons_dir)

        self._build()
        self.update(battery_percent, minutes_left)

    # ── public ────────────────────────────────

    def set_battery(self, percent, minutes_left):
        self.update(percent, minutes_left)

    def set_percent(self, percent):
        self.update(percent, self.minutes)

    def set_minutes(self, minutes_left):
        self.update(self.percent, minutes_left)

    def update(self, percent, minutes_left):
        self.percent = max(0.0, min(100.0, float(percent)))
        self.minutes = max(0, int(minutes_left))
        self._refresh()

    # ── private ───────────────────────────────

    def _load_icons(self, icons_dir):
        cache = {}
        for _, name in ICONS:
            path = os.path.join(icons_dir, name)
            if os.path.exists(path):
                img = Image.open(path)
                cache[name] = ctk.CTkImage(img, img, size=(50, 50))
        return cache

    def _pick_icon(self):
        for threshold, name in ICONS:
            if self.percent > threshold:
                return self.icons.get(name)
        return self.icons.get("battery25.png")

    def _color(self):
        if self.percent > 50: return "#2ecc71"
        if self.percent > 20: return "#f39c12"
        return "#e74c3c"

    def _time_str(self):
        if not self.minutes:
            return ""
        h, m = divmod(self.minutes, 60)
        return f"· {h}s {m}dk" if h else f"· {m}dk"

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)

        self.icon_lbl = ctk.CTkLabel(self, text="🔋", font=("Arial", 26))
        self.icon_lbl.grid(row=0, column=0, padx=(10, 4), pady=(6, 2), sticky="ns")

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=0, column=1, padx=(2, 10), pady=(6, 2), sticky="nsew")

        self.pct_lbl = ctk.CTkLabel(info, text="", font=ctk.CTkFont("Arial", 20, "bold"))
        self.pct_lbl.pack(side="left")

        self.min_lbl = ctk.CTkLabel(info, text="", font=("Arial", 15), text_color="gray")
        self.min_lbl.pack(side="left", padx=(6, 0))

        self.bar = ctk.CTkProgressBar(self, height=6, corner_radius=3)
        self.bar.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 14), sticky="ew")

    def _refresh(self):
        color = self._color()
        icon  = self._pick_icon()

        if icon:
            self.icon_lbl.configure(image=icon, text="")
        else:
            self.icon_lbl.configure(image=None, text="🔋")

        self.pct_lbl.configure(text=f"%{self.percent:.0f}", text_color=color)
        self.min_lbl.configure(text=self._time_str())
        self.bar.configure(progress_color=color)
        self.bar.set(self.percent / 100)


# ── demo ──────────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Battery")
    app.geometry("300x190")

    bat = BatteryIndicator(app, battery_percent=78, minutes_left=95, corner_radius=10)
    bat.pack(padx=20, pady=20, fill="x")

    ctrl = ctk.CTkFrame(app, fg_color="transparent")
    ctrl.pack(padx=20, fill="x")

    pct = ctk.StringVar(value="78")
    mins = ctk.StringVar(value="95")

    row = ctk.CTkFrame(ctrl, fg_color="transparent")
    row.pack(fill="x", pady=4)
    ctk.CTkLabel(row, text="%",  width=20).pack(side="left")
    ctk.CTkEntry(row, textvariable=pct,  width=65).pack(side="left", padx=4)
    ctk.CTkLabel(row, text="dk", width=20).pack(side="left", padx=(8, 0))
    ctk.CTkEntry(row, textvariable=mins, width=65).pack(side="left", padx=4)
    ctk.CTkButton(row, text="Güncelle", width=80,
                  command=lambda: bat.set_battery(pct.get(), mins.get())
                  ).pack(side="left", padx=(8, 0))

    app.mainloop()