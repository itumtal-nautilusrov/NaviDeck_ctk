import customtkinter as ctk

class CameraSelector(ctk.CTkFrame):
    def __init__(self, master, cameras, on_change=None, **kwargs):
        # We pop any unexpected kwargs like icons_dir if it was passed by older code
        kwargs.pop("icons_dir", None)
        
        super().__init__(master, fg_color="transparent", bg_color="transparent", **kwargs)
        
        self.cameras = cameras
        self.on_change = on_change
        
        self.seg_button = ctk.CTkSegmentedButton(
            self,
            values=self.cameras,
            command=self._handle_change,
            fg_color="#1a1a1a",
            selected_color="#333333",
            selected_hover_color="#444444",
            unselected_color="#1a1a1a",
            unselected_hover_color="#222222",
            text_color="#CCCCCC",
            font=("Segoe UI", 14, "bold"),
            corner_radius=8
        )
        self.seg_button.pack(fill="both", expand=True)
        if self.cameras:
            self.seg_button.set(self.cameras[0])
            
    def _handle_change(self, value):
        if self.on_change:
            self.on_change(value)