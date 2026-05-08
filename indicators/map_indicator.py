import customtkinter as ctk
import tkintermapview
import os
class MiniMapIndicator(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#1a1a1a", border_width=2, border_color="#393939", corner_radius=0, **kwargs)
        
        self.is_fullscreen = False
        
        self.map_widget = tkintermapview.TkinterMapView(
            self,
            width=250,
            height=250,
            corner_radius=0
        )
        self.map_widget.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Fullscreen Toggle Button (Top Left)
        self.resize_btn = ctk.CTkButton(
            self, text="⛶", width=30, height=30, corner_radius=8,
            fg_color="#333333", hover_color="#555555", command=self.toggle_fullscreen
        )
        self.resize_btn.place(relx=0.02, rely=0.02, anchor="nw")

        # Delete native zoom buttons and override draw so they don't respawn
        if hasattr(self.map_widget, "button_zoom_in"):
            self.map_widget.canvas.delete(self.map_widget.button_zoom_in.canvas_rect)
            self.map_widget.canvas.delete(self.map_widget.button_zoom_in.canvas_text)
            self.map_widget.button_zoom_in.draw = lambda *args: None

            self.map_widget.canvas.delete(self.map_widget.button_zoom_out.canvas_rect)
            self.map_widget.canvas.delete(self.map_widget.button_zoom_out.canvas_text)
            self.map_widget.button_zoom_out.draw = lambda *args: None

        # Custom Zoom Buttons (Bottom Right)
        self.zoom_in_btn = ctk.CTkButton(
            self, text="+", width=25, height=25, corner_radius=6,
            fg_color="#333333", hover_color="#555555", command=lambda: self.map_widget.set_zoom(self.map_widget.zoom + 1)
        )
        self.zoom_in_btn.place(relx=0.98, rely=0.98, anchor="se", x=0, y=-30)

        self.zoom_out_btn = ctk.CTkButton(
            self, text="-", width=25, height=25, corner_radius=6,
            fg_color="#333333", hover_color="#555555", command=lambda: self.map_widget.set_zoom(self.map_widget.zoom - 1)
        )
        self.zoom_out_btn.place(relx=0.98, rely=0.98, anchor="se", x=0, y=0)

        # Load offline database if it exists and we want to default to offline
        # But we will start online by default unless set otherwise
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19)
        
        # Default position (e.g., somewhere central or where the drone operates)
        self.map_widget.set_position(41.0082, 28.9784)  # Istanbul
        self.map_widget.set_zoom(15)


    def toggle_fullscreen(self, event=None):
        if self.is_fullscreen:
            # minimize back to square
            self.place_forget()
            self.configure(width=250, height=250)
            self.place(relx=0.99, rely=0.99, anchor="se", x=-10, y=-10)
            self.is_fullscreen = False
            
            # Make zoom buttons smaller
            self.zoom_in_btn.configure(width=25, height=25)
            self.zoom_in_btn.place(y=-30)
            self.zoom_out_btn.configure(width=25, height=25)
            self.resize_btn.configure(width=30, height=30)
        else:
            # maximize
            self.place_forget()
            self.place(relx=0.5, rely=0.5, anchor="center", x=0, y=0, relwidth=1.0, relheight=1.0)
            self.is_fullscreen = True
            # bring to front
            self.lift()
            
            # Make zoom buttons larger
            self.zoom_in_btn.configure(width=40, height=40)
            self.zoom_in_btn.place(y=-45)
            self.zoom_out_btn.configure(width=40, height=40)
            self.resize_btn.configure(width=40, height=40)

