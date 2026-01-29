import pyautogui

from JinChanChan.config import Config


class GameController:
    """操作控制类：负责动"""

    def __init__(self):
        # 预先计算好每个格子的中心点偏移量，避免每次点击都重复计算
        self.card_centers = []
        start_x, start_y = Config.point
        center_offset_x = Config.w // 2
        center_offset_y = Config.h // 2

        for i in range(5):
            cx = start_x + center_offset_x + (i * Config.move)
            cy = start_y + center_offset_y
            self.card_centers.append((cx, cy))

    def click_card(self, idx, hero_name="未知"):
        """
        点击第 idx 张卡牌
        :param idx: 卡牌序号 (0-4)
        :param hero_name: 英雄名称(用于日志)
        """
        if idx < 0 or idx >= 5:
            return

        cx, cy = self.card_centers[idx]

        # 修正: 移除硬编码的 1920，除非你是双屏且游戏在副屏
        # 如果必须偏移，建议在 Config 中定义 Config.screen_offset_x
        final_x = cx + getattr(Config, 'screen_offset_x', 0)
        final_y = cy + getattr(Config, 'y_bias', 0)

        # 移动并点击
        pyautogui.moveTo(final_x, final_y, duration=0)
        # 连点两下防止漏点
        for _ in range(2):
            pyautogui.mouseDown(button="left")
            pyautogui.mouseUp(button="left")

        print(f'\033[32m[Action] 已拿牌: {idx + 1}号位 - {hero_name}\033[0m')
