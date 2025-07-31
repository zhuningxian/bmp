#!/usr/bin/env python3
"""
图书馆智能推荐系统自动演示脚本
"""

import json
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class DemoDatabase:
    """演示数据库"""
    
    def __init__(self):
        self.users = []
        self.books = []
        self.ratings = []
        self.borrowings = []
        self.generate_demo_data()
    
    def generate_demo_data(self):
        """生成演示数据"""
        print("🔄 正在生成演示数据...")
        
        # 生成用户数据
        user_profiles = ['学生', '教师', '研究员', '图书馆员', '访问学者']
        interests = ['文学', '科学', '历史', '艺术', '哲学', '技术', '医学', '经济', '法律', '教育']
        
        for i in range(1, 21):  # 20个用户
            user_interests = random.sample(interests, random.randint(2, 4))
            self.users.append({
                'user_id': i,
                'name': f'用户{i}',
                'profile': random.choice(user_profiles),
                'age': random.randint(18, 65),
                'interests': user_interests
            })
        
        # 生成图书数据
        categories = interests
        authors = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
        
        for i in range(1, 101):  # 100本书
            category = random.choice(categories)
            self.books.append({
                'book_id': i,
                'title': f'{category}经典著作{i}',
                'author': random.choice(authors),
                'category': category,
                'description': f'这是一本关于{category}的优秀著作。'
            })
        
        # 生成评分数据
        for i in range(200):  # 200条评分记录
            user_id = random.randint(1, 20)
            book_id = random.randint(1, 100)
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 25, 35, 25])[0]
            
            # 避免重复评分
            existing = [r for r in self.ratings if r['user_id'] == user_id and r['book_id'] == book_id]
            if not existing:
                self.ratings.append({
                    'user_id': user_id,
                    'book_id': book_id,
                    'rating': rating,
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 365))
                })
        
        # 生成借阅数据
        for i in range(300):  # 300条借阅记录
            user_id = random.randint(1, 20)
            book_id = random.randint(1, 100)
            borrow_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            self.borrowings.append({
                'user_id': user_id,
                'book_id': book_id,
                'borrow_date': borrow_date,
                'status': random.choice(['已归还', '借阅中'])
            })
        
        print(f"✅ 生成完成: {len(self.users)}个用户, {len(self.books)}本书, {len(self.ratings)}条评分, {len(self.borrowings)}条借阅记录")

