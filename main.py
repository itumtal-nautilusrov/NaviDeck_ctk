import customtkinter as ctk
import ctypes
from PIL import Image
from indicators.battery_indicator import BatteryIndicator
from indicators.warning_indicator import WarningIndicator

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NaviDeck.app")

class NaviDeck(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.iconbitmap("./_icons/nrt_logo.ico")
        self.title("NaviDeck")
        self.geometry("1920x1080")
        self.attributes("-fullscreen", True)

        self.top_bar = ctk.CTkFrame(
            self,
            height=75,
            fg_color="#000000",
            corner_radius=0
        )
        self.top_bar.pack(anchor="n", fill="x")

        img = ctk.CTkImage(light_image=Image.open("./_icons/more.png"), size=(60, 60))
        self.img_button = ctk.CTkButton(
            self.top_bar,
            width=75,
            image=img,
            text="",
            fg_color="transparent"
        )
        self.img_button.pack(side="right", padx=20, pady=12)

        self.spacer = ctk.CTkFrame(
            self.top_bar,
            fg_color="#393939",
            height=65,
            width=2
        )
        self.spacer.pack(side="right", padx=5, pady=5)

        self.battery = BatteryIndicator(
            self.top_bar,
            battery_percent=78,
            minutes_left=95,
            icons_dir="./_icons",
            fg_color="transparent",
            border_width=2,
            border_color="#3a3a3a", 
            corner_radius=12,
        )
        self.battery.pack(side="right", anchor="center", padx=20, pady=12)

        self.warning = WarningIndicator(
            self.top_bar,
            text="Low Battery",
            level=2,
            corner_radius=12,
        )
        self.warning.pack(side="left", anchor="center", padx=20, pady=12)


    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = NaviDeck()
    app.run()