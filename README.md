# 图书馆智能推荐系统

基于用户行为的智能图书推荐系统，采用多种推荐算法为用户提供个性化的图书推荐服务。

## 🚀 系统特性

### 推荐算法
- **协同过滤推荐**：基于用户相似度的推荐算法
- **内容推荐**：基于图书特征的推荐算法
- **矩阵分解**：使用NMF进行潜在因子分解
- **混合推荐**：结合多种算法的综合推荐策略

### 用户行为分析
- 借阅行为跟踪
- 评分和评论系统
- 浏览行为记录
- 用户偏好分析

### 系统功能
- 用户注册和登录
- 图书浏览和搜索
- 借阅和归还管理
- 个性化推荐
- 数据可视化
- 管理员统计面板

## 🛠️ 技术栈

### 后端
- **Flask**：Web框架
- **SQLAlchemy**：ORM数据库操作
- **scikit-learn**：机器学习算法
- **pandas & numpy**：数据处理
- **SQLite**：数据库

### 前端
- **Bootstrap 5**：响应式UI框架
- **Chart.js**：数据可视化
- **Font Awesome**：图标库
- **JavaScript**：交互功能

### 机器学习
- **协同过滤**：基于用户的推荐
- **TF-IDF**：文本特征提取
- **余弦相似度**：相似度计算
- **NMF**：非负矩阵分解

## 📦 安装和运行

### 1. 环境要求
- Python 3.8+
- pip

### 2. 克隆项目
```bash
git clone <repository-url>
cd library-recommendation-system
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 初始化系统
```bash
python init_system.py
```

### 5. 启动应用
```bash
python app.py
```

### 6. 访问系统
- 主页：http://localhost:5000
- 管理员统计：http://localhost:5000/admin/stats

## 📁 项目结构

```
library-recommendation-system/
├── app.py                 # Flask主应用
├── models.py              # 数据模型
├── recommendation_engine.py  # 推荐引擎
├── data_generator.py      # 数据生成器
├── init_system.py         # 系统初始化
├── requirements.txt       # 依赖包列表
├── README.md             # 项目文档
├── static/               # 静态文件
│   ├── css/
│   │   └── style.css     # 自定义样式
│   └── js/
│       └── main.js       # 主要JavaScript
├── templates/            # HTML模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── login.html        # 登录页
│   ├── register.html     # 注册页
│   ├── dashboard.html    # 用户中心
│   ├── books.html        # 图书列表
│   ├── book_detail.html  # 图书详情
│   └── admin_stats.html  # 管理员统计
└── library.db           # SQLite数据库
```

## 🎯 核心功能

### 1. 用户管理
- 用户注册和登录
- 个人信息管理
- 借阅历史查看

### 2. 图书管理
- 图书信息展示
- 分类浏览
- 搜索功能
- 库存管理

### 3. 推荐系统
- **新用户**：热门图书推荐
- **老用户**：个性化推荐
- **实时更新**：基于最新行为
- **多算法融合**：提高推荐准确性

### 4. 借阅系统
- 图书借阅
- 归还管理
- 逾期提醒
- 借阅统计

### 5. 评分系统
- 五星评分
- 用户评论
- 评分统计
- 推荐权重

## 🔧 推荐算法详解

### 协同过滤 (Collaborative Filtering)
```python
def collaborative_filtering_recommendations(self, user_id, n_recommendations=10):
    # 1. 构建用户-图书交互矩阵
    # 2. 计算用户相似度
    # 3. 找到相似用户
    # 4. 推荐相似用户喜欢的图书
```

### 内容推荐 (Content-Based)
```python
def content_based_recommendations(self, user_id, n_recommendations=10):
    # 1. 提取用户历史借阅图书特征
    # 2. 构建用户偏好向量
    # 3. 计算图书相似度
    # 4. 推荐相似图书
```

### 矩阵分解 (Matrix Factorization)
```python
def matrix_factorization_recommendations(self, user_id, n_recommendations=10):
    # 1. 使用NMF分解用户-图书矩阵
    # 2. 获取潜在因子
    # 3. 预测用户评分
    # 4. 推荐高分图书
```

### 混合推荐 (Hybrid)
```python
def hybrid_recommendations(self, user_id, n_recommendations=10):
    # 1. 获取各算法推荐结果
    # 2. 加权融合
    # 3. 排序输出
    # 4. 去重和过滤
```

## 📊 数据模型

### 用户表 (users)
- id: 用户ID
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- age: 年龄
- gender: 性别
- occupation: 职业

### 图书表 (books)
- id: 图书ID
- isbn: ISBN号
- title: 书名
- author: 作者
- publisher: 出版社
- category: 分类
- description: 描述

### 借阅表 (borrowings)
- id: 借阅ID
- user_id: 用户ID
- book_id: 图书ID
- borrow_date: 借阅日期
- return_date: 归还日期
- status: 状态

### 评分表 (ratings)
- id: 评分ID
- user_id: 用户ID
- book_id: 图书ID
- rating: 评分
- review: 评论

## 🎨 界面展示

### 首页
- 热门图书推荐
- 最新图书展示
- 系统特色介绍
- 快速操作入口

### 用户中心
- 个人信息展示
- 借阅统计
- 个性化推荐
- 借阅历史

### 图书浏览
- 分类筛选
- 搜索功能
- 分页显示
- 图书详情

### 管理员面板
- 系统统计
- 数据可视化
- 用户管理
- 图书管理

## 🔍 API接口

### 推荐接口
```
GET /api/recommendations?algorithm=hybrid&n=10
```

### 参数说明
- `algorithm`: 推荐算法 (collaborative, content, matrix, hybrid)
- `n`: 推荐数量

### 返回格式
```json
[
  {
    "id": 1,
    "title": "图书标题",
    "author": "作者",
    "category": "分类",
    "cover_url": "封面URL"
  }
]
```

## 📈 性能优化

### 1. 算法优化
- 使用稀疏矩阵存储
- 缓存相似度计算结果
- 增量更新推荐模型

### 2. 数据库优化
- 索引优化
- 查询优化
- 连接池配置

### 3. 前端优化
- 懒加载
- 缓存策略
- 响应式设计

## 🚀 部署指南

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_system.py

# 启动开发服务器
python app.py
```

### 生产环境
```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用Nginx反向代理
# 配置Nginx配置文件
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础推荐功能
- 用户管理系统
- Web界面

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目维护者：[Your Name]
- 邮箱：[your.email@example.com]
- 项目地址：[GitHub Repository URL]

## 🙏 致谢

感谢以下开源项目的支持：
- Flask
- scikit-learn
- Bootstrap
- Chart.js
- Font Awesome

---

**注意**：这是一个演示项目，生产环境使用前请进行充分测试和安全加固。
