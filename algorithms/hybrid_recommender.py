import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .collaborative_filtering import CollaborativeFilteringRecommender
from .content_based import ContentBasedRecommender
from models.database import User, Book, Rating, Borrowing

class HybridRecommender:
    """混合推荐系统"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.cf_recommender = CollaborativeFilteringRecommender(db_session)
        self.cb_recommender = ContentBasedRecommender(db_session)
        self.books_df = None
        
    def initialize(self):
        """初始化推荐系统"""
        # 加载数据
        self.cf_recommender.load_data()
        self.cb_recommender.load_data()
        
        # 预计算相似度矩阵
        self.cf_recommender.create_user_item_matrix()
        self.cb_recommender.calculate_book_similarity()
        
        # 训练协同过滤模型
        self.cf_recommender.train_svd_model()
        
        # 获取图书信息
        self.books_df = self.cb_recommender.books_df
        
    def get_hybrid_recommendations(self, user_id, n_recommendations=10, 
                                 cf_weight=0.6, cb_weight=0.4):
        """
        混合推荐算法
        
        Args:
            user_id: 用户ID
            n_recommendations: 推荐数量
            cf_weight: 协同过滤权重
            cb_weight: 基于内容推荐权重
        """
        # 获取协同过滤推荐
        cf_recommendations = []
        try:
            # 尝试使用SVD模型
            cf_recommendations = self.cf_recommender.get_svd_recommendations(
                user_id, n_recommendations * 2
            )
            
            # 如果SVD推荐结果不足，补充基于用户的协同过滤
            if len(cf_recommendations) < n_recommendations:
                user_based_recs = self.cf_recommender.get_user_based_recommendations(
                    user_id, n_recommendations * 2
                )
                cf_recommendations.extend(user_based_recs)
                
        except Exception as e:
            print(f"协同过滤推荐出错: {e}")
            cf_recommendations = []
        
        # 获取基于内容的推荐
        cb_recommendations = []
        try:
            cb_recommendations = self.cb_recommender.get_content_based_recommendations(
                user_id, n_recommendations * 2
            )
        except Exception as e:
            print(f"基于内容推荐出错: {e}")
            cb_recommendations = []
        
        # 合并推荐结果
        hybrid_scores = {}
        
        # 处理协同过滤推荐
        for book_id, score in cf_recommendations:
            if book_id not in hybrid_scores:
                hybrid_scores[book_id] = 0
            hybrid_scores[book_id] += cf_weight * score
        
        # 处理基于内容的推荐
        for book_id, score in cb_recommendations:
            if book_id not in hybrid_scores:
                hybrid_scores[book_id] = 0
            hybrid_scores[book_id] += cb_weight * score
        
        # 如果推荐结果不足，添加热门图书
        if len(hybrid_scores) < n_recommendations:
            popular_books = self.cb_recommender.get_popular_books(n_recommendations)
            for book_id, score in popular_books:
                if book_id not in hybrid_scores:
                    hybrid_scores[book_id] = 0.1 * score  # 较低权重
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            hybrid_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_recommendations[:n_recommendations]
    
    def get_adaptive_recommendations(self, user_id, n_recommendations=10):
        """
        自适应推荐：根据用户数据量调整策略
        """
        # 获取用户评分数据
        user_ratings_count = self.db_session.query(Rating).filter(
            Rating.user_id == user_id
        ).count()
        
        # 获取用户借阅数据
        user_borrowings_count = self.db_session.query(Borrowing).filter(
            Borrowing.user_id == user_id
        ).count()
        
        total_interactions = user_ratings_count + user_borrowings_count
        
        if total_interactions == 0:
            # 新用户：主要基于热门图书
            return self.get_new_user_recommendations(user_id, n_recommendations)
        elif total_interactions < 5:
            # 数据稀少：主要基于内容
            return self.get_hybrid_recommendations(
                user_id, n_recommendations, cf_weight=0.2, cb_weight=0.8
            )
        elif total_interactions < 20:
            # 中等数据：平衡混合
            return self.get_hybrid_recommendations(
                user_id, n_recommendations, cf_weight=0.5, cb_weight=0.5
            )
        else:
            # 数据丰富：主要基于协同过滤
            return self.get_hybrid_recommendations(
                user_id, n_recommendations, cf_weight=0.7, cb_weight=0.3
            )
    
    def get_new_user_recommendations(self, user_id, n_recommendations=10):
        """新用户推荐策略"""
        recommendations = []
        
        # 获取用户信息
        user = self.db_session.query(User).filter(User.id == user_id).first()
        
        # 1. 热门图书 (40%)
        popular_books = self.cb_recommender.get_popular_books(int(n_recommendations * 0.4))
        recommendations.extend([(book_id, score * 0.4) for book_id, score in popular_books])
        
        # 2. 不同类别的代表性图书 (60%)
        categories = ['小说', '科学', '历史', '传记', '技术', '文学']
        books_per_category = max(1, int(n_recommendations * 0.6 / len(categories)))
        
        for category in categories:
            category_books = self.cb_recommender.get_books_by_category(
                category, books_per_category
            )
            recommendations.extend([(book_id, score * 0.6) for book_id, score in category_books])
        
        # 去重并排序
        unique_recommendations = {}
        for book_id, score in recommendations:
            if book_id not in unique_recommendations:
                unique_recommendations[book_id] = score
            else:
                unique_recommendations[book_id] += score
        
        sorted_recommendations = sorted(
            unique_recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_recommendations[:n_recommendations]
    
    def get_category_recommendations(self, user_id, category, n_recommendations=10):
        """按类别推荐"""
        # 先获取该类别的所有图书
        category_books = self.cb_recommender.get_books_by_category(
            category, n_recommendations * 3
        )
        
        if not category_books:
            return []
        
        # 获取用户在该类别的历史行为
        user_ratings = self.db_session.query(Rating).join(Book).filter(
            Rating.user_id == user_id,
            Book.category.contains(category)
        ).all()
        
        if not user_ratings:
            # 没有该类别的历史，返回该类别的热门图书
            return category_books[:n_recommendations]
        
        # 基于用户在该类别的偏好进行推荐
        cb_recommendations = self.cb_recommender.get_content_based_recommendations(
            user_id, n_recommendations * 2
        )
        
        # 过滤出该类别的推荐
        category_recommendations = []
        category_book_ids = set([book_id for book_id, _ in category_books])
        
        for book_id, score in cb_recommendations:
            if book_id in category_book_ids:
                category_recommendations.append((book_id, score))
        
        return category_recommendations[:n_recommendations]
    
    def get_similar_users(self, user_id, n_users=10):
        """获取相似用户"""
        if self.cf_recommender.user_item_matrix is None:
            return []
            
        if user_id not in self.cf_recommender.user_item_matrix.index:
            return []
        
        from sklearn.metrics.pairwise import cosine_similarity
        
        # 计算用户相似度
        user_similarities = cosine_similarity(self.cf_recommender.user_item_matrix)
        user_sim_df = pd.DataFrame(
            user_similarities,
            index=self.cf_recommender.user_item_matrix.index,
            columns=self.cf_recommender.user_item_matrix.index
        )
        
        # 获取相似用户
        similar_users = user_sim_df[user_id].sort_values(ascending=False)[1:n_users+1]
        
        return [(user_id, similarity) for user_id, similarity in similar_users.items()]
    
    def explain_recommendation(self, user_id, book_id):
        """解释推荐原因"""
        explanations = []
        
        # 获取图书信息
        book = self.db_session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return ["未找到该图书信息"]
        
        # 检查用户评分历史
        user_ratings = self.db_session.query(Rating).filter(
            Rating.user_id == user_id
        ).all()
        
        if user_ratings:
            # 找相似的已评分图书
            for rating in user_ratings:
                if rating.rating >= 4:  # 高分图书
                    rated_book = self.db_session.query(Book).filter(
                        Book.id == rating.book_id
                    ).first()
                    
                    if rated_book and rated_book.category == book.category:
                        explanations.append(
                            f"因为您喜欢《{rated_book.title}》，推荐同类别的《{book.title}》"
                        )
                        break
                    
                    if rated_book and rated_book.author == book.author:
                        explanations.append(
                            f"因为您喜欢{rated_book.author}的作品，推荐《{book.title}》"
                        )
                        break
        
        # 检查热门度
        borrowing_count = self.db_session.query(Borrowing).filter(
            Borrowing.book_id == book_id
        ).count()
        
        if borrowing_count > 10:
            explanations.append(f"《{book.title}》是热门图书，已被借阅{borrowing_count}次")
        
        # 检查相似用户
        similar_users = self.get_similar_users(user_id, 5)
        if similar_users:
            explanations.append("根据相似用户的喜好推荐")
        
        if not explanations:
            explanations.append("基于您的阅读偏好推荐")
        
        return explanations
    
    def get_book_details_with_recommendations(self, book_id):
        """获取图书详情及相关推荐"""
        book = self.db_session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None
        
        # 获取相似图书
        similar_books = []
        if self.cb_recommender.book_similarity is not None:
            book_idx = self.cb_recommender.books_df[
                self.cb_recommender.books_df['book_id'] == book_id
            ].index
            
            if len(book_idx) > 0:
                book_idx = book_idx[0]
                similarities = list(enumerate(self.cb_recommender.book_similarity[book_idx]))
                similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
                
                for idx, similarity in similarities[1:6]:  # 取前5个相似图书
                    similar_book_id = self.cb_recommender.books_df.iloc[idx]['book_id']
                    similar_books.append((similar_book_id, similarity))
        
        return {
            'book': book,
            'similar_books': similar_books,
            'borrowing_count': self.db_session.query(Borrowing).filter(
                Borrowing.book_id == book_id
            ).count(),
            'average_rating': self.db_session.query(Rating).filter(
                Rating.book_id == book_id
            ).with_entities(Rating.rating).all()
        }