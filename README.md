# 图像转换特征分析工具

这个工具用于分析JPEG图像转换为JFIF格式时的特征变化，特别适用于数字取证和图像处理研究。

## 功能特性

### 1. 多维度特征提取
- **文件级特征**: 文件大小变化、格式信息、文件头分析
- **图像级特征**: 尺寸变化、颜色空间分析、边缘检测
- **压缩特征**: JPEG质量分析、压缩伪影检测、DCT系数分析
- **质量特征**: PSNR、SSIM、MSE、信息熵
- **统计特征**: 像素统计、梯度分析、纹理分析

### 2. 批量处理能力
- 支持批量处理大量图像文件
- 自动匹配原始文件和转换后的文件
- 生成详细的特征报告

### 3. 可视化分析
- 文件大小变化分布
- 质量指标分布
- 特征相关性热图
- 文件大小与质量关系图

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

1. 准备数据目录结构：
```
data/
├── original/     # 原始图像目录
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── converted/    # 转换后的图像目录
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

2. 修改脚本中的路径：
```python
original_dir = "path/to/original/images"
converted_dir = "path/to/converted/images"
```

3. 运行分析：
```bash
python conversion_analyzer.py
```

### 高级使用

#### 自定义特征提取
```python
from conversion_analyzer import ConversionFeatureExtractor

extractor = ConversionFeatureExtractor()
features = extractor.extract_conversion_features("original.jpg", "converted.jpg")
print(features)
```

#### 批量分析
```python
from conversion_analyzer import BatchConversionFeatureExtractor

batch_extractor = BatchConversionFeatureExtractor()
features_df = batch_extractor.extract_batch_features("original_dir", "converted_dir")

# 保存结果
features_df.to_csv("features.csv", index=False)

# 分析模式
patterns = batch_extractor.analyze_conversion_patterns()
print(patterns)

# 可视化
batch_extractor.visualize_conversion_features("analysis.png")
```

## 输出结果

### 1. 特征数据 (conversion_features.csv)
包含每对图像的详细特征信息：
- 文件大小变化比例
- 质量指标 (PSNR, SSIM, MSE)
- 颜色直方图相似度
- 压缩伪影检测结果
- 统计特征差异

### 2. 分析报告
- 转换模式统计
- 特征相关性分析
- 质量变化趋势

### 3. 可视化图表
- 特征分布直方图
- 相关性热图
- 散点图分析

## 特征说明

### 文件级特征
- `file_size_ratio`: 转换后文件大小与原始文件大小的比例
- `file_size_reduction`: 文件大小减少比例
- `format_change`: 格式是否发生变化
- `header_similarity`: 文件头相似度

### 质量特征
- `psnr`: 峰值信噪比，衡量图像质量
- `ssim`: 结构相似性指数
- `mse`: 均方误差
- `entropy_difference`: 信息熵差异

### 压缩特征
- `quality_ratio`: 质量比例
- `blocking_artifacts_ratio`: 块效应比例
- `ringing_artifacts_ratio`: 振铃效应比例
- `dct_mean_difference`: DCT系数均值差异

### 统计特征
- `mean_difference`: 像素均值差异
- `std_difference`: 标准差差异
- `skewness_difference`: 偏度差异
- `gradient_magnitude_ratio`: 梯度幅值比例

## 应用场景

1. **数字取证**: 分析图像是否经过转换处理
2. **质量控制**: 评估图像转换对质量的影响
3. **算法研究**: 研究不同转换算法的效果
4. **数据预处理**: 为机器学习模型准备特征数据

## 注意事项

1. 确保原始图像和转换后的图像文件名匹配
2. 支持的图像格式: JPG, JPEG, PNG, WebP
3. 处理大量图像时可能需要较长时间
4. 建议在有足够内存的机器上运行

## 故障排除

### 常见问题

1. **内存不足**: 减少批量处理的图像数量
2. **文件路径错误**: 检查目录路径是否正确
3. **格式不支持**: 确保图像格式在支持列表中
4. **依赖缺失**: 运行 `pip install -r requirements.txt`

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License
