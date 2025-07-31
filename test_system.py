#!/usr/bin/env python3
"""
系统测试脚本
"""

from app import app, db
from models import User, Book, Borrowing, Rating, UserBehavior
from recommendation_engine import RecommendationEngine

def test_database():
    """测试数据库状态"""
    print("=" * 50)
    print("数据库状态测试")
    print("=" * 50)
    
    with app.app_context():
        # 检查表是否存在
        try:
            user_count = User.query.count()
            book_count = Book.query.count()
            borrowing_count = Borrowing.query.count()
            rating_count = Rating.query.count()
            
            print(f"用户数量: {user_count}")
            print(f"图书数量: {book_count}")
            print(f"借阅记录: {borrowing_count}")
            print(f"评分记录: {rating_count}")
            
            if user_count == 0 or book_count == 0:
                print("⚠️  数据库数据不足，正在生成测试数据...")
                from data_generator import DataGenerator
                generator = DataGenerator()
                generator.generate_all_data()
                
                # 重新统计
                user_count = User.query.count()
                book_count = Book.query.count()
                borrowing_count = Borrowing.query.count()
                rating_count = Rating.query.count()
                
                print(f"生成后 - 用户数量: {user_count}")
                print(f"生成后 - 图书数量: {book_count}")
                print(f"生成后 - 借阅记录: {borrowing_count}")
                print(f"生成后 - 评分记录: {rating_count}")
            
            return True
            
        except Exception as e:
            print(f"数据库测试失败: {e}")
            return False

def test_recommendation_engine():
    """测试推荐引擎"""
    print("\n" + "=" * 50)
    print("推荐引擎测试")
    print("=" * 50)
    
    with app.app_context():
        try:
            engine = RecommendationEngine()
            
            # 获取一个用户
            user = User.query.first()
            if not user:
                print("没有找到用户")
                return False
            
            print(f"测试用户: {user.username} (ID: {user.id})")
            
            # 测试热门图书推荐
            print("\n1. 测试热门图书推荐...")
            popular_books = engine.get_popular_books(5)
            print(f"热门图书: {len(popular_books)} 本")
            for book_id in popular_books[:3]:
                book = Book.query.get(book_id)
                if book:
                    print(f"   - {book.title}")
            
            # 测试最新图书推荐
            print("\n2. 测试最新图书推荐...")
            recent_books = engine.get_recent_books(5)
            print(f"最新图书: {len(recent_books)} 本")
            for book_id in recent_books[:3]:
                book = Book.query.get(book_id)
                if book:
                    print(f"   - {book.title}")
            
            # 测试个性化推荐
            print("\n3. 测试个性化推荐...")
            personalized = engine.get_personalized_recommendations(user.id, 5)
            print(f"个性化推荐: {len(personalized)} 本")
            for book_id in personalized[:3]:
                book = Book.query.get(book_id)
                if book:
                    print(f"   - {book.title}")
            
            return True
            
        except Exception as e:
            print(f"推荐引擎测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_web_routes():
    """测试Web路由"""
    print("\n" + "=" * 50)
    print("Web路由测试")
    print("=" * 50)
    
    import requests
    
    base_url = "http://localhost:5000"
    
    routes = [
        ("/", "首页"),
        ("/books", "图书列表"),
        ("/login", "登录页面"),
        ("/register", "注册页面"),
        ("/admin/stats", "管理员统计")
    ]
    
    for route, name in routes:
        try:
            response = requests.get(f"{base_url}{route}")
            if response.status_code == 200:
                print(f"✓ {name}: 正常")
            else:
                print(f"✗ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ {name}: 连接失败 - {e}")

def main():
    """主测试函数"""
    print("图书馆智能推荐系统测试")
    print("=" * 50)
    
    # 测试数据库
    db_ok = test_database()
    
    if db_ok:
        # 测试推荐引擎
        engine_ok = test_recommendation_engine()
        
        # 测试Web路由
        test_web_routes()
        
        print("\n" + "=" * 50)
        print("测试总结")
        print("=" * 50)
        print(f"数据库: {'✓ 正常' if db_ok else '✗ 异常'}")
        print(f"推荐引擎: {'✓ 正常' if engine_ok else '✗ 异常'}")
        print("Web路由: ✓ 已测试")
        
        if db_ok and engine_ok:
            print("\n🎉 系统运行正常！")
            print("访问地址: http://localhost:5000")
        else:
            print("\n⚠️  系统存在问题，请检查日志")
    else:
        print("\n❌ 数据库初始化失败")

if __name__ == '__main__':
    main()