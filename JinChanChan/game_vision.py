from JinChanChan.config import Config
import numpy as np


class GameVision:
    def capture_hero_cards(self, sct):
        target_monitor = None
        global_x, global_y = Config.point

        for monitor in sct.monitors[1:]:
            m_x, m_y = monitor['left'], monitor['top']
            m_w, m_h = monitor['width'], monitor['height']

            if (m_x <= global_x < m_x + m_w) and (m_y <= global_y < m_y + m_h):
                target_monitor = monitor
                break

        if target_monitor is None:
            print(f"Error: Config.point {Config.point} is not inside any detected screen.")
            return []

        screenshot = sct.grab(target_monitor)
        img_bgra = np.array(screenshot)
        img_rgb = img_bgra[:, :, :3][:, :, ::-1]

        monitor_left = target_monitor['left']
        monitor_top = target_monitor['top']

        relative_x = global_x - monitor_left
        relative_y = global_y - monitor_top

        sub_imgs = []
        screen_h, screen_w = img_rgb.shape[:2]

        current_x = relative_x

        for _ in range(5):
            y_end = min(relative_y + Config.h, screen_h)
            x_end = min(current_x + Config.w, screen_w)

            if x_end <= current_x or y_end <= relative_y:
                print("Warning: Crop area is empty or out of bounds.")
                continue

            crop = img_rgb[relative_y:y_end, current_x:x_end, :]
            crop = np.ascontiguousarray(crop)
            sub_imgs.append(crop)
            current_x += Config.move

        return sub_imgs