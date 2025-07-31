#!/usr/bin/env python3
"""
图书馆智能推荐系统 - 简化版演示
不依赖外部库的基础实现
"""

import json
import random
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import csv
import os

class SimpleDatabase:
    """简化的数据库类"""
    
    def __init__(self):
        self.users = []
        self.books = []
        self.ratings = []
        self.borrowings = []
        self.generate_demo_data()
    
    def generate_demo_data(self):
        """生成演示数据"""
        print("正在生成演示数据...")
        
        # 生成用户数据
        user_profiles = ['学生', '教师', '研究员', '图书馆员', '访问学者']
        interests = ['文学', '科学', '历史', '艺术', '哲学', '技术', '医学', '经济', '法律', '教育']
        
        for i in range(1, 51):  # 50个用户
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
        
        for i in range(1, 201):  # 200本书
            category = random.choice(categories)
            self.books.append({
                'book_id': i,
                'title': f'{category}经典著作{i}',
                'author': random.choice(authors),
                'category': category,
                'description': f'这是一本关于{category}的优秀著作。'
            })
        
        # 生成评分数据
        for i in range(500):  # 500条评分记录
            user_id = random.randint(1, 50)
            book_id = random.randint(1, 200)
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
        for i in range(800):  # 800条借阅记录
            user_id = random.randint(1, 50)
            book_id = random.randint(1, 200)
            borrow_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            self.borrowings.append({
                'user_id': user_id,
                'book_id': book_id,
                'borrow_date': borrow_date,
                'status': random.choice(['已归还', '借阅中'])
            })
        
        print(f"生成完成: {len(self.users)}个用户, {len(self.books)}本书, {len(self.ratings)}条评分, {len(self.borrowings)}条借阅记录")

class SimpleRecommendationEngine:
    """简化的推荐引擎"""
    
    def __init__(self, database):
        self.db = database
    
    def get_user_ratings(self, user_id):
        """获取用户评分"""
        return [r for r in self.db.ratings if r['user_id'] == user_id]
    
    def get_book_ratings(self, book_id):
        """获取图书评分"""
        return [r for r in self.db.ratings if r['book_id'] == book_id]
    
    def collaborative_filtering_recommendations(self, user_id, num_recs=10):
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
            
            # 计算皮尔逊相关系数
            sum1 = sum([user_rated_books[book] for book in common_books])
            sum2 = sum([other_rated_books[book] for book in common_books])
            
            sum1_sq = sum([user_rated_books[book]**2 for book in common_books])
            sum2_sq = sum([other_rated_books[book]**2 for book in common_books])
            
            sum_products = sum([user_rated_books[book] * other_rated_books[book] for book in common_books])
            
            n = len(common_books)
            numerator = sum_products - (sum1 * sum2 / n)
            denominator = math.sqrt((sum1_sq - sum1**2/n) * (sum2_sq - sum2**2/n))
            
            if denominator == 0:
                similarity = 0
            else:
                similarity = numerator / denominator
            
            if similarity > 0.1:  # 只考虑相似度大于0.1的用户
                similar_users.append((other_user['user_id'], similarity))
        
        # 按相似度排序
        similar_users.sort(key=lambda x: x[1], reverse=True)
        similar_users = similar_users[:10]  # 取前10个相似用户
        
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
    
    def content_based_recommendations(self, user_id, num_recs=10):
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
    
    def popularity_recommendations(self, num_recs=10):
        """基于流行度的推荐"""
        book_stats = defaultdict(lambda: {'total_rating': 0, 'count': 0})
        
        for rating in self.db.ratings:
            book_stats[rating['book_id']]['total_rating'] += rating['rating']
            book_stats[rating['book_id']]['count'] += 1
        
        # 计算平均评分和流行度分数
        book_scores = []
        for book in self.db.books:
            stats = book_stats[book['book_id']]
            if stats['count'] >= 3:  # 至少有3个评分
                avg_rating = stats['total_rating'] / stats['count']
                popularity_score = avg_rating * 0.7 + math.log(1 + stats['count']) * 0.3
                book_scores.append((book, popularity_score))
        
        # 排序并返回前N个
        book_scores.sort(key=lambda x: x[1], reverse=True)
        return book_scores[:num_recs]
    
    def hybrid_recommendations(self, user_id, num_recs=10):
        """混合推荐"""
        collab_recs = self.collaborative_filtering_recommendations(user_id, num_recs * 2)
        content_recs = self.content_based_recommendations(user_id, num_recs * 2)
        popularity_recs = self.popularity_recommendations(num_recs)
        
        # 合并推荐结果
        hybrid_scores = defaultdict(float)
        
        # 协同过滤权重 0.4
        for book, score in collab_recs:
            hybrid_scores[book['book_id']] += score * 0.4
        
        # 内容过滤权重 0.4
        for book, score in content_recs:
            hybrid_scores[book['book_id']] += score * 0.4
        
        # 流行度权重 0.2
        for book, score in popularity_recs:
            hybrid_scores[book['book_id']] += score * 0.2
        
        # 排序并返回前N个
        final_recs = []
        for book_id, score in hybrid_scores.items():
            book = next((b for b in self.db.books if b['book_id'] == book_id), None)
            if book:
                final_recs.append((book, score))
        
        final_recs.sort(key=lambda x: x[1], reverse=True)
        return final_recs[:num_recs]

