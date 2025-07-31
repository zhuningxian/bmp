import random
from datetime import datetime, timedelta
from models import db, User, Book, Borrowing, Rating, UserBehavior

class DataGenerator:
    """数据生成器，用于生成模拟的图书馆数据"""
    
    def __init__(self):
        self.categories = [
            '计算机科学', '文学', '历史', '哲学', '经济学', 
            '心理学', '社会学', '数学', '物理学', '化学',
            '生物学', '医学', '艺术', '音乐', '体育',
            '旅游', '烹饪', '园艺', '科技', '教育'
        ]
        
        self.authors = [
            '张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十',
            '郑十一', '王十二', '冯十三', '陈十四', '褚十五', '卫十六',
            '蒋十七', '沈十八', '韩十九', '杨二十', '朱二一', '秦二二'
        ]
        
        self.publishers = [
            '人民出版社', '商务印书馆', '中华书局', '三联书店', '机械工业出版社',
            '电子工业出版社', '清华大学出版社', '北京大学出版社', '高等教育出版社',
            '科学出版社', '化学工业出版社', '人民邮电出版社', '中国建筑工业出版社'
        ]
        
        self.occupations = [
            '学生', '教师', '工程师', '医生', '律师', '会计师', '销售员',
            '设计师', '程序员', '研究员', '作家', '记者', '公务员', '自由职业'
        ]
        
    def generate_users(self, num_users=100):
        """生成用户数据"""
        users = []
        for i in range(num_users):
            user = User(
                username=f'user{i+1:03d}',
                email=f'user{i+1:03d}@example.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO',  # 默认密码: password
                age=random.randint(18, 65),
                gender=random.choice(['男', '女']),
                occupation=random.choice(self.occupations)
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"生成了 {num_users} 个用户")
        return users
    
    def generate_books(self, num_books=500):
        """生成图书数据"""
        books = []
        for i in range(num_books):
            # 生成ISBN
            isbn = f"{random.randint(1000000000000, 9999999999999)}"
            
            # 生成标题
            title_templates = [
                f"{random.choice(['现代', '当代', '经典', '实用', '高级', '基础'])}{random.choice(['教程', '指南', '手册', '概论', '导论', '原理'])}",
                f"{random.choice(['深入', '浅谈', '探索', '研究', '分析', '解读'])}{random.choice(['计算机', '文学', '历史', '哲学', '经济', '心理'])}",
                f"{random.choice(['Python', 'Java', 'C++', 'JavaScript', '数据库', '算法'])}{random.choice(['编程', '开发', '实践', '应用', '进阶', '精通'])}",
                f"{random.choice(['中国', '世界', '古代', '现代', '当代', '近代'])}{random.choice(['历史', '文化', '文学', '艺术', '哲学', '经济'])}"
            ]
            
            title = random.choice(title_templates)
            
            book = Book(
                isbn=isbn,
                title=title,
                author=random.choice(self.authors),
                publisher=random.choice(self.publishers),
                publish_year=random.randint(1990, 2023),
                category=random.choice(self.categories),
                language='中文',
                pages=random.randint(100, 800),
                description=f"这是一本关于{random.choice(self.categories)}的{random.choice(['经典', '实用', '入门', '进阶'])}书籍。",
                total_copies=random.randint(1, 5),
                available_copies=random.randint(0, 5)
            )
            books.append(book)
            db.session.add(book)
        
        db.session.commit()
        print(f"生成了 {num_books} 本图书")
        return books
    
    def generate_borrowings(self, users, books, num_borrowings=1000):
        """生成借阅记录"""
        borrowings = []
        for _ in range(num_borrowings):
            user = random.choice(users)
            book = random.choice(books)
            
            # 随机生成借阅日期（过去一年内）
            borrow_date = datetime.now() - timedelta(days=random.randint(1, 365))
            due_date = borrow_date + timedelta(days=30)
            
            # 随机决定是否已归还
            if random.random() < 0.8:  # 80%的概率已归还
                return_date = borrow_date + timedelta(days=random.randint(1, 30))
                status = 'returned'
            else:
                return_date = None
                status = 'borrowed' if due_date > datetime.now() else 'overdue'
            
            borrowing = Borrowing(
                user_id=user.id,
                book_id=book.id,
                borrow_date=borrow_date,
                return_date=return_date,
                due_date=due_date,
                status=status
            )
            borrowings.append(borrowing)
            db.session.add(borrowing)
        
        db.session.commit()
        print(f"生成了 {num_borrowings} 条借阅记录")
        return borrowings
    
    def generate_ratings(self, users, books, num_ratings=500):
        """生成评分数据"""
        ratings = []
        for _ in range(num_ratings):
            user = random.choice(users)
            book = random.choice(books)
            
            # 检查是否已经借阅过这本书
            existing_borrowing = db.session.query(Borrowing).filter(
                Borrowing.user_id == user.id,
                Borrowing.book_id == book.id
            ).first()
            
            if existing_borrowing:
                rating = Rating(
                    user_id=user.id,
                    book_id=book.id,
                    rating=random.uniform(1.0, 5.0),
                    review=random.choice([
                        "很好的书，推荐阅读！",
                        "内容详实，值得一读。",
                        "适合初学者，讲解清晰。",
                        "经典之作，不容错过。",
                        "实用性强，很有帮助。"
                    ])
                )
                ratings.append(rating)
                db.session.add(rating)
        
        db.session.commit()
        print(f"生成了 {len(ratings)} 条评分记录")
        return ratings
    
    def generate_user_behaviors(self, users, books, num_behaviors=2000):
        """生成用户行为数据"""
        behaviors = []
        behavior_types = ['view', 'search', 'wishlist']
        
        for _ in range(num_behaviors):
            user = random.choice(users)
            book = random.choice(books)
            behavior_type = random.choice(behavior_types)
            
            # 随机生成时间戳（过去一个月内）
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            behavior = UserBehavior(
                user_id=user.id,
                book_id=book.id,
                behavior_type=behavior_type,
                timestamp=timestamp,
                session_id=f"session_{random.randint(1000, 9999)}"
            )
            behaviors.append(behavior)
            db.session.add(behavior)
        
        db.session.commit()
        print(f"生成了 {num_behaviors} 条用户行为记录")
        return behaviors
    
    def generate_all_data(self):
        """生成所有模拟数据"""
        print("开始生成模拟数据...")
        
        # 生成用户
        users = self.generate_users(100)
        
        # 生成图书
        books = self.generate_books(500)
        
        # 生成借阅记录
        borrowings = self.generate_borrowings(users, books, 1000)
        
        # 生成评分
        ratings = self.generate_ratings(users, books, 500)
        
        # 生成用户行为
        behaviors = self.generate_user_behaviors(users, books, 2000)
        
        print("所有模拟数据生成完成！")
        print(f"总计：{len(users)} 个用户，{len(books)} 本图书，{len(borrowings)} 条借阅记录，{len(ratings)} 条评分，{len(behaviors)} 条行为记录")
        
        return {
            'users': users,
            'books': books,
            'borrowings': borrowings,
            'ratings': ratings,
            'behaviors': behaviors
        }