import os
from PIL import Image

class ResourceManager:
    """资源管理类：负责加载文件"""

    @staticmethod
    def load_hero_images(folder_path):
        """加载本地英雄图片库"""
        imgs = {}
        if not os.path.exists(folder_path):
            print(f"错误: 图片路径不存在 {folder_path}")
            return imgs

        print(f"正在加载图片资源: {folder_path} ...")
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                img_path = os.path.join(folder_path, filename)
                try:
                    # 使用 PIL 打开
                    img = Image.open(img_path)
                    # 强制加载图像数据，防止文件句柄占用
                    img.load()
                    name = os.path.splitext(filename)[0]
                    imgs[name] = img
                except Exception as e:
                    print(f"警告：无法加载图片 {filename} - {e}")
        return imgs

    @staticmethod
    def select_lineup(lineup_dir):
        """交互式选择阵容"""
        if not os.path.exists(lineup_dir):
            os.makedirs(lineup_dir)
            print(f"已创建阵容文件夹: {lineup_dir}，请放入txt文件。")
            return [], "无阵容"

        filenames = [f for f in os.listdir(lineup_dir) if f.endswith('.txt')]
        filenames.sort()

        if not filenames:
            print("警告: 阵容目录下没有txt文件。")
            return [], "无阵容"

        print('\n' + '=' * 30)
        print('       可用阵容列表')
        print('=' * 30)
        for i, filename in enumerate(filenames):
            print(f" [{i}] {filename}")
        print('=' * 30)

        while True:
            try:
                idx_str = input('请输入选择的阵容序号: ')
                idx = int(idx_str)
                if 0 <= idx < len(filenames):
                    target_file = filenames[idx]
                    break
                print("序号超出范围，请重试。")
            except ValueError:
                print("输入无效，请输入数字。")

        full_path = os.path.join(lineup_dir, target_file)
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                # 过滤空行和空白字符
                heros = [line.strip() for line in file if line.strip()]
            return heros, target_file
        except Exception as e:
            print(f"读取文件失败: {e}")
            return [], "读取失败"

