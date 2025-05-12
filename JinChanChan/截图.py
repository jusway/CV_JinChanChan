import dxcam
from config import Config
from PIL import Image

from utils import get_imgs


def main():
    grab=dxcam.create(output_idx=Config.output_idx,output_color='RGB')
    sub_imgs=get_imgs(grab)

    # 保存
    for i,sub_img in enumerate(sub_imgs):
        sub_img=Image.fromarray(sub_img)
        sub_img.save(f'img_{i}.png')


if __name__ == '__main__':
    main()