class DemoRecommendationEngine:
    """演示推荐引擎"""
    
    def __init__(self, database):
        self.db = database
    
    def get_user_ratings(self, user_id):
        """获取用户评分"""
        return [r for r in self.db.ratings if r['user_id'] == user_id]
    
    def collaborative_filtering_recommendations(self, user_id, num_recs=5):
        """协同过滤推荐"""
        user_ratings = self.get_user_ratings(user_id)
        if not user_ratings:
            return self.popularity_recommendations(num_recs)
        
        user_rated_books = {r['book_id']: r['rating'] for r in user_ratings}
        
        # 找到相似用户
        similar_users = []
        for other_user in self.db.users:
            if other_user['user_id'] == user_id:
                continue
            
            other_ratings = self.get_user_ratings(other_user['user_id'])
            other_rated_books = {r['book_id']: r['rating'] for r in other_ratings}
            
            # 计算共同评分的书籍
            common_books = set(user_rated_books.keys()) & set(other_rated_books.keys())
            if len(common_books) < 2:
                continue
            
            # 简化的相似度计算
            similarity_score = 0
            for book_id in common_books:
                similarity_score += 1 - abs(user_rated_books[book_id] - other_rated_books[book_id]) / 4
            
            similarity = similarity_score / len(common_books)
            if similarity > 0.3:
                similar_users.append((other_user['user_id'], similarity))
        
        # 按相似度排序
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:5]  # 取前5个相似用户
        
        # 生成推荐
        recommendations = defaultdict(float)
        similarity_sum = defaultdict(float)
        
        for similar_user_id, similarity in similar_users:
            similar_ratings = self.get_user_ratings(similar_user_id)
            for rating in similar_ratings:
                if rating['book_id'] not in user_rated_books:  # 用户未评分的书
                    recommendations[rating['book_id']] += similarity * rating['rating']
                    similarity_sum[rating['book_id']] += similarity
        
        # 计算加权平均分
        final_recs = []
        for book_id, weighted_sum in recommendations.items():
            if similarity_sum[book_id] > 0:
                score = weighted_sum / similarity_sum[book_id]
                book = next((b for b in self.db.books if b['book_id'] == book_id), None)
                if book:
                    final_recs.append((book, score))
        
        # 排序并返回前N个
        final_recs.sort(key=lambda x: x[1], reverse=True)
        return final_recs[:num_recs]
    
    def content_based_recommendations(self, user_id, num_recs=5):
        """基于内容的推荐"""
        user_ratings = self.get_user_ratings(user_id)
        if not user_ratings:
            return self.popularity_recommendations(num_recs)
        
        # 获取用户喜欢的书籍类别（评分>=4）
        liked_categories = []
        user_rated_books = set()
        
        for rating in user_ratings:
            user_rated_books.add(rating['book_id'])
            if rating['rating'] >= 4:
                book = next((b for b in self.db.books if b['book_id'] == rating['book_id']), None)
                if book:
                    liked_categories.append(book['category'])
        
        # 统计喜欢的类别
        category_scores = Counter(liked_categories)
        
        if not category_scores:
            return self.popularity_recommendations(num_recs)
        
        # 推荐同类别的书籍
        recommendations = []
        for book in self.db.books:
            if book['book_id'] not in user_rated_books:  # 用户未评分的书
                if book['category'] in category_scores:
                    score = category_scores[book['category']] / len(liked_categories)
                    recommendations.append((book, score))
        
        # 排序并返回前N个
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:num_recs]
    
    def popularity_recommendations(self, num_recs=5):
        """基于流行度的推荐"""
        book_stats = defaultdict(lambda: {'total_rating': 0, 'count': 0})
        
        for rating in self.db.ratings:
            book_stats[rating['book_id']]['total_rating'] += rating['rating']
            book_stats[rating['book_id']]['count'] += 1
        
        # 计算平均评分和流行度分数
        book_scores = []
        for book in self.db.books:
            stats = book_stats[book['book_id']]
            if stats['count'] >= 2:  # 至少有2个评分
                avg_rating = stats['total_rating'] / stats['count']
                popularity_score = avg_rating * 0.7 + math.log(1 + stats['count']) * 0.3
                book_scores.append((book, popularity_score))
        
        # 排序并返回前N个
        book_scores.sort(key=lambda x: x[1], reverse=True)
        return book_scores[:num_recs]

class DemoBehaviorAnalyzer:
    """演示用户行为分析器"""
    
    def __init__(self, database):
        self.db = database
    
    def analyze_user_behavior(self, user_id):
        """分析用户行为"""
        user = next((u for u in self.db.users if u['user_id'] == user_id), None)
        if not user:
            return {"error": "用户不存在"}
        
        user_ratings = [r for r in self.db.ratings if r['user_id'] == user_id]
        user_borrowings = [b for b in self.db.borrowings if b['user_id'] == user_id]
        
        # 基本统计
        total_ratings = len(user_ratings)
        total_borrowings = len(user_borrowings)
        avg_rating = sum(r['rating'] for r in user_ratings) / total_ratings if total_ratings > 0 else 0
        active_borrowings = len([b for b in user_borrowings if b['status'] == '借阅中'])
        
        # 偏好分析
        category_preferences = defaultdict(int)
        author_preferences = defaultdict(int)
        
        for rating in user_ratings:
            if rating['rating'] >= 4:  # 高分书籍
                book = next((b for b in self.db.books if b['book_id'] == rating['book_id']), None)
                if book:
                    category_preferences[book['category']] += 1
                    author_preferences[book['author']] += 1
        
        # 评分倾向
        if avg_rating >= 4.0:
            rating_tendency = "积极评分者"
        elif avg_rating >= 3.0:
            rating_tendency = "中等评分者"
        else:
            rating_tendency = "挑剔评分者"
        
        return {
            'user_info': user,
            'reading_statistics': {
                'total_ratings': total_ratings,
                'total_borrowings': total_borrowings,
                'average_rating': round(avg_rating, 2),
                'active_borrowings': active_borrowings
            },
            'preference_analysis': {
                'favorite_categories': dict(Counter(category_preferences).most_common(3)),
                'favorite_authors': dict(Counter(author_preferences).most_common(2))
            },
            'reading_behavior': {
                'rating_tendency': rating_tendency
            }
        }

