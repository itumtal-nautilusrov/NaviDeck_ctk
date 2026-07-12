"""Offline tile download helpers shared by the settings screen and CLI tool."""

from __future__ import annotations

from pathlib import Path

TILE_SERVER = "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
MAP_DATABASE = Path(__file__).resolve().parents[1] / "data" / "map" / "offline_map_data.db"


def download_offline_area(top_left, bottom_right, zoom_min=12, zoom_max=16, status=print):
    """Store satellite tiles in the database used by ``MiniMapIndicator``."""
    import tkintermapview

    zoom_min, zoom_max = int(zoom_min), int(zoom_max)
    if not (0 <= zoom_min <= zoom_max <= 19):
        raise ValueError("Zoom range must be between 0 and 19.")
    if top_left[0] <= bottom_right[0] or top_left[1] >= bottom_right[1]:
        raise ValueError("Top-left must be north-west of bottom-right.")

    MAP_DATABASE.parent.mkdir(parents=True, exist_ok=True)
    status("Preparing offline map download…")
    loader = tkintermapview.OfflineLoader(path=str(MAP_DATABASE), tile_server=TILE_SERVER, max_zoom=19)
    loader.save_offline_tiles(top_left, bottom_right, zoom_min, zoom_max)
    status("Offline map download completed.")
    return str(MAP_DATABASE)
