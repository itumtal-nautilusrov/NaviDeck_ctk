import customtkinter as ctk
import tkintermapview
import os
import json
from tkinter import Menu
from PIL import Image, ImageDraw, ImageFont, ImageTk

class MiniMapIndicator(ctk.CTkFrame):
    def __init__(self, master, on_waypoints_changed=None, **kwargs):
        super().__init__(master, fg_color="#1a1a1a", border_width=2, border_color="#393939", corner_radius=0, **kwargs)

        # Called after every waypoint mutation.  The owning UI is responsible
        # for deciding how the current route is sent to the vehicle/server.
        self.on_waypoints_changed = on_waypoints_changed
        self.is_fullscreen = False
        self.home_position = (41.0082, 28.9784)
        self.waypoints_file = os.path.abspath("waypoints.json")
        self.marker_list = [] # Haritadaki marker objeleri
        self.marker_icons = []  # Keep PhotoImage references alive for Tk.
        self.waypoint_data = self.load_waypoints() # Koordinat verileri (Lat, Lng)

        # 1. Veritabanı ve Harita Kurulumu
        save_dir = os.path.join(os.getcwd(), "data", "map")
        os.makedirs(save_dir, exist_ok=True)
        db_path = os.path.join(save_dir, "offline_map_data.db")
        
        self.map_widget = tkintermapview.TkinterMapView(
            self, width=250, height=250, corner_radius=0, database_path=db_path
        )
        self.map_widget.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 2. Google Satellite Ayarı
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", max_zoom=19)
        self.map_widget.set_position(*self.home_position)  
        self.map_widget.set_zoom(15)

        # 3. Sağ Tık Menüsü (Context Menu)
        self.context_menu = Menu(self, tearoff=0, bg="#1a1a1f", fg="white", activebackground="#0ea5e9", bd=0)
        self.context_menu.add_command(label="📍 Add Waypoint", command=self.add_waypoint_context)
        self.context_menu.add_command(label="🏠 Center Map", command=self.reset_to_home)
        self.map_widget.add_right_click_menu_command(label="Add Waypoint", command=self.add_waypoint_from_map, pass_coords=True)

        # 4. Özel Butonlar
        # Fullscreen
        self.resize_btn = ctk.CTkButton(
            self, text="⛶", width=28, height=28, corner_radius=6,
            fg_color="#222222", hover_color="#444444", command=self.toggle_fullscreen
        )
        self.resize_btn.place(relx=0.02, rely=0.02, anchor="nw")

        # Rewind (Temizle)
        self.clear_btn = ctk.CTkButton(
            self, text="↺", width=28, height=28, corner_radius=6,
            fg_color="#222222", hover_color="#ef4444", command=self.clear_all_waypoints
        )
        self.clear_btn.place(relx=0.02, rely=0.15, anchor="nw")

        # Zoom In
        self.zoom_in_btn = ctk.CTkButton(
            self, text="+", width=25, height=25, corner_radius=5,
            fg_color="#222222", hover_color="#444444", command=lambda: self.map_widget.set_zoom(self.map_widget.zoom + 1)
        )
        self.zoom_in_btn.place(relx=0.98, rely=0.98, anchor="se", x=0, y=-30)

        # Zoom Out
        self.zoom_out_btn = ctk.CTkButton(
            self, text="-", width=25, height=25, corner_radius=5,
            fg_color="#222222", hover_color="#444444", command=lambda: self.map_widget.set_zoom(self.map_widget.zoom - 1)
        )
        self.zoom_out_btn.place(relx=0.98, rely=0.98, anchor="se", x=0, y=0)

        # Harita yüklendiğinde eski waypointleri çiz
        self.refresh_markers()

    # --- WAYPOINT MANTIĞI ---

    def load_waypoints(self):
        if os.path.exists(self.waypoints_file):
            try:
                with open(self.waypoints_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

    def save_waypoints(self):
        with open(self.waypoints_file, "w", encoding="utf-8") as f:
            json.dump(self.waypoint_data, f, indent=2)

    def _notify_waypoints_changed(self, action):
        """Publish a JSON-safe snapshot after add, delete, or clear actions."""
        if not self.on_waypoints_changed:
            return

        waypoints = [
            {"number": index + 1, "lat": waypoint["lat"], "lng": waypoint["lng"]}
            for index, waypoint in enumerate(self.waypoint_data)
        ]
        self.on_waypoints_changed(action, waypoints)

    def add_waypoint_from_map(self, coords):
        """Sağ tıklandığında koordinatı alır."""
        lat, lng = coords
        self.waypoint_data.append({"lat": lat, "lng": lng})
        self.save_waypoints()
        self.refresh_markers()
        self._notify_waypoints_changed("add")

    def add_waypoint_context(self):
        """Menüden ekleme (Alternatif)"""
        pos = self.map_widget.get_position()
        self.add_waypoint_from_map(pos)

    def delete_waypoint(self, marker):
        """Bir markera tıklandığında onu siler."""
        # Marker verisini bul ve listeden çıkar
        lat, lng = marker.position
        self.waypoint_data = [wp for wp in self.waypoint_data if not (wp['lat'] == lat and wp['lng'] == lng)]
        self.save_waypoints()
        self.refresh_markers()
        self._notify_waypoints_changed("delete")

    def clear_all_waypoints(self):
        self.waypoint_data = []
        self.save_waypoints()
        self.refresh_markers()
        self._notify_waypoints_changed("clear")

    def refresh_markers(self):
        """Tüm markerları siler ve güncel listeye göre yeniden (1,2,3...) çizer."""
        for m in self.marker_list:
            m.delete()
        self.marker_list = []

        self.marker_icons = []
        for i, wp in enumerate(self.waypoint_data):
            icon = self._make_waypoint_icon(i + 1)
            self.marker_icons.append(icon)
            marker = self.map_widget.set_marker(
                wp['lat'], wp['lng'],
                icon=icon,
                icon_anchor="center",
                command=self.delete_waypoint # Tıklayınca silme fonksiyonu
            )
            self.marker_list.append(marker)

    @staticmethod
    def _make_waypoint_icon(number):
        """Create a blue circle with a centered white waypoint number."""
        size = 32
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((1, 1, size - 2, size - 2), fill="#0ea5e9", outline="#ffffff", width=2)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except OSError:
            font = ImageFont.load_default()
        text = str(number)
        box = draw.textbbox((0, 0), text, font=font)
        draw.text(
            ((size - (box[2] - box[0])) / 2, (size - (box[3] - box[1])) / 2 - box[1]),
            text, fill="white", font=font,
        )
        return ImageTk.PhotoImage(image)

    def reset_to_home(self):
        self.map_widget.set_position(*self.home_position)
        self.map_widget.set_zoom(15)

    # --- UI AYARLARI ---

    def set_offline_mode(self, is_offline):
        self.map_widget.use_database_only = is_offline

    def toggle_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.place_forget()
            self.configure(width=250, height=250)
            self.place(relx=0.99, rely=0.99, anchor="se", x=-10, y=-10)
            self.is_fullscreen = False
            # Küçük butonlar
            self.zoom_in_btn.configure(width=25, height=25)
            self.zoom_out_btn.configure(width=25, height=25)
            self.resize_btn.configure(width=28, height=28)
            self.clear_btn.configure(width=28, height=28)
        else:
            self.place_forget()
            self.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)
            self.is_fullscreen = True
            self.lift()
            # Büyük butonlar
            self.zoom_in_btn.configure(width=40, height=40)
            self.zoom_out_btn.configure(width=40, height=40)
            self.resize_btn.configure(width=40, height=40)
            self.clear_btn.configure(width=40, height=40)
