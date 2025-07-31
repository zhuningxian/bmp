#!/usr/bin/env python3
"""
创建测试用户脚本
"""

from app import app, db
from models import User, Book, Borrowing, Rating
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

def create_test_user():
    """创建有借阅历史的测试用户"""
    
    with app.app_context():
        # 创建测试用户
        test_user = User(
            username='test_user',
            email='test@example.com',
            password_hash=generate_password_hash('test123'),
            age=25,
            gender='男',
            occupation='学生'
        )
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username='test_user').first()
        if existing_user:
            print("测试用户已存在，使用现有用户")
            test_user = existing_user
        else:
            db.session.add(test_user)
            db.session.commit()
            print("创建测试用户成功")
        
        # 获取一些图书
        books = Book.query.limit(20).all()
        if not books:
            print("没有找到图书")
            return
        
        # 为测试用户创建借阅记录
        borrowings_created = 0
        for i in range(5):  # 借阅5本书
            book = random.choice(books)
            
            # 检查是否已经借阅过
            existing_borrowing = Borrowing.query.filter_by(
                user_id=test_user.id,
                book_id=book.id
            ).first()
            
            if not existing_borrowing:
                borrowing = Borrowing(
                    user_id=test_user.id,
                    book_id=book.id,
                    borrow_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                    due_date=datetime.now() + timedelta(days=30),
                    status='returned'
                )
                db.session.add(borrowing)
                borrowings_created += 1
        
        # 为借阅的图书创建评分
        ratings_created = 0
        for i in range(3):  # 为3本书评分
            book = random.choice(books)
            
            # 检查是否已经评分过
            existing_rating = Rating.query.filter_by(
                user_id=test_user.id,
                book_id=book.id
            ).first()
            
            if not existing_rating:
                rating = Rating(
                    user_id=test_user.id,
                    book_id=book.id,
                    rating=random.uniform(3.0, 5.0),
                    review=f"这是一本很好的书，推荐阅读！"
                )
                db.session.add(rating)
                ratings_created += 1
        
        db.session.commit()
        
        print(f"为测试用户创建了 {borrowings_created} 条借阅记录")
        print(f"为测试用户创建了 {ratings_created} 条评分记录")
        
        return test_user

def test_recommendations():
    """测试推荐功能"""
    
    with app.app_context():
        from recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        # 获取测试用户
        test_user = User.query.filter_by(username='test_user').first()
        if not test_user:
            print("没有找到测试用户")
            return
        
        print(f"测试用户: {test_user.username} (ID: {test_user.id})")
        
        # 测试个性化推荐
        print("\n测试个性化推荐...")
        recommendations = engine.get_personalized_recommendations(test_user.id, 5)
        print(f"推荐结果: {len(recommendations)} 本")
        
        for i, book_id in enumerate(recommendations, 1):
            book = Book.query.get(book_id)
            if book:
                print(f"  {i}. {book.title} - {book.author}")
        
        # 测试不同算法
        algorithms = ['collaborative', 'content', 'matrix', 'hybrid']
        
        for algorithm in algorithms:
            print(f"\n测试 {algorithm} 算法...")
            if algorithm == 'collaborative':
                recs = engine.collaborative_filtering_recommendations(test_user.id, 3)
            elif algorithm == 'content':
                recs = engine.content_based_recommendations(test_user.id, 3)
            elif algorithm == 'matrix':
                recs = engine.matrix_factorization_recommendations(test_user.id, 3)
            else:
                recs = engine.hybrid_recommendations(test_user.id, 3)
            
            print(f"  {algorithm} 算法推荐: {len(recs)} 本")
            for i, book_id in enumerate(recs[:2], 1):
                book = Book.query.get(book_id)
                if book:
                    print(f"    {i}. {book.title}")

if __name__ == '__main__':
    print("创建测试用户...")
    create_test_user()
    
    print("\n测试推荐功能...")
    test_recommendations()