# 图书馆智能推荐系统

基于用户行为分析的图书馆智能推荐系统，采用多种推荐算法为用户提供个性化图书推荐。

## 功能特性

- 基于协同过滤的推荐算法
- 基于内容的推荐算法
- 混合推荐策略
- 用户行为分析
- 实时推荐API
- 可视化分析界面

## 技术栈

- **后端**: Python Flask, SQLAlchemy
- **数据分析**: Pandas, NumPy, Scikit-learn
- **推荐算法**: Surprise库
- **可视化**: Matplotlib, Seaborn
- **前端**: HTML, CSS, JavaScript
- **数据库**: SQLite

## 快速开始

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 初始化数据库:
```bash
python init_db.py
```

3. 运行系统:
```bash
python app.py
```

4. 访问 http://localhost:5000

## 项目结构

```
├── app.py                 # 主应用文件
├── models/               # 数据模型
├── algorithms/           # 推荐算法
├── api/                  # API接口
├── static/               # 静态文件
├── templates/            # HTML模板
├── data/                 # 数据文件
└── utils/                # 工具函数
```
