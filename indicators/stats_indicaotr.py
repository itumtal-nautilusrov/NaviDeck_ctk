import cv2 as cv
import numpy as np
import math

class StatsIndicator():
    def __init__(self):
        pass

    def draw_roll(self, frame, roll=0):
        h, w = frame.shape[:2]

        cx = w // 2
        cy = h // 4

        line_length = 570
        gap = 50

        roll_rad = math.radians(roll)

        dx = math.cos(roll_rad)
        dy = math.sin(roll_rad)

        half_len = line_length / 2
        half_gap = gap / 3

        # Sol çizgi
        x1 = int(cx - half_len * dx)
        y1 = int(cy - half_len * dy)

        x2 = int(cx - half_gap * dx)
        y2 = int(cy - half_gap * dy)

        cv.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Sağ çizgi
        x3 = int(cx + half_gap * dx)
        y3 = int(cy + half_gap * dy)

        x4 = int(cx + half_len * dx)
        y4 = int(cy + half_len * dy)

        cv.line(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)

        return frame

    
if __name__ == "__main__":
    indicator = StatsIndicator()

    roll = 0

    while True:
        frame = np.zeros((600, 800, 3), dtype=np.uint8)

        frame = indicator.draw_roll(frame, roll=roll)

        cv.imshow("Roll Indicator", frame)

        roll += 1
        if roll > 360:
            roll = 0

        if cv.waitKey(20) & 0xFF == 27:
            break

    cv.destroyAllWindows()