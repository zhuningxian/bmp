# 智能图书馆推荐系统

基于用户行为的智能图书推荐系统，采用多种机器学习算法为用户提供个性化图书推荐。

## 功能特性

### 🎯 智能推荐算法
- **协同过滤推荐**：基于用户相似度的推荐
- **内容过滤推荐**：基于图书特征的推荐
- **矩阵分解推荐**：使用NMF算法的潜在因子模型
- **混合推荐**：结合多种算法的综合推荐

### 📊 用户行为分析
- 借阅记录分析
- 评分行为分析
- 浏览行为跟踪
- 阅读偏好挖掘

### 🎨 现代化界面
- 响应式设计，支持移动端
- 美观的用户界面
- 实时交互体验
- 数据可视化展示

### 🔐 用户管理
- 用户注册登录
- 个人信息管理
- 借阅历史查看
- 评分记录管理

## 技术栈

### 后端
- **Flask**: Web框架
- **SQLAlchemy**: ORM数据库操作
- **scikit-learn**: 机器学习算法
- **pandas & numpy**: 数据处理
- **Flask-Login**: 用户认证

### 前端
- **Bootstrap 5**: UI框架
- **jQuery**: JavaScript库
- **Font Awesome**: 图标库
- **Chart.js**: 数据可视化（可选）

### 数据库
- **SQLite**: 轻量级数据库（开发环境）
- **PostgreSQL/MySQL**: 生产环境推荐

## 安装和运行

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

### 4. 运行应用
```bash
python run.py
```

### 5. 访问系统
打开浏览器访问：http://localhost:5000

## 系统架构

### 数据模型
```
User (用户)
├── id, username, email, password_hash
├── age, gender, occupation
└── created_at

Book (图书)
├── id, isbn, title, author
├── publisher, publish_year, category
├── language, pages, description
└── total_copies, available_copies

Borrowing (借阅记录)
├── id, user_id, book_id
├── borrow_date, due_date, return_date
└── status

Rating (评分)
├── id, user_id, book_id
├── rating, review
└── created_at

UserBehavior (用户行为)
├── id, user_id, book_id
├── behavior_type, duration
└── created_at
```

### 推荐算法流程
1. **数据收集**：收集用户借阅、评分、浏览等行为数据
2. **数据预处理**：清洗数据，构建用户-图书交互矩阵
3. **特征工程**：提取图书特征，计算用户偏好
4. **算法训练**：训练多种推荐算法模型
5. **结果融合**：结合多种算法结果，生成最终推荐
6. **实时更新**：根据新数据持续优化模型

## 推荐算法详解

### 1. 协同过滤 (Collaborative Filtering)
- **原理**：找到相似用户，推荐他们喜欢的图书
- **优势**：能发现用户的潜在兴趣
- **劣势**：冷启动问题，稀疏性问题

### 2. 内容过滤 (Content-Based Filtering)
- **原理**：基于图书特征和用户历史偏好推荐
- **优势**：能处理冷启动问题，推荐结果可解释
- **劣势**：特征提取困难，推荐多样性不足

### 3. 矩阵分解 (Matrix Factorization)
- **原理**：将用户-图书矩阵分解为潜在因子
- **优势**：能处理稀疏数据，推荐精度高
- **劣势**：模型训练复杂，可解释性差

### 4. 混合推荐 (Hybrid Recommendation)
- **原理**：结合多种算法的优势
- **权重分配**：
  - 协同过滤：40%
  - 内容过滤：30%
  - 矩阵分解：30%

## 使用指南

### 用户操作
1. **注册登录**：创建账户或使用现有账户登录
2. **浏览图书**：按分类、关键词搜索图书
3. **借阅图书**：点击借阅按钮，系统自动更新库存
4. **评分评论**：为阅读过的图书评分和评论
5. **查看推荐**：在个人中心查看个性化推荐

### 管理员功能
- 图书管理：添加、编辑、删除图书
- 用户管理：查看用户信息，管理用户状态
- 数据统计：查看系统使用统计
- 推荐监控：监控推荐算法效果

## 性能优化

### 数据库优化
- 建立合适的索引
- 使用连接池
- 定期清理过期数据

### 算法优化
- 使用缓存减少重复计算
- 增量更新推荐模型
- 并行处理大量数据

### 前端优化
- 图片懒加载
- 分页加载数据
- 本地缓存用户偏好

## 部署说明

### 开发环境
```bash
python run.py
```

### 生产环境
```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用Docker
docker build -t library-recommendation .
docker run -p 5000:5000 library-recommendation
```

## 扩展功能

### 计划中的功能
- [ ] 实时聊天系统
- [ ] 图书推荐API
- [ ] 移动端应用
- [ ] 高级数据分析
- [ ] 多语言支持

### 技术改进
- [ ] 深度学习推荐算法
- [ ] 实时推荐引擎
- [ ] 分布式部署
- [ ] 微服务架构

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：[Your Name]
- 邮箱：[your.email@example.com]
- 项目地址：[GitHub Repository URL]

## 致谢

感谢所有为这个项目做出贡献的开发者和用户！
