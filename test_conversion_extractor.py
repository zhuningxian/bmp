#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图像转换特征提取器
Test script for image conversion feature extractor
"""

import os
import cv2
import numpy as np
from PIL import Image
from conversion_feature_extractor import ConversionFeatureExtractor, BatchConversionFeatureExtractor


def create_sample_images():
    """创建示例图像用于测试"""
    # 创建测试目录
    os.makedirs("test_images/original", exist_ok=True)
    os.makedirs("test_images/converted", exist_ok=True)
    
    # 生成几个测试图像
    for i in range(5):
        # 创建随机图像
        img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        
        # 添加一些结构化的内容
        cv2.rectangle(img, (50, 50), (200, 200), (255, 255, 255), 2)
        cv2.circle(img, (128, 128), 30, (0, 255, 0), -1)
        
        # 保存原始图像
        original_path = f"test_images/original/test_{i}.jpg"
        cv2.imwrite(original_path, img)
        
        # 创建"转换"后的图像（添加噪声和压缩）
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        converted_img = cv2.add(img, noise)
        
        # 模拟JPEG压缩
        converted_path = f"test_images/converted/test_{i}.jpg"
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # 降低质量
        cv2.imwrite(converted_path, converted_img, encode_param)
    
    print("示例图像创建完成")


def test_single_conversion():
    """测试单个图像对的特征提取"""
    print("\n=== 测试单个图像转换特征提取 ===")
    
    extractor = ConversionFeatureExtractor()
    
    original_path = "test_images/original/test_0.jpg"
    converted_path = "test_images/converted/test_0.jpg"
    
    if not os.path.exists(original_path) or not os.path.exists(converted_path):
        print("测试图像不存在，先创建示例图像")
        create_sample_images()
    
    # 提取特征
    features = extractor.extract_conversion_features(original_path, converted_path)
    
    print(f"提取到 {len(features)} 个特征:")
    for key, value in features.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")


def test_batch_conversion():
    """测试批量特征提取"""
    print("\n=== 测试批量图像转换特征提取 ===")
    
    batch_extractor = BatchConversionFeatureExtractor()
    
    # 确保测试图像存在
    if not os.path.exists("test_images/original") or not os.path.exists("test_images/converted"):
        create_sample_images()
    
    # 批量提取特征
    features_df = batch_extractor.extract_batch_features("test_images/original", "test_images/converted")
    
    if not features_df.empty:
        print(f"成功提取 {len(features_df)} 个图像对的特征")
        print(f"特征维度: {features_df.shape}")
        print("\n特征列名:")
        for col in features_df.columns:
            print(f"  {col}")
        
        # 分析转换模式
        patterns = batch_extractor.analyze_conversion_patterns()
        print("\n转换模式分析:")
        for key, value in patterns.items():
            if key != 'correlations' and isinstance(value, (int, float)):
                print(f"  {key}: {value:.4f}")
        
        # 保存结果
        features_df.to_csv("test_conversion_features.csv", index=False)
        print("\n特征数据已保存到 test_conversion_features.csv")
        
        # 可视化（如果有足够的数据）
        try:
            batch_extractor.visualize_conversion_features("test_conversion_analysis.png")
            print("可视化结果已保存到 test_conversion_analysis.png")
        except Exception as e:
            print(f"可视化失败: {e}")
    else:
        print("没有提取到特征数据")


def analyze_jpeg_conversion():
    """分析JPEG转换的具体特征"""
    print("\n=== JPEG转换特征分析 ===")
    
    # 创建高质量和低质量的JPEG图像
    original_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    
    # 添加详细纹理
    for i in range(0, 512, 8):
        for j in range(0, 512, 8):
            cv2.rectangle(original_img, (j, i), (j+4, i+4), (255, 255, 255), 1)
    
    # 保存高质量版本
    high_quality_path = "test_high_quality.jpg"
    encode_param_high = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
    cv2.imwrite(high_quality_path, original_img, encode_param_high)
    
    # 保存低质量版本
    low_quality_path = "test_low_quality.jpg"
    encode_param_low = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
    cv2.imwrite(low_quality_path, original_img, encode_param_low)
    
    # 分析质量差异
    extractor = ConversionFeatureExtractor()
    features = extractor.extract_conversion_features(high_quality_path, low_quality_path)
    
    print("高质量 -> 低质量 JPEG 转换特征:")
    quality_features = {k: v for k, v in features.items() 
                       if any(keyword in k.lower() for keyword in ['quality', 'psnr', 'ssim', 'mse', 'blocking', 'ringing'])}
    
    for key, value in quality_features.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    # 清理临时文件
    os.remove(high_quality_path)
    os.remove(low_quality_path)


def demonstrate_format_conversion():
    """演示不同格式之间的转换分析"""
    print("\n=== 格式转换分析 ===")
    
    # 创建测试图像
    img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (200, 200), (128, 128, 128), -1)
    cv2.circle(img, (128, 128), 50, (255, 255, 255), 2)
    
    # 保存为不同格式
    jpeg_path = "test_format.jpg"
    png_path = "test_format.png"
    webp_path = "test_format.webp"
    
    cv2.imwrite(jpeg_path, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    cv2.imwrite(png_path, img)
    cv2.imwrite(webp_path, img, [cv2.IMWRITE_WEBP_QUALITY, 85])
    
    extractor = ConversionFeatureExtractor()
    
    # JPEG -> PNG
    print("JPEG -> PNG 转换:")
    features_jp = extractor.extract_conversion_features(jpeg_path, png_path)
    print(f"  文件大小比例: {features_jp.get('file_size_ratio', 'N/A'):.4f}")
    print(f"  格式变化: {features_jp.get('format_change', 'N/A')}")
    print(f"  PSNR: {features_jp.get('psnr', 'N/A'):.4f}")
    
    # PNG -> WebP
    print("\nPNG -> WebP 转换:")
    features_pw = extractor.extract_conversion_features(png_path, webp_path)
    print(f"  文件大小比例: {features_pw.get('file_size_ratio', 'N/A'):.4f}")
    print(f"  格式变化: {features_pw.get('format_change', 'N/A')}")
    print(f"  PSNR: {features_pw.get('psnr', 'N/A'):.4f}")
    
    # 清理文件
    for path in [jpeg_path, png_path, webp_path]:
        if os.path.exists(path):
            os.remove(path)


def main():
    """主测试函数"""
    print("图像转换特征提取器测试")
    print("=" * 50)
    
    try:
        # 测试单个图像转换
        test_single_conversion()
        
        # 测试批量转换
        test_batch_conversion()
        
        # 分析JPEG压缩特征
        analyze_jpeg_conversion()
        
        # 演示格式转换
        demonstrate_format_conversion()
        
        print("\n所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理测试文件
    finally:
        cleanup_test_files()


def cleanup_test_files():
    """清理测试文件"""
    import shutil
    test_dirs = ["test_images"]
    test_files = ["test_conversion_features.csv", "test_conversion_analysis.png"]
    
    for directory in test_dirs:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    print("测试文件已清理")


if __name__ == "__main__":
    main()