def demo_system():
    """演示系统功能"""
    print("=" * 80)
    print("🏛️  图书馆智能推荐系统 - 自动演示")
    print("   基于用户行为的个性化推荐算法演示")
    print("=" * 80)
    
    # 初始化系统
    db = DemoDatabase()
    recommender = DemoRecommendationEngine(db)
    analyzer = DemoBehaviorAnalyzer(db)
    
    print("\n📈 系统统计信息:")
    print(f"👥 用户总数: {len(db.users)}")
    print(f"📚 图书总数: {len(db.books)}")
    print(f"⭐ 评分总数: {len(db.ratings)}")
    print(f"📖 借阅总数: {len(db.borrowings)}")
    
    # 演示用户样例
    demo_users = [1, 5, 10, 15]
    
    for user_id in demo_users:
        print("\n" + "="*60)
        print(f"🔍 演示用户 {user_id} 的推荐系统")
        print("="*60)
        
        # 显示用户信息
        user = next((u for u in db.users if u['user_id'] == user_id), None)
        if user:
            print(f"\n👤 用户信息:")
            print(f"   姓名: {user['name']}")
            print(f"   类型: {user['profile']}")
            print(f"   年龄: {user['age']}岁")
            print(f"   兴趣: {', '.join(user['interests'])}")
        
        # 用户行为分析
        print(f"\n📊 用户行为分析:")
        analysis = analyzer.analyze_user_behavior(user_id)
        if 'error' not in analysis:
            stats = analysis['reading_statistics']
            prefs = analysis['preference_analysis']
            behavior = analysis['reading_behavior']
            
            print(f"   📈 阅读统计: {stats['total_ratings']}次评分, {stats['total_borrowings']}次借阅")
            print(f"   ⭐ 平均评分: {stats['average_rating']}")
            print(f"   📚 当前借阅: {stats['active_borrowings']}本")
            print(f"   💡 评分倾向: {behavior['rating_tendency']}")
            
            if prefs['favorite_categories']:
                print(f"   ❤️  喜爱类别: {', '.join(prefs['favorite_categories'].keys())}")
        
        # 推荐算法演示
        algorithms = [
            ('混合推荐', 'hybrid'),
            ('协同过滤', 'collaborative'),
            ('内容过滤', 'content'),
            ('流行度推荐', 'popularity')
        ]
        
        for algo_name, algo_type in algorithms:
            print(f"\n🌟 {algo_name}结果:")
            
            if algo_type == 'hybrid':
                # 简化的混合推荐
                collab_recs = recommender.collaborative_filtering_recommendations(user_id, 3)
                content_recs = recommender.content_based_recommendations(user_id, 3)
                recommendations = collab_recs[:2] + content_recs[:2]
            elif algo_type == 'collaborative':
                recommendations = recommender.collaborative_filtering_recommendations(user_id, 4)
            elif algo_type == 'content':
                recommendations = recommender.content_based_recommendations(user_id, 4)
            elif algo_type == 'popularity':
                recommendations = recommender.popularity_recommendations(4)
            
            if recommendations:
                for i, (book, score) in enumerate(recommendations, 1):
                    print(f"   {i}. {book['title']} - {book['author']}")
                    print(f"      类别: {book['category']} | 推荐分数: {score:.3f}")
            else:
                print("   ❌ 暂无推荐结果")
        
        print("\n" + "-"*60)
    
    print("\n🎯 推荐算法对比分析:")
    print("""
    🔹 协同过滤推荐:
       - 基于用户相似度计算推荐
       - 适合有丰富历史数据的用户
       - "喜欢这本书的用户还喜欢..."
    
    🔹 内容过滤推荐:
       - 基于图书内容特征匹配
       - 适合新用户或特定兴趣用户
       - "因为您读过XX类书籍..."
    
    🔹 流行度推荐:
       - 基于图书整体受欢迎程度
       - 适合冷启动场景
       - "热门推荐"
    
    🔹 混合推荐:
       - 综合多种算法的优势
       - 平衡个性化和多样性
       - 最佳推荐效果
    """)
    
    print("\n" + "="*80)
    print("🎉 演示完成！图书馆智能推荐系统展示了基于用户行为的")
    print("   多种推荐算法，能够为不同类型用户提供个性化推荐服务。")
    print("="*80)

if __name__ == '__main__':
    try:
        demo_system()
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")