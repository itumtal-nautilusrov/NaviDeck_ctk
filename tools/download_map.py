"""Download a sample Istanbul area into NaviDeck's active map database."""

from offline_map import download_offline_area


if __name__ == "__main__":
    download_offline_area((41.0500, 28.9000), (40.9500, 29.0500), 10, 16)
