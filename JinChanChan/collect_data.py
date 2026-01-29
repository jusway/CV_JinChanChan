import os
import time
import mss
import numpy as np
from PIL import Image

# 导入现有模块
from config import Config
from game_vision import GameVision
from system_env import SystemEnv


class DataCollector:
    def __init__(self):
        # 1. 初始化 DPI 感知 (非常重要，否则截图位置会偏)
        SystemEnv.init_dpi_awareness()

        # 2. 初始化视觉模块
        self.vision = GameVision()

        # 3. 初始化截图对象
        self.sct = mss.mss()

        # 4. 设置保存路径
        self.save_dir = "collected_cards"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"已创建保存目录: {self.save_dir}")

    def save_current_cards(self):
        """截取当前屏幕的5张卡牌并保存"""
        try:
            # 使用 GameVision 获取切片后的 Numpy 数组列表
            # 注意：vision.capture_hero_cards 返回的是 RGB 格式的 numpy array
            card_imgs_np = self.vision.capture_hero_cards(self.sct)

            timestamp = int(time.time())
            print(f"正在保存 {len(card_imgs_np)} 张图片...")

            for i, img_np in enumerate(card_imgs_np):
                # 将 Numpy 数组转换为 PIL Image 对象以便保存
                img = Image.fromarray(img_np)

                # 生成文件名: timestamp_位置索引.png
                # 例如: 1705666666_0.png (代表第1个格子的卡)
                filename = f"{timestamp}_{i}.png"
                full_path = os.path.join(self.save_dir, filename)

                img.save(full_path)
                print(f"  - 已保存: {filename}")

            print(f"完成。保存路径: {os.path.abspath(self.save_dir)}")

        except Exception as e:
            print(f"截图保存失败: {e}")

    def run(self):
        print("=" * 40)
        print("   金铲铲卡牌收集工具已启动")
        print("=" * 40)
        print("操作说明:")
        print("按 [Enter] 键 -> 截图并保存当前5张卡牌")
        print("输入 'q' -> 退出程序")
        print("-" * 40)

        while True:
            cmd = input("\n等待指令 (回车截图/q退出): ").lower().strip()

            if cmd == 'q':
                print("程序退出。")
                break

            # 这里的逻辑是：只要不是q，按回车就截图
            self.save_current_cards()


if __name__ == '__main__':
    collector = DataCollector()
    collector.run()