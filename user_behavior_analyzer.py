import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class UserBehaviorAnalyzer:
    """用户行为分析器"""
    
    def __init__(self, database):
        self.db = database
    
    def analyze_user_behavior(self, user_id):
        """分析单个用户的行为"""
        user_profile = self.db.get_user_profile(user_id)
        if not user_profile:
            return {"error": "用户不存在"}
        
        user_ratings = self.db.get_user_ratings(user_id)
        user_borrowings = self.db.get_user_borrowings(user_id)
        
        analysis = {
            "user_info": user_profile,
            "reading_statistics": self._calculate_reading_stats(user_ratings, user_borrowings),
            "preference_analysis": self._analyze_preferences(user_id, user_ratings, user_borrowings),
            "activity_pattern": self._analyze_activity_pattern(user_ratings, user_borrowings),
            "reading_behavior": self._analyze_reading_behavior(user_ratings, user_borrowings)
        }
        
        return analysis
    
    def _calculate_reading_stats(self, ratings, borrowings):
        """计算阅读统计信息"""
        stats = {
            "total_ratings": len(ratings),
            "total_borrowings": len(borrowings),
            "average_rating": float(ratings['rating'].mean()) if not ratings.empty else 0,
            "rating_distribution": ratings['rating'].value_counts().to_dict() if not ratings.empty else {},
            "active_borrowings": len(borrowings[borrowings['status'] == '借阅中']) if not borrowings.empty else 0
        }
        return stats
    
    def _analyze_preferences(self, user_id, ratings, borrowings):
        """分析用户偏好"""
        preferences = {}
        
        # 分析评分过的图书类别偏好
        if not ratings.empty:
            rated_books = ratings.merge(self.db.books_df, on='book_id')
            category_ratings = rated_books.groupby('category')['rating'].agg(['mean', 'count']).round(2)
            preferences['category_ratings'] = category_ratings.to_dict('index')
            
            # 最喜欢的类别（评分>=4的书籍类别）
            high_rated = rated_books[rated_books['rating'] >= 4]
            if not high_rated.empty:
                favorite_categories = high_rated['category'].value_counts().head(5).to_dict()
                preferences['favorite_categories'] = favorite_categories
        
        # 分析借阅过的图书类别偏好
        if not borrowings.empty:
            borrowed_books = borrowings.merge(self.db.books_df, on='book_id')
            borrowing_categories = borrowed_books['category'].value_counts().head(10).to_dict()
            preferences['borrowing_categories'] = borrowing_categories
            
            # 分析作者偏好
            author_borrowings = borrowed_books['author'].value_counts().head(5).to_dict()
            preferences['favorite_authors'] = author_borrowings
        
        # 用户兴趣匹配度
        user_profile = self.db.get_user_profile(user_id)
        if user_profile and 'interests' in user_profile:
            user_interests = user_profile['interests'].split(',')
            preferences['declared_interests'] = user_interests
            
            # 计算声明兴趣与实际行为的匹配度
            if not ratings.empty:
                rated_books = ratings.merge(self.db.books_df, on='book_id')
                actual_categories = set(rated_books['category'].unique())
                declared_interests = set(user_interests)
                match_score = len(actual_categories.intersection(declared_interests)) / len(declared_interests) if declared_interests else 0
                preferences['interest_match_score'] = round(match_score, 2)
        
        return preferences
    
    def _analyze_activity_pattern(self, ratings, borrowings):
        """分析活动模式"""
        pattern = {}
        
        if not ratings.empty:
            # 转换时间戳
            ratings_copy = ratings.copy()
            ratings_copy['timestamp'] = pd.to_datetime(ratings_copy['timestamp'])
            
            # 按月份分析评分活动
            ratings_copy['month'] = ratings_copy['timestamp'].dt.month
            monthly_ratings = ratings_copy['month'].value_counts().sort_index().to_dict()
            pattern['monthly_rating_activity'] = monthly_ratings
            
            # 最近活动
            recent_ratings = ratings_copy[ratings_copy['timestamp'] > datetime.now() - timedelta(days=30)]
            pattern['recent_ratings_count'] = len(recent_ratings)
        
        if not borrowings.empty:
            # 转换借阅日期
            borrowings_copy = borrowings.copy()
            borrowings_copy['borrow_date'] = pd.to_datetime(borrowings_copy['borrow_date'])
            
            # 按月份分析借阅活动
            borrowings_copy['month'] = borrowings_copy['borrow_date'].dt.month
            monthly_borrowings = borrowings_copy['month'].value_counts().sort_index().to_dict()
            pattern['monthly_borrowing_activity'] = monthly_borrowings
            
            # 借阅频率分析
            borrowings_copy['week'] = borrowings_copy['borrow_date'].dt.isocalendar().week
            weekly_borrowings = borrowings_copy['week'].value_counts().describe().to_dict()
            pattern['borrowing_frequency_stats'] = {k: round(v, 2) for k, v in weekly_borrowings.items()}
        
        return pattern
    
    def _analyze_reading_behavior(self, ratings, borrowings):
        """分析阅读行为"""
        behavior = {}
        
        # 评分行为分析
        if not ratings.empty:
            behavior['rating_tendency'] = self._classify_rating_tendency(ratings['rating'])
            behavior['rating_consistency'] = round(ratings['rating'].std(), 2)
        
        # 借阅行为分析
        if not borrowings.empty:
            # 归还及时性
            returned_books = borrowings[borrowings['status'] == '已归还'].copy()
            if not returned_books.empty:
                returned_books['borrow_date'] = pd.to_datetime(returned_books['borrow_date'])
                returned_books['return_date'] = pd.to_datetime(returned_books['return_date'])
                returned_books['borrow_duration'] = (returned_books['return_date'] - returned_books['borrow_date']).dt.days
                
                avg_duration = returned_books['borrow_duration'].mean()
                behavior['average_borrow_duration'] = round(avg_duration, 1)
                behavior['return_punctuality'] = 'excellent' if avg_duration <= 14 else 'good' if avg_duration <= 21 else 'needs_improvement'
            
            # 重复借阅分析
            book_borrow_counts = borrowings['book_id'].value_counts()
            repeated_books = book_borrow_counts[book_borrow_counts > 1]
            behavior['repeated_borrowing_count'] = len(repeated_books)
            
            if len(repeated_books) > 0:
                behavior['most_borrowed_books'] = repeated_books.head(3).to_dict()
        
        return behavior
    
    def _classify_rating_tendency(self, ratings):
        """分类评分倾向"""
        avg_rating = ratings.mean()
        if avg_rating >= 4.0:
            return "positive"  # 积极评分者
        elif avg_rating >= 3.0:
            return "moderate"  # 中等评分者
        else:
            return "critical"  # 挑剔评分者
    
    def generate_user_behavior_report(self, user_id):
        """生成用户行为报告"""
        analysis = self.analyze_user_behavior(user_id)
        
        if "error" in analysis:
            return analysis
        
        # 生成文本报告
        report = []
        user_info = analysis['user_info']
        stats = analysis['reading_statistics']
        preferences = analysis['preference_analysis']
        
        report.append(f"## 用户 {user_info['name']} 行为分析报告")
        report.append(f"**用户类型**: {user_info['profile']}")
        report.append(f"**年龄**: {user_info['age']}岁")
        report.append("")
        
        report.append("### 阅读统计")
        report.append(f"- 总评分数: {stats['total_ratings']}")
        report.append(f"- 总借阅数: {stats['total_borrowings']}")
        report.append(f"- 平均评分: {stats['average_rating']:.2f}")
        report.append(f"- 当前借阅中: {stats['active_borrowings']} 本")
        report.append("")
        
        if 'favorite_categories' in preferences:
            report.append("### 喜爱类别")
            for category, count in list(preferences['favorite_categories'].items())[:3]:
                report.append(f"- {category}: {count} 本高分图书")
            report.append("")
        
        return {
            'analysis': analysis,
            'report_text': '\n'.join(report)
        }
    
    def get_global_statistics(self):
        """获取全局统计信息"""
        stats = {}
        
        # 用户活跃度统计
        user_activity = self.db.ratings_df.groupby('user_id').size().describe()
        stats['user_activity_stats'] = user_activity.to_dict()
        
        # 图书受欢迎程度
        book_popularity = self.db.ratings_df.groupby('book_id').agg({
            'rating': ['mean', 'count']
        }).round(2)
        book_popularity.columns = ['avg_rating', 'rating_count']
        popular_books = book_popularity.sort_values(['rating_count', 'avg_rating'], ascending=False).head(10)
        stats['popular_books'] = popular_books.to_dict('index')
        
        # 类别统计
        category_stats = self.db.books_df['category'].value_counts().to_dict()
        stats['category_distribution'] = category_stats
        
        return stats