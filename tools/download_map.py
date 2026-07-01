import tkintermapview

print("Harita indiriliyor, lütfen bekleyin...")
loader = tkintermapview.OfflineLoader(path="offline_map_data.db")

# İstanbul merkez için örnek koordinatlar (Sol üst - Sağ alt köşeler)
top_left = (41.0500, 28.9000)
bottom_right = (40.9500, 29.0500)

loader.save_offline_tiles(
    top_left_position=top_left,
    bottom_right_position=bottom_right,
    zoom_min=10,
    zoom_max=16, 
    tile_server="https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
)

print("İndirme tamamlandı! Artık uygulamanız internetsiz ve kasmadan çalışabilir.")