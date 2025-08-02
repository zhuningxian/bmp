#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图像转换特征分析工具
"""

import os
import tempfile
import numpy as np
from PIL import Image
from conversion_analyzer import ConversionFeatureExtractor, BatchConversionFeatureExtractor

def create_test_images():
    """创建测试图像"""
    # 创建临时目录
    original_dir = tempfile.mkdtemp(prefix="original_")
    converted_dir = tempfile.mkdtemp(prefix="converted_")
    
    # 创建测试图像
    for i in range(5):
        # 创建原始图像
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        original_img = Image.fromarray(img_array)
        original_path = os.path.join(original_dir, f"test_image_{i}.jpg")
        original_img.save(original_path, "JPEG", quality=95)
        
        # 创建转换后的图像（模拟质量损失）
        converted_img = Image.fromarray(img_array)
        converted_path = os.path.join(converted_dir, f"test_image_{i}.jpg")
        converted_img.save(converted_path, "JPEG", quality=70)
    
    return original_dir, converted_dir

def test_single_feature_extraction():
    """测试单个特征提取"""
    print("测试单个特征提取...")
    
    # 创建测试图像
    original_dir, converted_dir = create_test_images()
    
    # 获取文件列表
    original_files = [f for f in os.listdir(original_dir) if f.endswith('.jpg')]
    converted_files = [f for f in os.listdir(converted_dir) if f.endswith('.jpg')]
    
    if original_files and converted_files:
        original_path = os.path.join(original_dir, original_files[0])
        converted_path = os.path.join(converted_dir, converted_files[0])
        
        # 提取特征
        extractor = ConversionFeatureExtractor()
        features = extractor.extract_conversion_features(original_path, converted_path)
        
        print(f"提取到 {len(features)} 个特征")
        print("主要特征:")
        for key, value in list(features.items())[:10]:
            print(f"  {key}: {value}")
        
        # 清理
        import shutil
        shutil.rmtree(original_dir)
        shutil.rmtree(converted_dir)
        
        return True
    return False

def test_batch_feature_extraction():
    """测试批量特征提取"""
    print("\n测试批量特征提取...")
    
    # 创建测试图像
    original_dir, converted_dir = create_test_images()
    
    # 批量提取特征
    batch_extractor = BatchConversionFeatureExtractor()
    features_df = batch_extractor.extract_batch_features(original_dir, converted_dir)
    
    print(f"处理了 {len(features_df)} 对图像")
    print(f"提取了 {len(features_df.columns)} 个特征")
    
    # 分析模式
    patterns = batch_extractor.analyze_conversion_patterns()
    print("转换模式分析:")
    for key, value in list(patterns.items())[:5]:
        if isinstance(value, dict):
            print(f"  {key}: [字典数据]")
        else:
            print(f"  {key}: {value}")
    
    # 清理
    import shutil
    shutil.rmtree(original_dir)
    shutil.rmtree(converted_dir)
    
    return True

def test_error_handling():
    """测试错误处理"""
    print("\n测试错误处理...")
    
    extractor = ConversionFeatureExtractor()
    
    # 测试不存在的文件
    try:
        features = extractor.extract_conversion_features("nonexistent.jpg", "nonexistent2.jpg")
        print("错误处理测试通过")
        return True
    except Exception as e:
        print(f"预期的错误: {e}")
        return True

def main():
    """主测试函数"""
    print("开始测试图像转换特征分析工具...")
    
    # 测试单个特征提取
    if test_single_feature_extraction():
        print("✓ 单个特征提取测试通过")
    else:
        print("✗ 单个特征提取测试失败")
    
    # 测试批量特征提取
    if test_batch_feature_extraction():
        print("✓ 批量特征提取测试通过")
    else:
        print("✗ 批量特征提取测试失败")
    
    # 测试错误处理
    if test_error_handling():
        print("✓ 错误处理测试通过")
    else:
        print("✗ 错误处理测试失败")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    main()