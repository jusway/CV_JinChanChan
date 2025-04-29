import os

import pyautogui
from PIL import Image

from config import Config


def load_imgs(folder_path):
    imgs = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img_path = os.path.join(folder_path, filename)
            # 读取图片
            img = Image.open(img_path)
            if img is not None:
                name=filename.split('.')[0]
                imgs[name]=img
            else:
                print(f"警告：无法加载图片 {filename}")
    return imgs

def get_heros(lineup_dir):
    # 读取文件内文件名
    filenames=[]
    for i,filename in enumerate(os.listdir(lineup_dir)):
        filenames.append(filename)
    # 排序
    filenames.sort()
    # 打印
    for i,filename in enumerate(filenames):
        print(i,":",filename)
    print('---------请输入阵容序号---------')
    idx = input('请输入选择阵容序号：')
    filename=filenames[int(idx)]
    heros_path=os.path.join(lineup_dir,filename)
    with open(heros_path, 'r', encoding='utf-8') as file:
        heros = [line.strip() for line in file]
    return heros,filename

def get_imgs(grab):
    # 得到当前5张图片
    img=None
    while img is None:
        img = grab.grab()
    # print('截图成功')
    sub_imgs = []
    x, y = Config.point
    for _ in range(5):
        sub_imgs.append(img[y:y + Config.h,
                        x:x + Config.w, :])
        x += Config.move
    return sub_imgs

def click(idx,name):
    x,y=Config.point
    pyautogui.moveTo(x+50+idx*Config.move, y+50, duration=0)
    for _ in range(2):
        pyautogui.mouseDown( button="left")
        # time.sleep(0.01)
        pyautogui.mouseUp(button="left")
        # time.sleep(0.01)
    print(f'\033[32m点击图片{idx + 1}{name}!\033[0m')
