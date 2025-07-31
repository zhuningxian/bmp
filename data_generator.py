import random
from datetime import datetime, timedelta
from models import db, User, Book, Borrowing, Rating, UserBehavior
from werkzeug.security import generate_password_hash

class DataGenerator:
    """数据生成器，用于创建模拟数据"""
    
    def __init__(self):
        self.categories = [
            '文学', '科技', '历史', '哲学', '艺术', '经济', '教育', '医学', 
            '计算机', '心理学', '社会学', '政治学', '地理', '生物', '化学', '物理'
        ]
        
        self.occupations = [
            '学生', '教师', '工程师', '医生', '律师', '会计师', '销售员', 
            '程序员', '设计师', '研究员', '作家', '记者', '公务员', '自由职业'
        ]
        
        self.publishers = [
            '人民教育出版社', '商务印书馆', '中华书局', '三联书店', '机械工业出版社',
            '电子工业出版社', '清华大学出版社', '北京大学出版社', '高等教育出版社',
            '科学出版社', '中国青年出版社', '作家出版社', '译林出版社', '上海译文出版社'
        ]
        
        self.book_titles = [
            # 文学类
            '红楼梦', '西游记', '水浒传', '三国演义', '百年孤独', '战争与和平',
            '安娜·卡列尼娜', '简·爱', '飘', '老人与海', '1984', '动物农场',
            '百年孤独', '霍乱时期的爱情', '白鹿原', '活着', '平凡的世界',
            
            # 科技类
            '人工智能：一种现代方法', '深度学习', '机器学习', '数据科学导论',
            'Python编程：从入门到实践', '算法导论', '设计模式', '重构',
            '代码整洁之道', '人月神话', '黑客与画家', '硅谷之谜',
            
            # 历史类
            '史记', '资治通鉴', '全球通史', '人类简史', '未来简史',
            '枪炮、病菌与钢铁', '明朝那些事儿', '万历十五年', '中国通史',
            
            # 哲学类
            '苏菲的世界', '存在与虚无', '查拉图斯特拉如是说', '道德经',
            '论语', '孟子', '庄子', '理想国', '形而上学', '纯粹理性批判',
            
            # 经济类
            '经济学原理', '国富论', '资本论', '货币战争', '穷爸爸富爸爸',
            '经济学通识', '魔鬼经济学', '小岛经济学', '经济学的思维方式',
            
            # 教育类
            '教育的目的', '给教师的建议', '教育漫话', '爱弥儿', '教育心理学',
            '学习之道', '刻意练习', '认知天性', '如何阅读一本书',
            
            # 医学类
            '内科学', '外科学', '儿科学', '妇产科学', '诊断学', '药理学',
            '人体解剖学', '生理学', '病理学', '医学伦理学',
            
            # 计算机类
            '计算机科学导论', '数据结构与算法', '操作系统', '计算机网络',
            '数据库系统概念', '编译原理', '软件工程', '计算机组成原理',
            '数字逻辑设计', '计算机图形学', '人工智能', '机器学习',
            
            # 心理学类
            '心理学导论', '社会心理学', '发展心理学', '认知心理学',
            '实验心理学', '心理测量学', '临床心理学', '咨询心理学',
            '行为心理学', '积极心理学',
            
            # 社会学类
            '社会学导论', '社会研究方法', '社会心理学', '组织社会学',
            '城市社会学', '农村社会学', '经济社会学', '文化社会学',
            '政治社会学', '教育社会学'
        ]
        
        self.authors = [
            '曹雪芹', '吴承恩', '施耐庵', '罗贯中', '加西亚·马尔克斯',
            '列夫·托尔斯泰', '夏洛蒂·勃朗特', '玛格丽特·米切尔',
            '海明威', '乔治·奥威尔', '陈忠实', '余华', '路遥',
            '斯图尔特·罗素', '伊恩·古德费洛', '周志华', '李航',
            '安德鲁·吴', '托马斯·科曼', '埃里希·伽马', '马丁·福勒',
            '罗伯特·马丁', '弗雷德里克·布鲁克斯', '保罗·格雷厄姆',
            '司马迁', '司马光', '斯塔夫里阿诺斯', '尤瓦尔·赫拉利',
            '贾雷德·戴蒙德', '当年明月', '黄仁宇', '吕思勉',
            '乔斯坦·贾德', '让-保罗·萨特', '弗里德里希·尼采',
            '老子', '孔子', '孟子', '庄子', '柏拉图', '亚里士多德',
            '伊曼努尔·康德', '曼昆', '亚当·斯密', '卡尔·马克思',
            '宋鸿兵', '罗伯特·清崎', '薛兆丰', '史蒂文·列维特',
            '亨利·黑兹利特', '托马斯·索维尔', '阿尔弗雷德·诺思·怀特海',
            '苏霍姆林斯基', '约翰·洛克', '让-雅克·卢梭', '皮亚杰',
            '乔希·维茨金', '安德斯·艾利克森', '彼得·布朗',
            '莫提默·艾德勒', '查尔斯·范多伦'
        ]
    
    def generate_users(self, num_users=100):
        """生成用户数据"""
        users = []
        for i in range(num_users):
            user = User(
                username=f'user{i+1:03d}',
                email=f'user{i+1:03d}@example.com',
                password_hash=generate_password_hash('password123'),
                age=random.randint(18, 65),
                gender=random.choice(['男', '女']),
                occupation=random.choice(self.occupations),
                created_at=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            users.append(user)
        
        db.session.add_all(users)
        db.session.commit()
        return users
    
    def generate_books(self, num_books=500):
        """生成图书数据"""
        books = []
        for i in range(num_books):
            title = random.choice(self.book_titles)
            author = random.choice(self.authors)
            category = random.choice(self.categories)
            publisher = random.choice(self.publishers)
            publish_year = random.randint(1950, 2023)
            pages = random.randint(100, 800)
            
            book = Book(
                isbn=f'978{random.randint(1000000000000, 9999999999999)}',
                title=title,
                author=author,
                publisher=publisher,
                publish_year=publish_year,
                category=category,
                language='中文',
                pages=pages,
                description=f'这是一本关于{category}的经典著作，作者{author}。',
                cover_url=f'https://example.com/covers/{i+1}.jpg',
                total_copies=random.randint(1, 5),
                available_copies=random.randint(0, 5),
                created_at=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            books.append(book)
        
        db.session.add_all(books)
        db.session.commit()
        return books
    
    def generate_borrowings(self, users, books, num_borrowings=1000):
        """生成借阅记录"""
        borrowings = []
        for _ in range(num_borrowings):
            user = random.choice(users)
            book = random.choice(books)
            borrow_date = datetime.now() - timedelta(days=random.randint(1, 365))
            due_date = borrow_date + timedelta(days=30)
            
            # 70%的概率已归还
            if random.random() < 0.7:
                return_date = borrow_date + timedelta(days=random.randint(1, 30))
                status = 'returned'
            else:
                return_date = None
                status = 'borrowed' if due_date > datetime.now() else 'overdue'
            
            borrowing = Borrowing(
                user_id=user.id,
                book_id=book.id,
                borrow_date=borrow_date,
                due_date=due_date,
                return_date=return_date,
                status=status
            )
            borrowings.append(borrowing)
        
        db.session.add_all(borrowings)
        db.session.commit()
        return borrowings
    
    def generate_ratings(self, users, books, num_ratings=800):
        """生成评分数据"""
        ratings = []
        for _ in range(num_ratings):
            user = random.choice(users)
            book = random.choice(books)
            rating = random.uniform(1.0, 5.0)
            
            # 添加一些评论
            review_templates = [
                f'这本书很不错，值得推荐！',
                f'内容充实，讲解详细。',
                f'适合初学者阅读。',
                f'经典之作，必读！',
                f'作者的观点很有启发性。',
                f'文笔流畅，易于理解。',
                f'理论与实践结合得很好。',
                f'内容丰富，收获很大。'
            ]
            review = random.choice(review_templates)
            
            rating_obj = Rating(
                user_id=user.id,
                book_id=book.id,
                rating=round(rating, 1),
                review=review,
                created_at=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            ratings.append(rating_obj)
        
        db.session.add_all(ratings)
        db.session.commit()
        return ratings
    
    def generate_behaviors(self, users, books, num_behaviors=2000):
        """生成用户行为数据"""
        behaviors = []
        behavior_types = ['view', 'search', 'bookmark', 'share']
        
        for _ in range(num_behaviors):
            user = random.choice(users)
            book = random.choice(books)
            behavior_type = random.choice(behavior_types)
            duration = random.randint(10, 600) if behavior_type == 'view' else None
            
            behavior = UserBehavior(
                user_id=user.id,
                book_id=book.id,
                behavior_type=behavior_type,
                duration=duration,
                created_at=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            behaviors.append(behavior)
        
        db.session.add_all(behaviors)
        db.session.commit()
        return behaviors
    
    def generate_all_data(self):
        """生成所有模拟数据"""
        print("开始生成模拟数据...")
        
        # 生成用户
        print("生成用户数据...")
        users = self.generate_users(100)
        
        # 生成图书
        print("生成图书数据...")
        books = self.generate_books(500)
        
        # 生成借阅记录
        print("生成借阅记录...")
        borrowings = self.generate_borrowings(users, books, 1000)
        
        # 生成评分
        print("生成评分数据...")
        ratings = self.generate_ratings(users, books, 800)
        
        # 生成用户行为
        print("生成用户行为数据...")
        behaviors = self.generate_behaviors(users, books, 2000)
        
        print("数据生成完成！")
        print(f"生成了 {len(users)} 个用户")
        print(f"生成了 {len(books)} 本图书")
        print(f"生成了 {len(borrowings)} 条借阅记录")
        print(f"生成了 {len(ratings)} 条评分记录")
        print(f"生成了 {len(behaviors)} 条用户行为记录")
        
        return users, books, borrowings, ratings, behaviors