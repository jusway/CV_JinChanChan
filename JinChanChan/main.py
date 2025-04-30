import threading
from time import sleep

import dxcam
from config import Config
from feature_matcher import FeatureMatcher
from utils import load_imgs, get_heros, get_imgs, click
from pynput import keyboard
hero_lock = threading.Lock()  # 线程锁
# 截图器
grab = dxcam.create(output_idx=Config.output_idx, output_color='RGB')
# 初始化匹配器
print('---正在加载模型---')
matcher = FeatureMatcher(device='cuda')
# 构建特征数据库（只需运行一次）
img_dict = load_imgs(Config.pictrue_dir)  # imgs {name:ndarray}
img_features = {} # 向量数据库
for k, v in img_dict.items():
    img_features[k] = matcher.extract_features(v)
# 准备阵容
heros,filename=get_heros(Config.lineup_dir)
def heros_show():
    global heros,filename
    print(f"---> {filename}")
    for id, item in enumerate(heros):
        print(id, item, ' ', end="")
    print()
    print('*' * 30)
heros_show()

def on_press_n(key):
    global img_features,matcher,grab
    try:
        if key.char == 'n':
            #  截图
            sub_imgs = get_imgs(grab)
            for i, img in enumerate(sub_imgs):
                hero_name, best_score = matcher.match_images(img, img_features)
                print(f'{i + 1} {hero_name} {round(best_score.item(), 2)}  ')
                # 点击
                if hero_name  in heros:
                    click(i,hero_name)
            heros_show()
    except AttributeError:
        pass

def remove_hero_by_name(name):
    global heros
    if name in heros:
        heros.remove(name)
        print(f"\033[33m已移除: {name}\033[0m")

def command_handler():
    while True:
        cmd = input("\n>>> 请输入命令 (r-移除英雄/a-添加英雄/i-重来): ").lower()
        if cmd == 'r':
            try:
                names = [heros[int(i)] for i in input('请输入要移除的英雄序号,用空格隔开: ').split()]
                with hero_lock:
                    for name in names:
                        remove_hero_by_name(name)
                heros_show()
            except ValueError:
                print("\033[31m错误: 请输入数字\033[0m")
        elif cmd == 'a':
            name = input('请输入要添加的英雄名称: ').strip()
            with hero_lock:
                heros.insert(0, name)
                print(f"\033[33m已添加: {name}\033[0m")
            heros_show()
        elif cmd == 'i':
            heros.clear()
            add_heros()
        else:
            print("\033[31m未知命令\033[0m")
            heros_show()

def add_heros():
    global heros, filename
    tmp_heros_list, name = get_heros(Config.lineup_dir)
    filename = name
    with hero_lock:
        for name in tmp_heros_list:
            if name in heros:
                continue
            heros.append(name)
            print(f"\033[33m已添加: {name}\033[0m")
    heros_show()


if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_press_n)
    listener.daemon = True  # 设为守护线程
    listener.start()
    # 启动命令处理线程
    cmd_thread = threading.Thread(target=command_handler, daemon=True)
    cmd_thread.start()
    while True:
        sleep(0.1)



