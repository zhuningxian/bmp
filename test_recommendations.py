#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.database import SessionLocal, User, Book, Rating
from algorithms.hybrid_recommender import HybridRecommender

def test_recommendations():
    """测试推荐系统功能"""
    print("🧪 开始测试推荐系统...")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 初始化推荐系统
        recommender = HybridRecommender(db)
        print("📊 初始化推荐系统...")
        recommender.initialize()
        
        # 测试用户1的推荐
        user_id = 1
        print(f"\n👤 测试用户 {user_id} 的推荐:")
        
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            print(f"   用户: {user.username}, {user.age}岁, {user.occupation}")
        
        # 获取用户评分历史
        user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        print(f"   历史评分: {len(user_ratings)} 本图书")
        
        for rating in user_ratings[:3]:  # 显示前3个评分
            book = db.query(Book).filter(Book.id == rating.book_id).first()
            if book:
                print(f"   - 《{book.title}》: {rating.rating}分")
        
        # 测试不同的推荐算法
        algorithms = [
            ('adaptive', '自适应推荐'),
            ('content', '基于内容推荐'),
            ('collaborative', '协同过滤推荐'),
            ('hybrid', '混合推荐')
        ]
        
        for algo_type, algo_name in algorithms:
            print(f"\n🔍 {algo_name}:")
            
            try:
                if algo_type == 'adaptive':
                    recommendations = recommender.get_adaptive_recommendations(user_id, 5)
                elif algo_type == 'content':
                    recommendations = recommender.cb_recommender.get_content_based_recommendations(user_id, 5)
                elif algo_type == 'collaborative':
                    recommendations = recommender.cf_recommender.get_svd_recommendations(user_id, 5)
                elif algo_type == 'hybrid':
                    recommendations = recommender.get_hybrid_recommendations(user_id, 5)
                
                if recommendations:
                    for i, (book_id, score) in enumerate(recommendations, 1):
                        book = db.query(Book).filter(Book.id == book_id).first()
                        if book:
                            print(f"   {i}. 《{book.title}》 (评分: {score:.3f})")
                else:
                    print("   暂无推荐结果")
                    
            except Exception as e:
                print(f"   错误: {e}")
        
        # 测试热门图书
        print(f"\n🔥 热门图书:")
        popular_books = recommender.cb_recommender.get_popular_books(5)
        for i, (book_id, popularity) in enumerate(popular_books, 1):
            book = db.query(Book).filter(Book.id == book_id).first()
            if book:
                print(f"   {i}. 《{book.title}》 (热度: {popularity})")
        
        # 测试搜索功能
        print(f"\n🔍 搜索测试 (关键词: '计算机'):")
        search_results = recommender.cb_recommender.search_books('计算机', 3)
        for i, (book_id, relevance) in enumerate(search_results, 1):
            book = db.query(Book).filter(Book.id == book_id).first()
            if book:
                print(f"   {i}. 《{book.title}》 (相关度: {relevance})")
        
        print("\n✅ 推荐系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_recommendations()