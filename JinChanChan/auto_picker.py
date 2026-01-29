import mss
import threading
import sys
from pynput import keyboard

from config import Config
from feature_matcher import FeatureMatcher
from game_controler import GameController
from resource_manager import ResourceManager
from game_vision import GameVision
from system_env import SystemEnv


class AutoPicker:
    def __init__(self):
        SystemEnv.init_dpi_awareness()
        self.lock = threading.Lock()

        self.running = True

        self.wanted_heros = []
        self.lineup_name = "未加载"

        # 1. 实例化各个模块
        self.vision = GameVision()
        self.controller = GameController()

        # 2. 初始化模型
        print('---正在加载模型---')
        self.matcher = FeatureMatcher()

        # 3. 加载资源
        self.feature_db = {}
        # 移除全局 self.sct，在局部使用

        self._load_resources()

    def _load_resources(self):
        img_dict = ResourceManager.load_hero_images(Config.pictrue_dir)
        for k, v in img_dict.items():
            self.feature_db[k] = self.matcher.extract_features(v)
        self.reload_lineup()

    def reload_lineup(self):
        with self.lock:
            heros_list, name = ResourceManager.select_lineup(Config.lineup_dir)
            if heros_list:
                self.wanted_heros = heros_list
                self.lineup_name = name
                print(f"阵容已加载: {name}, 包含 {len(self.wanted_heros)} 个英雄")
            else:
                print("未选择有效阵容，请手动添加英雄。")

    def show_status(self):
        """显示当前阵容状态"""
        print(f"\n当前阵容 [{self.lineup_name}]:")
        if not self.wanted_heros:
            print("  (空)")
        else:
            # 将列表转为字符串打印，看起来更整洁
            print(f"  {', '.join(self.wanted_heros)}")
        print("-" * 30)

    def scan_and_pick(self):
        print("\n[开始扫描]...")
        try:
            # 创建 mss 上下文，确保线程安全
            with mss.mss() as sct:
                sub_imgs = self.vision.capture_hero_cards(sct)

                if not sub_imgs:
                    print("警告: 未截取到图片，请检查 Config.point 设置")
                    return

                for i, img in enumerate(sub_imgs):
                    hero_name, best_score = self.matcher.match_images(img, self.feature_db)

                    score_val = round(best_score.item(), 2)
                    # 只有当相似度大于一定阈值（比如0.5）或者为了调试时才打印，这里保留打印
                    print(f'  位置{i + 1}: {hero_name} ({score_val})')

                    should_click = False
                    with self.lock:
                        if hero_name in self.wanted_heros:
                            should_click = True

                    if should_click:
                        self.controller.click_card(i, hero_name)

        except Exception as e:
            print(f"扫描出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # [修改] 无论扫描结果如何，最后都刷新一次状态
            self.show_status()

    def on_key_press(self, key):
        try:
            if hasattr(key, 'char') and key.char == 'n':
                self.scan_and_pick()
        except AttributeError:
            pass

    def add_hero(self, name):
        with self.lock:
            self.wanted_heros.insert(0, name)
            print(f"\033[33m已添加: {name}\033[0m")
        self.show_status()

    def remove_hero_by_index(self, indices_str):
        try:
            indices = [int(i) for i in indices_str.split()]
            indices.sort(reverse=True)
            with self.lock:
                for i in indices:
                    if 0 <= i < len(self.wanted_heros):
                        removed = self.wanted_heros.pop(i)
                        print(f"\033[33m已移除: {removed}\033[0m")
                    else:
                        print(f"\033[31m序号 {i} 超出范围\033[0m")
            self.show_status()
        except ValueError:
            print("\033[31m错误: 请输入数字\033[0m")

    def run_cli(self):
        print("\n" + "=" * 40)
        print("系统已启动。操作指南:")
        print("  [n] 键 -> 触发截图拿牌 (并刷新状态)")
        print("  CLI命令: a(添加) / r(移除) / i(重载) / q(退出)")
        print("=" * 40)

        # 启动时先显示一次
        self.show_status()

        while self.running:
            try:
                # 提示符换行，避免和日志混在一起
                cmd = input("\n>>> ").lower().strip()
                if not cmd: continue

                if cmd == 'r':
                    idx_str = input('请输入要移除的英雄序号(空格隔开): ')
                    self.remove_hero_by_index(idx_str)
                elif cmd == 'a':
                    name = input('请输入要添加的英雄名称: ').strip()
                    if name: self.add_hero(name)
                elif cmd == 'i':
                    print("\033[33m正在重置阵容...\033[0m")
                    self.reload_lineup()
                    # 重载后自动显示状态
                    self.show_status()
                elif cmd == 'q':
                    print("正在退出...")
                    self.running = False
                else:
                    print("\033[31m未知命令\033[0m")
            except EOFError:
                break
            except Exception as e:
                print(f"CLI Error: {e}")

    def start(self):
        # 启动键盘监听
        listener = keyboard.Listener(on_press=self.on_key_press)
        listener.daemon = True
        listener.start()

        # 运行主循环
        self.run_cli()


if __name__ == '__main__':
    app = AutoPicker()
    app.start()