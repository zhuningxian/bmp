#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 14:31:50 2025
QQ说说将JPEG图像转为JFIF格式的实现原理
@author: ubt
"""

import cv2
from pathlib import Path
import numpy as np
import os
import json
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from PIL.ExifTags import TAGS
import pandas as pd
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class ConversionFeatureExtractor:
    def __init__(self):
        self.feature_names = []
        self.conversion_patterns = {}
        self.feature_importance = {}
        
    def extract_conversion_features(self, original_path: str, converted_path: str) -> Dict:
        """提取转换特征"""
        features = {}
        
        # 1. 文件级特征
        features.update(self.extract_file_features(original_path, converted_path))
        
        # 2. 图像级特征
        features.update(self.extract_image_features(original_path, converted_path))
        
        # 3. 压缩特征
        features.update(self.extract_compression_features(original_path, converted_path))
        
        # 4. 质量特征
        features.update(self.extract_quality_features(original_path, converted_path))
        
        # 5. 统计特征
        features.update(self.extract_statistical_features(original_path, converted_path))
        
        return features

    def extract_file_features(self, original_path: str, converted_path: str) -> Dict:
        """提取文件级特征"""
        features = {}
        
        # 文件大小变化
        original_size = os.path.getsize(original_path)
        converted_size = os.path.getsize(converted_path)
        
        features['file_size_ratio'] = converted_size / original_size
        features['file_size_reduction'] = (original_size - converted_size) / original_size
        features['file_size_difference'] = original_size - converted_size
        
        # 文件格式信息
        original_format = self.get_image_format(original_path)
        converted_format = self.get_image_format(converted_path)
        
        features['format_change'] = 1 if original_format != converted_format else 0
        features['original_format'] = original_format
        features['converted_format'] = converted_format
        
        # 文件头分析
        features.update(self.analyze_file_headers(original_path, converted_path))
        
        return features

    def get_image_format(self, image_path: str) -> str:
        """获取图像格式"""
        try:
            with Image.open(image_path) as img:
                return img.format
        except:
            return os.path.splitext(image_path)[1].lower().replace('.', '')

    def analyze_file_headers(self, original_path: str, converted_path: str) -> Dict:
        """分析文件头信息"""
        features = {}
        
        # 读取文件头
        with open(original_path, 'rb') as f:
            original_header = f.read(16)
        
        with open(converted_path, 'rb') as f:
            converted_header = f.read(16)
        
        # 计算文件头差异
        features['header_similarity'] = self.calculate_similarity(original_header, converted_header)
        features['header_entropy_original'] = self.calculate_entropy(original_header)
        features['header_entropy_converted'] = self.calculate_entropy(converted_header)
        
        return features

    def calculate_similarity(self, data1: bytes, data2: bytes) -> float:
        """计算两个字节序列的相似度"""
        min_len = min(len(data1), len(data2))
        if min_len == 0:
            return 0.0
        
        matches = sum(1 for i in range(min_len) if data1[i] == data2[i])
        return matches / min_len

    def calculate_entropy(self, data: bytes) -> float:
        """计算数据的信息熵"""
        if len(data) == 0:
            return 0.0
        
        # 计算字节频率
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        
        # 计算熵
        entropy = 0.0
        for count in freq.values():
            p = count / len(data)
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy

    def extract_image_features(self, original_path: str, converted_path: str) -> Dict:
        """提取图像级特征"""
        features = {}
        
        # 加载图像
        original_img = cv2.imread(original_path)
        converted_img = cv2.imread(converted_path)
        
        if original_img is None or converted_img is None:
            return features
        
        # 尺寸变化
        original_shape = original_img.shape
        converted_shape = converted_img.shape
        
        features['size_change'] = 1 if original_shape != converted_shape else 0
        features['width_ratio'] = converted_shape[1] / original_shape[1]
        features['height_ratio'] = converted_shape[0] / original_shape[0]
        features['pixel_count_ratio'] = (converted_shape[0] * converted_shape[1]) / (original_shape[0] * original_shape[1])
        
        # 颜色空间分析
        features.update(self.analyze_color_space(original_img, converted_img))
        
        # 边缘检测对比
        features.update(self.analyze_edge_detection(original_img, converted_img))
        
        return features

    def analyze_color_space(self, original_img: np.ndarray, converted_img: np.ndarray) -> Dict:
        """分析颜色空间特征"""
        features = {}
        
        # 确保尺寸一致
        if original_img.shape != converted_img.shape:
            converted_img = cv2.resize(converted_img, (original_img.shape[1], original_img.shape[0]))
        
        # 转换为RGB
        original_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        converted_rgb = cv2.cvtColor(converted_img, cv2.COLOR_BGR2RGB)
        
        # 颜色直方图对比
        for i, color in enumerate(['red', 'green', 'blue']):
            original_hist = cv2.calcHist([original_rgb], [i], None, [256], [0, 256])
            converted_hist = cv2.calcHist([converted_rgb], [i], None, [256], [0, 256])
            
            # 直方图相似度
            similarity = cv2.compareHist(original_hist, converted_hist, cv2.HISTCMP_CORREL)
            features[f'{color}_histogram_similarity'] = similarity
            
            # 直方图差异
            diff = np.abs(original_hist - converted_hist)
            features[f'{color}_histogram_difference'] = np.mean(diff)
        
        return features

    def analyze_edge_detection(self, original_img: np.ndarray, converted_img: np.ndarray) -> Dict:
        """分析边缘检测特征"""
        features = {}
        
        # 确保尺寸一致
        if original_img.shape != converted_img.shape:
            converted_img = cv2.resize(converted_img, (original_img.shape[1], original_img.shape[0]))
        
        # 转换为灰度图
        original_gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        converted_gray = cv2.cvtColor(converted_img, cv2.COLOR_BGR2GRAY)
        
        # Canny边缘检测
        original_edges = cv2.Canny(original_gray, 100, 200)
        converted_edges = cv2.Canny(converted_gray, 100, 200)
        
        # 边缘像素数量比较
        original_edge_count = np.sum(original_edges > 0)
        converted_edge_count = np.sum(converted_edges > 0)
        
        features['edge_count_ratio'] = converted_edge_count / original_edge_count if original_edge_count > 0 else 0
        features['edge_preservation'] = np.sum(original_edges & converted_edges) / original_edge_count if original_edge_count > 0 else 0
        
        return features

    def extract_compression_features(self, original_path: str, converted_path: str) -> Dict:
        """提取压缩特征"""
        features = {}
        
        # JPEG质量分析
        features.update(self.analyze_jpeg_quality(original_path, converted_path))
        
        # 压缩伪影分析
        features.update(self.analyze_compression_artifacts(original_path, converted_path))
        
        # DCT系数分析
        features.update(self.analyze_dct_coefficients(original_path, converted_path))
        
        return features

    def analyze_jpeg_quality(self, original_path: str, converted_path: str) -> Dict:
        """分析JPEG质量"""
        features = {}
        
        # 使用PIL分析JPEG质量
        original_img = Image.open(original_path)
        converted_img = Image.open(converted_path)
        
        # 估计JPEG质量
        original_quality = self.estimate_jpeg_quality(original_img)
        converted_quality = self.estimate_jpeg_quality(converted_img)
        
        features['quality_ratio'] = converted_quality / original_quality if original_quality > 0 else 0
        features['quality_difference'] = original_quality - converted_quality
        features['quality_degradation'] = 1 if converted_quality < original_quality else 0
        
        return features

    def estimate_jpeg_quality(self, img: Image.Image) -> float:
        """估计JPEG质量"""
        try:
            # 尝试从EXIF数据获取质量信息
            if hasattr(img, 'quantization'):
                # 简化的质量估计算法
                qtables = img.quantization
                if qtables:
                    # 使用第一个量化表估计质量
                    qtable = list(qtables.values())[0]
                    quality = max(0, min(100, 100 - np.mean(qtable) / 50 * 100))
                    return quality
        except:
            pass
        
        # 默认质量估计
        return 85.0

    def analyze_compression_artifacts(self, original_path: str, converted_path: str) -> Dict:
        """分析压缩伪影"""
        features = {}
        
        original_img = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
        converted_img = cv2.imread(converted_path, cv2.IMREAD_GRAYSCALE)
        
        if original_img is None or converted_img is None:
            return features
        
        # 确保尺寸一致
        if original_img.shape != converted_img.shape:
            converted_img = cv2.resize(converted_img, (original_img.shape[1], original_img.shape[0]))
        
        # 块效应分析
        original_blocks = self.detect_blocking_artifacts(original_img)
        converted_blocks = self.detect_blocking_artifacts(converted_img)
        
        features['blocking_artifacts_ratio'] = converted_blocks / original_blocks if original_blocks > 0 else 0
        features['blocking_artifacts_difference'] = converted_blocks - original_blocks
        
        # 振铃效应分析
        original_ringing = self.detect_ringing_artifacts(original_img)
        converted_ringing = self.detect_ringing_artifacts(converted_img)
        
        features['ringing_artifacts_ratio'] = converted_ringing / original_ringing if original_ringing > 0 else 0
        features['ringing_artifacts_difference'] = converted_ringing - original_ringing
        
        return features

    def detect_blocking_artifacts(self, img: np.ndarray) -> float:
        """检测块效应伪影"""
        # 检测8x8块边界的不连续性
        h, w = img.shape
        blocking_score = 0.0
        count = 0
        
        # 垂直边界
        for i in range(8, h, 8):
            if i < h:
                diff = np.abs(img[i-1, :].astype(float) - img[i, :].astype(float))
                blocking_score += np.mean(diff)
                count += 1
        
        # 水平边界
        for j in range(8, w, 8):
            if j < w:
                diff = np.abs(img[:, j-1].astype(float) - img[:, j].astype(float))
                blocking_score += np.mean(diff)
                count += 1
        
        return blocking_score / count if count > 0 else 0.0

    def detect_ringing_artifacts(self, img: np.ndarray) -> float:
        """检测振铃效应伪影"""
        # 使用拉普拉斯算子检测振铃效应
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        return np.var(laplacian)

    def analyze_dct_coefficients(self, original_path: str, converted_path: str) -> Dict:
        """分析DCT系数"""
        features = {}
        
        original_img = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
        converted_img = cv2.imread(converted_path, cv2.IMREAD_GRAYSCALE)
        
        if original_img is None or converted_img is None:
            return features
        
        # 确保尺寸一致
        if original_img.shape != converted_img.shape:
            converted_img = cv2.resize(converted_img, (original_img.shape[1], original_img.shape[0]))
        
        # 计算DCT
        original_dct = cv2.dct(np.float32(original_img))
        converted_dct = cv2.dct(np.float32(converted_img))
        
        # DCT系数差异
        dct_diff = np.abs(original_dct - converted_dct)
        features['dct_difference_mean'] = np.mean(dct_diff)
        features['dct_difference_std'] = np.std(dct_diff)
        
        # 高频系数保持度
        h, w = original_dct.shape
        high_freq_original = original_dct[h//2:, w//2:]
        high_freq_converted = converted_dct[h//2:, w//2:]
        
        correlation = np.corrcoef(high_freq_original.flatten(), high_freq_converted.flatten())[0, 1]
        features['high_freq_correlation'] = correlation if not np.isnan(correlation) else 0.0
        
        return features

    def extract_quality_features(self, original_path: str, converted_path: str) -> Dict:
        """提取质量特征"""
        features = {}
        
        original_img = cv2.imread(original_path)
        converted_img = cv2.imread(converted_path)
        
        if original_img is None or converted_img is None:
            return features
        
        # 确保尺寸一致
        if original_img.shape != converted_img.shape:
            converted_img = cv2.resize(converted_img, (original_img.shape[1], original_img.shape[0]))
        
        # PSNR (Peak Signal-to-Noise Ratio)
        features['psnr'] = self.calculate_psnr(original_img, converted_img)
        
        # SSIM (Structural Similarity Index)
        features['ssim'] = self.calculate_ssim(original_img, converted_img)
        
        # MSE (Mean Squared Error)
        features['mse'] = self.calculate_mse(original_img, converted_img)
        
        # 信息熵
        features['entropy_original'] = self.calculate_image_entropy(original_img)
        features['entropy_converted'] = self.calculate_image_entropy(converted_img)
        features['entropy_difference'] = features['entropy_original'] - features['entropy_converted']
        
        return features

    def calculate_psnr(self, original: np.ndarray, converted: np.ndarray) -> float:
        """计算PSNR"""
        mse = np.mean((original.astype(float) - converted.astype(float)) ** 2)
        if mse == 0:
            return float('inf')
        return 20 * np.log10(255.0 / np.sqrt(mse))

    def calculate_ssim(self, original: np.ndarray, converted: np.ndarray) -> float:
        """计算SSIM"""
        # 转换为灰度图
        if len(original.shape) == 3:
            original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        if len(converted.shape) == 3:
            converted = cv2.cvtColor(converted, cv2.COLOR_BGR2GRAY)
        
        # 简化的SSIM计算
        mu1 = np.mean(original)
        mu2 = np.mean(converted)
        sigma1 = np.var(original)
        sigma2 = np.var(converted)
        sigma12 = np.mean((original - mu1) * (converted - mu2))
        
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        
        ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / ((mu1 ** 2 + mu2 ** 2 + c1) * (sigma1 + sigma2 + c2))
        return ssim

    def calculate_mse(self, original: np.ndarray, converted: np.ndarray) -> float:
        """计算MSE"""
        return np.mean((original.astype(float) - converted.astype(float)) ** 2)

    def calculate_image_entropy(self, img: np.ndarray) -> float:
        """计算图像熵"""
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 计算直方图
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # 归一化
        hist = hist / np.sum(hist)
        
        # 计算熵
        entropy = 0.0
        for p in hist:
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy

    def extract_statistical_features(self, original_path: str, converted_path: str) -> Dict:
        """提取统计特征"""
        features = {}
        
        original_img = cv2.imread(original_path)
        converted_img = cv2.imread(converted_path)
        
        if original_img is None or converted_img is None:
            return features
        
        # 确保尺寸一致
        if original_img.shape != converted_img.shape:
            converted_img = cv2.resize(converted_img, (original_img.shape[1], original_img.shape[0]))
        
        # 像素值统计
        features.update(self.analyze_pixel_statistics(original_img, converted_img))
        
        # 梯度统计
        features.update(self.analyze_gradient_statistics(original_img, converted_img))
        
        # 纹理统计
        features.update(self.analyze_texture_statistics(original_img, converted_img))
        
        return features

    def analyze_pixel_statistics(self, original: np.ndarray, converted: np.ndarray) -> Dict:
        """分析像素统计特征"""
        features = {}
        
        # 均值对比
        original_mean = np.mean(original)
        converted_mean = np.mean(converted)
        features['mean_difference'] = original_mean - converted_mean
        features['mean_ratio'] = converted_mean / original_mean if original_mean > 0 else 0
        
        # 标准差对比
        original_std = np.std(original)
        converted_std = np.std(converted)
        features['std_difference'] = original_std - converted_std
        features['std_ratio'] = converted_std / original_std if original_std > 0 else 0
        
        # 偏度和峰度
        original_skew = self.calculate_skewness(original)
        converted_skew = self.calculate_skewness(converted)
        features['skewness_difference'] = original_skew - converted_skew
        
        original_kurtosis = self.calculate_kurtosis(original)
        converted_kurtosis = self.calculate_kurtosis(converted)
        features['kurtosis_difference'] = original_kurtosis - converted_kurtosis
        
        return features

    def calculate_skewness(self, data: np.ndarray) -> float:
        """计算偏度"""
        data_flat = data.flatten()
        mean = np.mean(data_flat)
        std = np.std(data_flat)
        if std == 0:
            return 0.0
        
        skewness = np.mean(((data_flat - mean) / std) ** 3)
        return skewness

    def calculate_kurtosis(self, data: np.ndarray) -> float:
        """计算峰度"""
        data_flat = data.flatten()
        mean = np.mean(data_flat)
        std = np.std(data_flat)
        if std == 0:
            return 0.0
        
        kurtosis = np.mean(((data_flat - mean) / std) ** 4) - 3
        return kurtosis

    def analyze_gradient_statistics(self, original: np.ndarray, converted: np.ndarray) -> Dict:
        """分析梯度统计特征"""
        features = {}
        
        # 转换为灰度图
        if len(original.shape) == 3:
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        else:
            original_gray = original
            
        if len(converted.shape) == 3:
            converted_gray = cv2.cvtColor(converted, cv2.COLOR_BGR2GRAY)
        else:
            converted_gray = converted
        
        # 计算梯度
        original_grad_x = cv2.Sobel(original_gray, cv2.CV_64F, 1, 0, ksize=3)
        original_grad_y = cv2.Sobel(original_gray, cv2.CV_64F, 0, 1, ksize=3)
        original_grad_mag = np.sqrt(original_grad_x**2 + original_grad_y**2)
        
        converted_grad_x = cv2.Sobel(converted_gray, cv2.CV_64F, 1, 0, ksize=3)
        converted_grad_y = cv2.Sobel(converted_gray, cv2.CV_64F, 0, 1, ksize=3)
        converted_grad_mag = np.sqrt(converted_grad_x**2 + converted_grad_y**2)
        
        # 梯度统计
        features['gradient_mean_difference'] = np.mean(original_grad_mag) - np.mean(converted_grad_mag)
        features['gradient_std_difference'] = np.std(original_grad_mag) - np.std(converted_grad_mag)
        features['gradient_correlation'] = np.corrcoef(original_grad_mag.flatten(), converted_grad_mag.flatten())[0, 1]
        
        # 处理NaN值
        if np.isnan(features['gradient_correlation']):
            features['gradient_correlation'] = 0.0
        
        return features

    def analyze_texture_statistics(self, original: np.ndarray, converted: np.ndarray) -> Dict:
        """分析纹理统计特征"""
        features = {}
        
        # 转换为灰度图
        if len(original.shape) == 3:
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        else:
            original_gray = original
            
        if len(converted.shape) == 3:
            converted_gray = cv2.cvtColor(converted, cv2.COLOR_BGR2GRAY)
        else:
            converted_gray = converted
        
        # LBP (Local Binary Pattern) 简化实现
        original_lbp = self.calculate_lbp(original_gray)
        converted_lbp = self.calculate_lbp(converted_gray)
        
        # LBP统计
        features['lbp_mean_difference'] = np.mean(original_lbp) - np.mean(converted_lbp)
        features['lbp_std_difference'] = np.std(original_lbp) - np.std(converted_lbp)
        
        # 纹理能量
        original_energy = np.sum(original_gray.astype(float) ** 2)
        converted_energy = np.sum(converted_gray.astype(float) ** 2)
        features['texture_energy_ratio'] = converted_energy / original_energy if original_energy > 0 else 0
        
        return features

    def calculate_lbp(self, img: np.ndarray) -> np.ndarray:
        """计算简化的LBP特征"""
        h, w = img.shape
        lbp = np.zeros((h-2, w-2), dtype=np.uint8)
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                center = img[i, j]
                code = 0
                code |= (img[i-1, j-1] >= center) << 7
                code |= (img[i-1, j] >= center) << 6
                code |= (img[i-1, j+1] >= center) << 5
                code |= (img[i, j+1] >= center) << 4
                code |= (img[i+1, j+1] >= center) << 3
                code |= (img[i+1, j] >= center) << 2
                code |= (img[i+1, j-1] >= center) << 1
                code |= (img[i, j-1] >= center) << 0
                lbp[i-1, j-1] = code
        
        return lbp


class BatchConversionFeatureExtractor:
    def __init__(self):
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        self.extractor = ConversionFeatureExtractor()
        self.features_dataset = pd.DataFrame()
    
    def get_image_files(self, directory):
        """递归获取目录下所有图像文件"""
        from pathlib import Path
        return sorted(
            str(p) for p in Path(directory).rglob('*')
            if p.suffix.lower() in self.supported_extensions
        )
    
    def match_files(self, original_files, converted_files):
        """匹配原始文件和转换后的文件"""
        orig_map = {Path(f).stem: f for f in original_files}
        conv_map = {Path(f).stem: f for f in converted_files}
        common = set(orig_map) & set(conv_map)
        return [(orig_map[s], conv_map[s]) for s in common]
        
    def extract_batch_features(self, original_dir: str, converted_dir: str) -> pd.DataFrame:
        """批量提取转换特征"""
        features_list = []
        
        # 获取文件列表
        original_files = self.get_image_files(original_dir)
        converted_files = self.get_image_files(converted_dir)
        
        # 匹配文件对
        file_pairs = self.match_files(original_files, converted_files)
        
        print(f"开始提取 {len(file_pairs)} 对图像的特征...")
        
        for original_file, converted_file in file_pairs:
            try:
                features = self.extractor.extract_conversion_features(original_file, converted_file)
                features['original_file'] = os.path.basename(original_file)
                features['converted_file'] = os.path.basename(converted_file)
                features_list.append(features)
                
                print(f"已处理: {os.path.basename(original_file)}")
                
            except Exception as e:
                print(f"处理失败 {original_file}: {e}")
                continue
        
        # 转换为DataFrame
        df = pd.DataFrame(features_list)
        self.features_dataset = df
        
        return df
    
    def analyze_conversion_patterns(self) -> Dict:
        """分析转换模式"""
        if self.features_dataset.empty:
            return {}
        
        patterns = {}
        
        # 统计转换特征
        numeric_columns = self.features_dataset.select_dtypes(include=[np.number]).columns
        
        if 'file_size_reduction' in numeric_columns:
            patterns['file_size_reduction_mean'] = self.features_dataset['file_size_reduction'].mean()
        if 'quality_degradation' in numeric_columns:
            patterns['quality_degradation_rate'] = self.features_dataset['quality_degradation'].mean()
        if 'format_change' in numeric_columns:
            patterns['format_change_rate'] = self.features_dataset['format_change'].mean()
        
        # 特征相关性分析
        numeric_df = self.features_dataset.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            patterns['correlations'] = numeric_df.corr().to_dict()
        
        return patterns
    
    def visualize_conversion_features(self, save_path: str = None):
        """可视化转换特征"""
        if self.features_dataset.empty:
            print("没有数据可可视化")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 文件大小变化分布
        if 'file_size_reduction' in self.features_dataset.columns:
            axes[0, 0].hist(self.features_dataset['file_size_reduction'], bins=20, alpha=0.7)
            axes[0, 0].set_title('文件大小减少分布')
            axes[0, 0].set_xlabel('大小减少比例')
            axes[0, 0].set_ylabel('频次')
        
        # 质量变化分布
        if 'psnr' in self.features_dataset.columns:
            axes[0, 1].hist(self.features_dataset['psnr'], bins=20, alpha=0.7)
            axes[0, 1].set_title('PSNR分布')
            axes[0, 1].set_xlabel('PSNR值')
            axes[0, 1].set_ylabel('频次')
        
        # 文件大小与质量关系
        if 'file_size_reduction' in self.features_dataset.columns and 'psnr' in self.features_dataset.columns:
            axes[1, 0].scatter(self.features_dataset['file_size_reduction'], self.features_dataset['psnr'], alpha=0.6)
            axes[1, 0].set_title('文件大小减少 vs PSNR')
            axes[1, 0].set_xlabel('文件大小减少比例')
            axes[1, 0].set_ylabel('PSNR')
        
        # 特征相关性热图
        numeric_df = self.features_dataset.select_dtypes(include=[np.number])
        if not numeric_df.empty and numeric_df.shape[1] > 1:
            corr_matrix = numeric_df.corr()
            # 选择前10个特征进行可视化
            if corr_matrix.shape[0] > 10:
                corr_matrix = corr_matrix.iloc[:10, :10]
            sns.heatmap(corr_matrix, ax=axes[1, 1], cmap='coolwarm', center=0, annot=True, fmt='.2f')
            axes[1, 1].set_title('特征相关性热图')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


def main():
    # 初始化批量特征提取器
    batch_extractor = BatchConversionFeatureExtractor()
    
    # 设置路径
    original_dir = "/home/ubt/notebook/ForensicImage/sns/hornor9/camera1"
    converted_dir = "/home/ubt/notebook/ForensicImage/sns/hornor9/camera2"
    
    # 检查目录是否存在
    if not os.path.exists(original_dir):
        print(f"原始目录不存在: {original_dir}")
        return
    
    if not os.path.exists(converted_dir):
        print(f"转换目录不存在: {converted_dir}")
        return
    
    # 批量提取特征
    features_df = batch_extractor.extract_batch_features(original_dir, converted_dir)
    
    if features_df.empty:
        print("没有提取到特征数据")
        return
    
    # 保存特征数据
    features_df.to_csv("conversion_features.csv", index=False)
    print(f"特征数据已保存到 conversion_features.csv，共 {len(features_df)} 条记录")
    
    # 分析转换模式
    patterns = batch_extractor.analyze_conversion_patterns()
    print("转换模式分析结果:")
    for key, value in patterns.items():
        if key != 'correlations':
            print(f"{key}: {value}")
    
    # 保存分析结果
    with open("conversion_patterns.json", "w", encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False, default=str)
    
    # 可视化特征
    batch_extractor.visualize_conversion_features("conversion_features_analysis.png")
    
    print("特征提取完成！")

if __name__ == "__main__":
    main()