import customtkinter as ctk
import ctypes
from PIL import Image
import cv2 as cv
import datetime
from indicators.battery_indicator import BatteryIndicator
from indicators.warning_indicator import WarningIndicator
from indicators.timer_indicator import TimerIndicator

from settings import SettingsPanel

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NaviDeck.app")

class NaviDeck(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.iconbitmap("./_icons/main/nrt_logo.ico")
        self.title("NaviDeck")
        self.geometry("1920x1080")
        self.attributes("-fullscreen", True)


# _____ TOP BAR ___________________________________

        self.top_bar = ctk.CTkFrame(
            self,
            height=85,
            fg_color="#000000",
            corner_radius=0
        )
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
        self.more_button.pack(side="right", padx=20, pady=12)

        self.more_button.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.more_button.bind("<Leave>", lambda e: self.config(cursor=""))

        self.vert_spacer = ctk.CTkFrame(
            self.top_bar,
            fg_color="#393939",
            height=70,
            width=2
        )
        self.vert_spacer.pack(side="right", padx=5, pady=5)

        self.battery = BatteryIndicator(
            self.top_bar,
            battery_percent=88,
            minutes_left=95,
            icons_dir="./_icons/main",
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
            corner_radius=12
        )
        self.warning.pack(side="left", anchor="center", padx=20, pady=12)


# _____ MAIN FRAME ___________________________________

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)


# _____ RIGHT BAR ___________________________________

        self.curr_footage = "N25"
        self.footage_buttons = {}

        self.right_bar = ctk.CTkFrame(
            self.main_frame,
            width=320,
            fg_color="#000000",
            corner_radius=0
        )
        self.right_bar.pack(side="right", fill="y")
        self.right_bar.pack_propagate(False)

        self.horizontal_spacer1 = ctk.CTkFrame(
            self.right_bar, 
            fg_color="#393939",
            height=2,
            width=280
        )
        self.horizontal_spacer1.pack(side="top", pady=5)

        self.clock_lbl = ctk.CTkLabel(
            self.right_bar,
            text="00:00",
            font=("Arial", 27, "bold")
        )
        self.clock_lbl.pack(side="top", pady=7)

        self.timer = TimerIndicator(
            self.right_bar,
            corner_radius=12,
            border_width=2,
            border_color="#393939",
            fg_color="#171616"
        )
        self.timer.pack(side="top", pady=10)

        self.footage_buttons = {}

        # Mini ROV
        self.footage_btn2 = ctk.CTkButton(
            self.right_bar,
            text="Footage 2\nMini ROV",
            font=("Arial", 20, "bold"),
            fg_color="#171616",
            hover=False,
            width=270,
            height=150,
            corner_radius=13,
            border_width=3,
            border_color="#00FFAA" if self.curr_footage == "Mini ROV" else "#393939",
            command=lambda: self.select_footage("Mini ROV")
        )
        self.footage_btn2.pack(side="bottom", pady=15)

        # N25
        self.footage_btn1 = ctk.CTkButton(
            self.right_bar,
            text="Footage 1\nN25",
            font=("Arial", 20, "bold"),
            fg_color="#171616",
            hover=False,
            width=270,
            height=150,
            corner_radius=13,
            border_width=3,
            border_color="#00FFAA" if self.curr_footage == "N25" else "#393939",
            command=lambda: self.select_footage("N25")
        )

        self.footage_btn1.pack(side="bottom", pady=7)

        self.footage_lbl = ctk.CTkLabel(
            self.right_bar,
            text=f"Selected: {self.curr_footage}",
            font=("Arial", 20, "bold")
        )
        self.footage_lbl.pack(side="bottom", pady=5, padx=25, anchor="w")

        self.footage_buttons["Mini ROV"] = self.footage_btn2
        self.footage_buttons["N25"] = self.footage_btn1

        self.horizontal_spacer2 = ctk.CTkFrame(
            self.right_bar,
            fg_color="#393939",
            width=280,
            height=2
        )
        self.horizontal_spacer2.pack(side="bottom", pady=10)




# _____ CAM FRAME ___________________________________

        self.cam_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.cam_frame.pack(side="left", fill="both", expand=True)

        self.no_cam_img = ctk.CTkImage(
            light_image=Image.open("./_icons/main/nocam.png"),
            size=(350, 350) )

        self.cam_label = ctk.CTkLabel(
            self.cam_frame,
            text="",

            bg_color="transparent",
            fg_color="transparent"
        )
        self.cam_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.cam_running = True

        if not self.cam_running:
            self.cam_label.configure(image=self.no_cam_img)
        else:
            self.after(50, lambda: self.update_footage(cv.imread("./_footage/3.webp")))


# _____ LAST CALLS ___________________________________

        self.update_clock()

    def open_settings(self):

        # Panel ilk kez oluşturuluyor
        if not hasattr(self, "settings_panel") or not self.settings_panel.winfo_exists():
            self.settings_panel = SettingsPanel(self)

        self.settings_panel.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=1,
            relheight=1
        )

        self.settings_panel.lift()

    def select_footage(self, name):

        if not hasattr(self, "footage_lbl"):
            return

        self.curr_footage = name

        self.footage_lbl.configure(
            text=f"Selected: {self.curr_footage}"
        )

        for key, btn in self.footage_buttons.items():

            if key == name:
                btn.configure(
                    border_color="#00FFAA",
                    fg_color="#171616"
                )
            else:
                btn.configure(
                    border_color="#393939",
                    fg_color="#171616"
                )

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

        scale = min(display_w / frame_w, display_h / frame_h)

        new_w = int(frame_w * scale)
        new_h = int(frame_h * scale)

        resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)
        resized = cv.cvtColor(resized, cv.COLOR_BGR2RGB)

        img = Image.fromarray(resized)

        ctk_img = ctk.CTkImage(light_image=img, size=(new_w, new_h))

        self.cam_label.configure(image=ctk_img)
        self.cam_label.image = ctk_img

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M")

        self.clock_lbl.configure(text=now)

        self.after(600, self.update_clock)

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = NaviDeck()
    app.run()