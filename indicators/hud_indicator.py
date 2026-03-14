import cv2 as cv
import numpy as np
import math

class HUDIndicator():
    def __init__(self):
        self.roll_img = cv.imread("./_hud/roll.png", cv.IMREAD_UNCHANGED)
        if self.roll_img is None:
            raise FileNotFoundError("'./_hud/roll.png' bulunamadı!")

    def overlay_transparent(self, background, overlay, cx, cy):
        oh, ow = overlay.shape[:2]
        x_start = cx - ow // 2
        y_start = cy - oh // 2

        x1 = max(x_start, 0)
        y1 = max(y_start, 0)
        x2 = min(x_start + ow, background.shape[1])
        y2 = min(y_start + oh, background.shape[0])

        ox1 = x1 - x_start
        oy1 = y1 - y_start
        ox2 = ox1 + (x2 - x1)
        oy2 = oy1 + (y2 - y1)

        if x2 <= x1 or y2 <= y1:
            return background

        overlay_crop = overlay[oy1:oy2, ox1:ox2]
        bg_crop = background[y1:y2, x1:x2]

        if overlay_crop.shape[2] == 4:
            alpha = overlay_crop[:, :, 3:4].astype(np.float32) / 255.0
            rgb   = overlay_crop[:, :, :3].astype(np.float32)
            bg    = bg_crop.astype(np.float32)

            blended = (alpha * rgb + (1 - alpha) * bg).astype(np.uint8)
            background[y1:y2, x1:x2] = blended
        else:
            background[y1:y2, x1:x2] = overlay_crop[:, :, :3]

        return background

    def rotate_image(self, image, angle):
        h, w = image.shape[:2]
        cx, cy = w // 2, h // 2

        M = cv.getRotationMatrix2D((cx, cy), -angle, 1.0)

        cos = abs(M[0, 0])
        sin = abs(M[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)

        M[0, 2] += (new_w / 2) - cx
        M[1, 2] += (new_h / 2) - cy

        rotated = cv.warpAffine(
            image, M, (new_w, new_h),
            flags=cv.INTER_LINEAR,
            borderMode=cv.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )
        return rotated

    def draw_roll(self, frame, roll=0):
        h, w = frame.shape[:2]
        cx = w // 2
        cy = (h // 5)*2

        rotated = self.rotate_image(self.roll_img, roll)
        frame = self.overlay_transparent(frame, rotated, cx, cy)
        return frame


if __name__ == "__main__":
    indicator = HUDIndicator()
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