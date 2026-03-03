import customtkinter as ctk
from PIL import Image


class SettingsPanel(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="#0E0E0E", corner_radius=0)


# _____ TOP BAR ___________________________________

        self.top_bar = ctk.CTkFrame(
            self,
            height=300,
            fg_color="#141414",
            corner_radius=0
        )
        self.top_bar.pack(fill="x", side="top")

        self.back_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/back.png"),
            size=(60, 60)
        )

        self.back_btn = ctk.CTkButton(
            self.top_bar,
            width=60,
            height=60,
            text="",
            image=self.back_img,
            fg_color="transparent",
            hover=False,
            command=self.close_panel
        )
        self.back_btn.pack(side="left", padx=20)

        self.title_lbl = ctk.CTkLabel(
            self.top_bar,
            text="Settings",
            font=("Segoe UI", 50, "bold"),
            text_color="#FFFFFF"
        )
        self.title_lbl.pack(anchor="center", pady=40)


        ctk.CTkFrame(
            self, height=2, fg_color="#2A2A2A", corner_radius=0
        ).pack(fill="x")


# _____ LEFT BAR ___________________________________

        self.left_bar = ctk.CTkFrame(
            self,
            width=450,
            fg_color="transparent",
            corner_radius=0
        )
        self.left_bar.pack(side="left", fill="y", pady=20)

        _btn = dict(
            height=75,
            width=450,
            font=ctk.CTkFont("Segoe UI", 28, "bold"),
            fg_color="#1A1A1A",
            hover_color="#242424",
            text_color="#E0E0E0",
            corner_radius=14,
            anchor="w",
        )

        self.general_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/general.png"),
            size=(40, 40)
        )

        self.general_btn = ctk.CTkButton(
            self.left_bar,
            image=self.general_img,
            text=" General",
            **_btn
        )
        self.general_btn.pack(padx=12)

        self.camera_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/camera.png"),
            size=(40, 40)
        )

        self.camera_btn = ctk.CTkButton(
            self.left_bar,
            image=self.camera_img,
            text=" Camera",
            **_btn
        )
        self.camera_btn.pack(pady=10, padx=12)

        self.map_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/map.png"),
            size=(40, 40)
        )

        self.map_btn = ctk.CTkButton(
            self.left_bar,
            image=self.map_img,
            text= " Map",
            **_btn
        )
        self.map_btn.pack(pady=10, padx=12)

        self.media_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/media.png"),
            size=(40, 40)
        )

        self.media_btn = ctk.CTkButton(
            self.left_bar,
            image=self.media_img,
            text=" Media",
            **_btn
        )
        self.media_btn.pack(pady=10, padx=12)

        self.sound_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/sound.png"),
            size=(40, 40)
        )

        self.sound_btn = ctk.CTkButton(
            self.left_bar,
            image=self.sound_img,
            text=" Sound",
            **_btn
        )
        self.sound_btn.pack(pady=10, padx=12)

        self.credits_img = ctk.CTkImage(
            light_image=Image.open("./_icons/settings/credits.png"),
            size=(40, 40)
        )

        self.credits_btn = ctk.CTkButton(
            self.left_bar,
            image=self.credits_img,
            text=" Credits",
            **_btn
        )
        self.credits_btn.pack(pady=10, padx=12)


        ctk.CTkFrame(
            self, width=2, fg_color="#2A2A2A", corner_radius=0
        ).pack(side="left", fill="y", pady=20)


# _____ MAIN FRAME ___________________________________

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#141414",
            corner_radius=16
        )
        self.main_frame.pack(fill="both", expand=True, pady=20, padx=20)


    def close_panel(self):
        self.place_forget()