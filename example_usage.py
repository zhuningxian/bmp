#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像转换特征分析工具使用示例
"""

import os
import tempfile
import numpy as np
from PIL import Image
from conversion_analyzer import ConversionFeatureExtractor, BatchConversionFeatureExtractor

def create_sample_data():
    """创建示例数据"""
    print("创建示例数据...")
    
    # 创建临时目录
    original_dir = tempfile.mkdtemp(prefix="original_")
    converted_dir = tempfile.mkdtemp(prefix="converted_")
    
    # 创建不同类型的测试图像
    for i in range(10):
        # 创建原始图像 - 高质量
        if i < 5:
            # 创建彩色图像
            img_array = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        else:
            # 创建灰度图像
            img_array = np.random.randint(0, 255, (150, 150), dtype=np.uint8)
        
        original_img = Image.fromarray(img_array)
        original_path = os.path.join(original_dir, f"sample_image_{i:02d}.jpg")
        original_img.save(original_path, "JPEG", quality=95)
        
        # 创建转换后的图像 - 模拟不同质量损失
        converted_img = Image.fromarray(img_array)
        converted_path = os.path.join(converted_dir, f"sample_image_{i:02d}.jpg")
        
        # 模拟不同的转换质量
        quality = 70 if i < 5 else 60
        converted_img.save(converted_path, "JPEG", quality=quality)
    
    print(f"创建了 {len(os.listdir(original_dir))} 对测试图像")
    return original_dir, converted_dir

def demonstrate_single_analysis():
    """演示单个图像分析"""
    print("\n=== 单个图像特征分析 ===")
    
    # 创建示例数据
    original_dir, converted_dir = create_sample_data()
    
    # 获取第一对图像
    original_files = sorted([f for f in os.listdir(original_dir) if f.endswith('.jpg')])
    if original_files:
        original_path = os.path.join(original_dir, original_files[0])
        converted_path = os.path.join(converted_dir, original_files[0])
        
        # 创建特征提取器
        extractor = ConversionFeatureExtractor()
        
        # 提取特征
        features = extractor.extract_conversion_features(original_path, converted_path)
        
        print(f"分析图像: {original_files[0]}")
        print(f"提取到 {len(features)} 个特征")
        
        # 显示主要特征
        print("\n主要特征:")
        key_features = [
            'file_size_ratio', 'file_size_reduction', 'psnr', 'ssim', 
            'quality_ratio', 'entropy_difference', 'mean_difference'
        ]
        
        for key in key_features:
            if key in features:
                value = features[key]
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
        
        # 清理
        import shutil
        shutil.rmtree(original_dir)
        shutil.rmtree(converted_dir)
        
        return features
    return None

def demonstrate_batch_analysis():
    """演示批量分析"""
    print("\n=== 批量图像特征分析 ===")
    
    # 创建示例数据
    original_dir, converted_dir = create_sample_data()
    
    # 创建批量特征提取器
    batch_extractor = BatchConversionFeatureExtractor()
    
    # 批量提取特征
    print("开始批量特征提取...")
    features_df = batch_extractor.extract_batch_features(original_dir, converted_dir)
    
    print(f"处理了 {len(features_df)} 对图像")
    print(f"提取了 {len(features_df.columns)} 个特征")
    
    # 显示统计信息
    print("\n统计信息:")
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    for col in ['file_size_ratio', 'psnr', 'ssim', 'quality_ratio']:
        if col in numeric_cols:
            mean_val = features_df[col].mean()
            std_val = features_df[col].std()
            print(f"  {col}: 均值={mean_val:.4f}, 标准差={std_val:.4f}")
    
    # 分析转换模式
    patterns = batch_extractor.analyze_conversion_patterns()
    print(f"\n转换模式分析完成，包含 {len(patterns)} 个统计指标")
    
    # 可视化（如果可能）
    try:
        print("\n生成可视化图表...")
        batch_extractor.visualize_conversion_features("sample_analysis.png")
        print("可视化图表已保存为 sample_analysis.png")
    except Exception as e:
        print(f"可视化失败: {e}")
    
    # 保存结果
    features_df.to_csv("sample_features.csv", index=False)
    print("特征数据已保存为 sample_features.csv")
    
    # 清理
    import shutil
    shutil.rmtree(original_dir)
    shutil.rmtree(converted_dir)
    
    return features_df

def demonstrate_custom_analysis():
    """演示自定义分析"""
    print("\n=== 自定义特征分析 ===")
    
    # 创建示例数据
    original_dir, converted_dir = create_sample_data()
    
    # 获取文件列表
    original_files = sorted([f for f in os.listdir(original_dir) if f.endswith('.jpg')])
    
    if len(original_files) >= 3:
        # 分析前3个图像
        extractor = ConversionFeatureExtractor()
        results = []
        
        for i in range(3):
            original_path = os.path.join(original_dir, original_files[i])
            converted_path = os.path.join(converted_dir, original_files[i])
            
            features = extractor.extract_conversion_features(original_path, converted_path)
            results.append({
                'image': original_files[i],
                'file_size_ratio': features.get('file_size_ratio', 0),
                'psnr': features.get('psnr', 0),
                'ssim': features.get('ssim', 0),
                'quality_ratio': features.get('quality_ratio', 0)
            })
        
        print("自定义分析结果:")
        for result in results:
            print(f"  {result['image']}:")
            print(f"    文件大小比例: {result['file_size_ratio']:.4f}")
            print(f"    PSNR: {result['psnr']:.2f}")
            print(f"    SSIM: {result['ssim']:.4f}")
            print(f"    质量比例: {result['quality_ratio']:.4f}")
        
        # 清理
        import shutil
        shutil.rmtree(original_dir)
        shutil.rmtree(converted_dir)
        
        return results
    return None

def main():
    """主函数"""
    print("图像转换特征分析工具使用示例")
    print("=" * 50)
    
    try:
        # 演示单个图像分析
        single_features = demonstrate_single_analysis()
        
        # 演示批量分析
        batch_features = demonstrate_batch_analysis()
        
        # 演示自定义分析
        custom_results = demonstrate_custom_analysis()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        print("\n生成的文件:")
        print("  - sample_features.csv: 批量特征数据")
        print("  - sample_analysis.png: 可视化图表")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()