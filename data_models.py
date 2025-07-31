import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

class LibraryDatabase:
    """图书馆数据库模拟类"""
    
    def __init__(self):
        self.users_df = pd.DataFrame()
        self.books_df = pd.DataFrame()
        self.ratings_df = pd.DataFrame()
        self.borrowings_df = pd.DataFrame()
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        try:
            if os.path.exists('data/users.csv'):
                self.users_df = pd.read_csv('data/users.csv')
            if os.path.exists('data/books.csv'):
                self.books_df = pd.read_csv('data/books.csv')
            if os.path.exists('data/ratings.csv'):
                self.ratings_df = pd.read_csv('data/ratings.csv')
            if os.path.exists('data/borrowings.csv'):
                self.borrowings_df = pd.read_csv('data/borrowings.csv')
        except Exception as e:
            print(f"加载数据时出错: {e}")
            self.generate_demo_data()
    
    def save_data(self):
        """保存数据"""
        if not os.path.exists('data'):
            os.makedirs('data')
        
        self.users_df.to_csv('data/users.csv', index=False)
        self.books_df.to_csv('data/books.csv', index=False)
        self.ratings_df.to_csv('data/ratings.csv', index=False)
        self.borrowings_df.to_csv('data/borrowings.csv', index=False)
    
    def generate_demo_data(self):
        """生成演示数据"""
        print("生成演示数据...")
        
        # 生成用户数据
        user_data = []
        user_profiles = ['学生', '教师', '研究员', '图书馆员', '访问学者']
        interests = ['文学', '科学', '历史', '艺术', '哲学', '技术', '医学', '经济', '法律', '教育']
        
        for i in range(1, 201):  # 200个用户
            profile = random.choice(user_profiles)
            user_interests = random.sample(interests, random.randint(2, 5))
            user_data.append({
                'user_id': i,
                'name': f'用户{i}',
                'profile': profile,
                'age': random.randint(18, 65),
                'registration_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                'interests': ','.join(user_interests)
            })
        
        self.users_df = pd.DataFrame(user_data)
        
        # 生成图书数据
        book_data = []
        categories = ['文学', '科学', '历史', '艺术', '哲学', '技术', '医学', '经济', '法律', '教育']
        authors = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', 'Smith', 'Johnson', 'Brown', 'Davis']
        
        for i in range(1, 1001):  # 1000本书
            category = random.choice(categories)
            author = random.choice(authors)
            year = random.randint(1950, 2023)
            book_data.append({
                'book_id': i,
                'title': f'{category}经典著作{i}',
                'author': author,
                'category': category,
                'isbn': f'978-{random.randint(1000000000, 9999999999)}',
                'publication_year': year,
                'description': f'这是一本关于{category}的优秀著作，由{author}编写。',
                'language': random.choice(['中文', '英文']),
                'pages': random.randint(100, 800),
                'available_copies': random.randint(1, 10)
            })
        
        self.books_df = pd.DataFrame(book_data)
        
        # 生成评分数据
        rating_data = []
        for i in range(5000):  # 5000条评分记录
            user_id = random.randint(1, 200)
            book_id = random.randint(1, 1000)
            
            # 避免重复评分
            if not ((self.ratings_df['user_id'] == user_id) & (self.ratings_df['book_id'] == book_id)).any():
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 25, 35, 25])[0]
                rating_data.append({
                    'user_id': user_id,
                    'book_id': book_id,
                    'rating': rating,
                    'timestamp': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        self.ratings_df = pd.DataFrame(rating_data)
        
        # 生成借阅数据
        borrowing_data = []
        for i in range(8000):  # 8000条借阅记录
            user_id = random.randint(1, 200)
            book_id = random.randint(1, 1000)
            borrow_date = datetime.now() - timedelta(days=random.randint(1, 365))
            return_date = borrow_date + timedelta(days=random.randint(7, 30))
            
            borrowing_data.append({
                'user_id': user_id,
                'book_id': book_id,
                'borrow_date': borrow_date.strftime('%Y-%m-%d'),
                'return_date': return_date.strftime('%Y-%m-%d') if random.random() > 0.2 else None,
                'status': '已归还' if random.random() > 0.2 else '借阅中'
            })
        
        self.borrowings_df = pd.DataFrame(borrowing_data)
        
        # 保存数据
        self.save_data()
        print("演示数据生成完成！")
    
    def get_all_users(self):
        """获取所有用户"""
        return self.users_df.to_dict('records')
    
    def get_all_books(self):
        """获取所有图书"""
        return self.books_df.to_dict('records')
    
    def get_user_ratings(self, user_id):
        """获取用户的所有评分"""
        return self.ratings_df[self.ratings_df['user_id'] == user_id]
    
    def get_user_borrowings(self, user_id):
        """获取用户的所有借阅记录"""
        return self.borrowings_df[self.borrowings_df['user_id'] == user_id]
    
    def get_book_ratings(self, book_id):
        """获取图书的所有评分"""
        return self.ratings_df[self.ratings_df['book_id'] == book_id]
    
    def add_rating(self, user_id, book_id, rating):
        """添加评分"""
        new_rating = {
            'user_id': user_id,
            'book_id': book_id,
            'rating': rating,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.ratings_df = pd.concat([self.ratings_df, pd.DataFrame([new_rating])], ignore_index=True)
        self.save_data()
    
    def add_borrowing(self, user_id, book_id):
        """添加借阅记录"""
        new_borrowing = {
            'user_id': user_id,
            'book_id': book_id,
            'borrow_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': None,
            'status': '借阅中'
        }
        self.borrowings_df = pd.concat([self.borrowings_df, pd.DataFrame([new_borrowing])], ignore_index=True)
        self.save_data()
    
    def get_user_profile(self, user_id):
        """获取用户档案"""
        user = self.users_df[self.users_df['user_id'] == user_id]
        if not user.empty:
            return user.iloc[0].to_dict()
        return None
    
    def get_book_info(self, book_id):
        """获取图书信息"""
        book = self.books_df[self.books_df['book_id'] == book_id]
        if not book.empty:
            return book.iloc[0].to_dict()
        return None