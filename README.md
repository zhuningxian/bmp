# 图像转换特征提取器 (Image Conversion Feature Extractor)

这是一个用于分析JPEG图像转为JFIF格式以及其他图像格式转换的特征提取工具。该工具可以提取多维度的转换特征，用于图像取证、质量分析和转换模式识别。

## 功能特性

### 核心功能
- **文件级特征提取**: 文件大小变化、格式转换、文件头分析
- **图像级特征提取**: 尺寸变化、颜色空间分析、边缘检测对比
- **压缩特征提取**: JPEG质量分析、压缩伪影检测、DCT系数分析
- **质量特征提取**: PSNR、SSIM、MSE计算、信息熵分析
- **统计特征提取**: 像素统计、梯度分析、纹理特征
- **批量处理**: 支持批量图像对的特征提取
- **可视化分析**: 特征分布图、相关性热图

### 支持的图像格式
- JPEG/JPG
- PNG
- WebP
- 其他OpenCV支持的格式

## 安装依赖

```bash
pip install opencv-python
pip install pillow
pip install numpy
pip install pandas
pip install matplotlib
pip install seaborn
pip install scikit-learn
```

## 使用方法

### 1. 单个图像对分析

```python
from conversion_feature_extractor import ConversionFeatureExtractor

# 初始化特征提取器
extractor = ConversionFeatureExtractor()

# 提取转换特征
features = extractor.extract_conversion_features(
    original_path="original_image.jpg",
    converted_path="converted_image.jpg"
)

print(f"提取到 {len(features)} 个特征")
for key, value in features.items():
    print(f"{key}: {value}")
```

### 2. 批量图像分析

```python
from conversion_feature_extractor import BatchConversionFeatureExtractor

# 初始化批量处理器
batch_extractor = BatchConversionFeatureExtractor()

# 批量提取特征
features_df = batch_extractor.extract_batch_features(
    original_dir="/path/to/original/images",
    converted_dir="/path/to/converted/images"
)

# 保存结果
features_df.to_csv("conversion_features.csv", index=False)

# 分析转换模式
patterns = batch_extractor.analyze_conversion_patterns()
print("转换模式分析:", patterns)

# 可视化特征
batch_extractor.visualize_conversion_features("analysis.png")
```

### 3. 运行测试

```bash
# 运行测试脚本
python test_conversion_extractor.py

# 或直接运行主程序（需要修改路径）
python conversion_feature_extractor.py
```

## 特征详解

### 文件级特征
- `file_size_ratio`: 文件大小比例
- `file_size_reduction`: 文件大小减少比例
- `format_change`: 格式是否改变
- `header_similarity`: 文件头相似度
- `header_entropy_*`: 文件头信息熵

### 图像级特征
- `size_change`: 尺寸是否改变
- `width_ratio/height_ratio`: 宽高比例
- `*_histogram_similarity`: 颜色直方图相似度
- `edge_count_ratio`: 边缘像素比例
- `edge_preservation`: 边缘保持度

### 压缩特征
- `quality_ratio`: 质量比例
- `quality_degradation`: 质量是否下降
- `blocking_artifacts_*`: 块效应伪影
- `ringing_artifacts_*`: 振铃效应伪影
- `dct_difference_*`: DCT系数差异

### 质量特征
- `psnr`: 峰值信噪比
- `ssim`: 结构相似性指数
- `mse`: 均方误差
- `entropy_*`: 信息熵

### 统计特征
- `mean_*`: 均值相关特征
- `std_*`: 标准差相关特征
- `gradient_*`: 梯度统计特征
- `texture_*`: 纹理特征

## 应用场景

### 1. 图像取证
- 检测图像是否经过转换/压缩
- 分析图像处理历史
- 识别图像来源平台

### 2. 质量评估
- 评估转换后的图像质量
- 比较不同压缩算法效果
- 优化图像处理参数

### 3. 格式转换分析
- 分析JPEG到JFIF的转换特征
- 比较不同格式转换的影响
- 识别最优转换策略

## JPEG/JFIF转换原理

### JPEG格式特点
- 使用离散余弦变换(DCT)
- 有损压缩算法
- 支持多种编码方式

### JFIF格式特点
- JPEG File Interchange Format
- JPEG的标准化封装格式
- 包含特定的文件头结构

### 转换影响分析
1. **文件头变化**: JFIF标准化了文件头格式
2. **质量参数**: 可能导致重新压缩
3. **元数据**: EXIF信息可能丢失或改变
4. **颜色空间**: 可能影响颜色表示

## 高级功能

### 自定义特征提取
```python
# 继承基类添加自定义特征
class CustomFeatureExtractor(ConversionFeatureExtractor):
    def extract_custom_features(self, original_path, converted_path):
        features = {}
        # 添加自定义特征提取逻辑
        return features
```

### 机器学习集成
```python
from sklearn.ensemble import RandomForestClassifier

# 使用提取的特征训练分类器
features_df = batch_extractor.extract_batch_features(...)
X = features_df.select_dtypes(include=[np.number])
y = features_df['conversion_type']  # 需要标签数据

clf = RandomForestClassifier()
clf.fit(X, y)
```

## 注意事项

1. **内存使用**: 大图像会占用较多内存
2. **处理时间**: 复杂特征提取需要时间
3. **文件路径**: 确保图像文件路径正确
4. **格式支持**: 部分特征仅适用于特定格式
5. **错误处理**: 建议添加适当的异常处理

## 示例输出

```
提取到 45 个特征:
file_size_ratio: 0.8523
file_size_reduction: 0.1477
psnr: 28.4521
ssim: 0.9234
quality_degradation: 1
blocking_artifacts_ratio: 1.2341
...
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个工具！

## 许可证

此项目采用MIT许可证。
