import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

from resource_manager import ResourceManager
from config import Config

class FeatureMatcher:
    def __init__(self,device='cpu'):
        # 使用ResNet-18作为特征提取器
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])  # 移除最后一层
        self.model.eval()
        self.device = torch.device(device)
        self.model.to(self.device)
        # 图像预处理
        self.preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    def extract_features(self, img):
        # 图像读取与预处理
        img_tensor = self.preprocess(img).unsqueeze(0).to(self.device)
        # 特征提取
        with torch.no_grad():
            features = self.model(img_tensor)
        # 展平并归一化特征向量
        features = features.squeeze().cpu().numpy()
        features /= np.linalg.norm(features)
        # print(features.shape)
        # print(features)
        return features

    def match_images(self, img, img_features:dict):
        # 提取查询图像特征
        query_feat = self.extract_features(img)
        best_name=''
        best_score=0
        for k,v in img_features.items():
            # 计算余弦相似度
            score = np.dot(query_feat, v)
            if score>best_score:
                best_score=score
                best_name=k
        # 此时得到最好的名字和分数
        return best_name,best_score

if __name__ == '__main__':
    matcher = FeatureMatcher(device='cuda')
    # 构建特征数据库（只需运行一次）
    img_dict = ResourceManager.load_hero_images(Config.pictrue_dir)
    img_features = {}
    for k, v in img_dict.items():
        img_features[k] = matcher.extract_features(v)

    # 执行查询
    img = Image.open(r'D:\D_disk\DATA\project\python_project\CV\JinChanChan_github\JinChanChan\pictures\嘉文四世.png')
    best_name,best_score=matcher.match_images(img, img_features)
    print(f"最佳匹配：{best_name}，相似度：{best_score}")