class SimpleBehaviorAnalyzer:
    """简化的用户行为分析器"""
    
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
                'favorite_categories': dict(Counter(category_preferences).most_common(5)),
                'favorite_authors': dict(Counter(author_preferences).most_common(3))
            },
            'reading_behavior': {
                'rating_tendency': rating_tendency
            }
        }

def main():
    """主函数 - 演示系统功能"""
    print("=" * 60)
    print("🏛️  图书馆智能推荐系统 - 演示版")
    print("   基于用户行为的个性化推荐")
    print("=" * 60)
    
    # 初始化系统
    db = SimpleDatabase()
    recommender = SimpleRecommendationEngine(db)
    analyzer = SimpleBehaviorAnalyzer(db)
    
    while True:
        print("\n📋 请选择功能:")
        print("1. 查看用户列表")
        print("2. 获取用户推荐")
        print("3. 分析用户行为")
        print("4. 查看系统统计")
        print("5. 退出系统")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == '1':
            print("\n👥 用户列表:")
            for i, user in enumerate(db.users[:10], 1):  # 显示前10个用户
                print(f"{i:2d}. {user['name']} ({user['profile']}, {user['age']}岁)")
                print(f"    兴趣: {', '.join(user['interests'])}")
        
        elif choice == '2':
            try:
                user_id = int(input("\n请输入用户ID (1-50): "))
                if 1 <= user_id <= 50:
                    print("\n📚 推荐算法选择:")
                    print("1. 混合推荐")
                    print("2. 协同过滤")
                    print("3. 内容过滤")
                    print("4. 流行度推荐")
                    
                    method_choice = input("请选择算法 (1-4): ").strip()
                    
                    if method_choice == '1':
                        recommendations = recommender.hybrid_recommendations(user_id)
                        method_name = "混合推荐"
                    elif method_choice == '2':
                        recommendations = recommender.collaborative_filtering_recommendations(user_id)
                        method_name = "协同过滤"
                    elif method_choice == '3':
                        recommendations = recommender.content_based_recommendations(user_id)
                        method_name = "内容过滤"
                    elif method_choice == '4':
                        recommendations = recommender.popularity_recommendations()
                        method_name = "流行度推荐"
                    else:
                        print("❌ 无效选择")
                        continue
                    
                    print(f"\n🌟 {method_name}结果:")
                    if recommendations:
                        for i, (book, score) in enumerate(recommendations, 1):
                            print(f"{i:2d}. {book['title']} - {book['author']}")
                            print(f"    类别: {book['category']} | 推荐分数: {score:.3f}")
                    else:
                        print("❌ 暂无推荐结果")
                else:
                    print("❌ 用户ID超出范围")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        elif choice == '3':
            try:
                user_id = int(input("\n请输入用户ID (1-50): "))
                if 1 <= user_id <= 50:
                    analysis = analyzer.analyze_user_behavior(user_id)
                    
                    if 'error' in analysis:
                        print(f"❌ {analysis['error']}")
                    else:
                        user_info = analysis['user_info']
                        stats = analysis['reading_statistics']
                        prefs = analysis['preference_analysis']
                        behavior = analysis['reading_behavior']
                        
                        print(f"\n📊 用户 {user_info['name']} 行为分析:")
                        print(f"👤 基本信息: {user_info['profile']}, {user_info['age']}岁")
                        print(f"📈 阅读统计: {stats['total_ratings']}次评分, {stats['total_borrowings']}次借阅")
                        print(f"⭐ 平均评分: {stats['average_rating']}")
                        print(f"📚 当前借阅: {stats['active_borrowings']}本")
                        print(f"💡 评分倾向: {behavior['rating_tendency']}")
                        
                        if prefs['favorite_categories']:
                            print("❤️  喜爱类别:")
                            for category, count in prefs['favorite_categories'].items():
                                print(f"   - {category}: {count}本高分图书")
                else:
                    print("❌ 用户ID超出范围")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        elif choice == '4':
            print("\n📈 系统统计:")
            print(f"👥 用户总数: {len(db.users)}")
            print(f"📚 图书总数: {len(db.books)}")
            print(f"⭐ 评分总数: {len(db.ratings)}")
            print(f"📖 借阅总数: {len(db.borrowings)}")
            
            # 最受欢迎的类别
            category_counts = Counter()
            for book in db.books:
                category_counts[book['category']] += 1
            
            print("\n📊 图书类别分布:")
            for category, count in category_counts.most_common(5):
                print(f"   {category}: {count}本")
        
        elif choice == '5':
            print("\n👋 感谢使用图书馆智能推荐系统！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 系统已退出")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")