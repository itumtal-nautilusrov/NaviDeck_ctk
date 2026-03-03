import cv2 as cv
import numpy as np
import math

def draw_stats(roll, depth, speed, width=1280, height=720):
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    hud_color = (0, 255, 0)
    center = (width // 2, height // 2)

    # =======================
    # 🎡 ROLL LINE
    # =======================
    length = 400
    angle = math.radians(roll)

    x1 = int(center[0] - length * math.cos(angle))
    y1 = int(center[1] - length * math.sin(angle))
    x2 = int(center[0] + length * math.cos(angle))
    y2 = int(center[1] + length * math.sin(angle))

    cv.line(frame, (x1, y1), (x2, y2), hud_color, 2)
    cv.circle(frame, center, 6, hud_color, -1)

    cv.putText(frame, f"ROLL {roll:.1f}",
               (center[0]-70, center[1]+50),
               cv.FONT_HERSHEY_SIMPLEX, 0.7, hud_color, 2)

    # =======================
    # 📏 DEPTH SCALE (LEFT)
    # =======================
    top = 150
    bottom = height - 150
    x_pos = 120

    cv.line(frame, (x_pos, top), (x_pos, bottom), hud_color, 2)

    max_depth = 100  # ayarlayabilirsin
    depth = np.clip(depth, 0, max_depth)

    for d in range(0, max_depth+1, 10):
        y = bottom - int((d/max_depth)*(bottom-top))
        cv.line(frame, (x_pos-10, y), (x_pos+10, y), hud_color, 1)
        cv.putText(frame, str(d),
                   (x_pos-60, y+5),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5,
                   hud_color, 1)

    y_depth = bottom - int((depth/max_depth)*(bottom-top))
    cv.circle(frame, (x_pos, y_depth), 8, (0,0,255), -1)

    cv.putText(frame, f"{depth:.1f} m",
               (x_pos-40, bottom+40),
               cv.FONT_HERSHEY_SIMPLEX, 0.7,
               hud_color, 2)

    # =======================
    # 🚤 SPEED BOX (RIGHT)
    # =======================
    box_x1 = width - 300
    box_y1 = 100
    box_x2 = width - 80
    box_y2 = 180

    cv.rectangle(frame, (box_x1, box_y1),
                 (box_x2, box_y2),
                 hud_color, 2)

    cv.putText(frame, f"SPD",
               (box_x1+20, box_y1+35),
               cv.FONT_HERSHEY_SIMPLEX, 0.6,
               hud_color, 1)

    cv.putText(frame, f"{speed:.2f} m/s",
               (box_x1+20, box_y1+80),
               cv.FONT_HERSHEY_SIMPLEX, 0.8,
               hud_color, 2)

    return frame