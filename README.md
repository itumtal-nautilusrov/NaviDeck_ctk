# NaviDeck CTK

CustomTkinter ROV control UI with camera, telemetry, route waypoints, and offline satellite maps.

## Quick start (simulation)

```powershell
.venv\Scripts\python.exe -m server.main_server
.venv\Scripts\python.exe main.py
```

The server starts in `simulation` mode. It provides fake telemetry on port `9998`, receives UI commands (including `waypoints` JSON snapshots) on port `9997`, and keeps the camera endpoint on port `9999`.

## Hardware hand-off

The UI clients use `NAVIDECK_HOST`, `NAVIDECK_COMMAND_PORT`, and `NAVIDECK_TELEMETRY_PORT` when set; otherwise they connect to localhost.

On the ROV-side machine, switch only the server adapter:

```powershell
.venv\Scripts\python.exe -m server.main_server --mode hardware --serial-port COM3 --baudrate 115200
```

Hardware telemetry is one UTF-8 JSON object per serial line. The gateway forwards each UI command as the same UTF-8 newline-delimited line to that serial device. If the port is absent or a telemetry line is invalid, it automatically falls back to the simulation schema, so the UI remains usable during bring-up.

## Offline map

Open **Settings → Map**, specify the north-west and south-east corners plus zoom range, then download. Tiles are stored in `data/map/offline_map_data.db`, which is also the database read by the in-app map. The same download can be run from `tools/download_map.py` for the sample Istanbul area.
