import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from scipy.sparse import csr_matrix
import pickle
from datetime import datetime, timedelta
from models import db, User, Book, Borrowing, Rating, UserBehavior

class RecommendationEngine:
    """智能推荐引擎"""
    
    def __init__(self):
        self.user_book_matrix = None
        self.book_similarity_matrix = None
        self.user_similarity_matrix = None
        self.nmf_model = None
        self.tfidf_vectorizer = None
        self.book_features = None
        
    def load_data(self):
        """从数据库加载数据"""
        # 加载借阅数据
        borrowings = pd.read_sql(
            db.session.query(Borrowing).statement, 
            db.session.bind
        )
        
        # 加载评分数据
        ratings = pd.read_sql(
            db.session.query(Rating).statement, 
            db.session.bind
        )
        
        # 加载用户行为数据
        behaviors = pd.read_sql(
            db.session.query(UserBehavior).statement, 
            db.session.bind
        )
        
        # 加载图书数据
        books = pd.read_sql(
            db.session.query(Book).statement, 
            db.session.bind
        )
        
        return borrowings, ratings, behaviors, books
    
    def create_user_book_matrix(self, borrowings, ratings, behaviors):
        """创建用户-图书交互矩阵"""
        # 合并所有交互数据
        interactions = []
        
        # 借阅记录权重为3
        for _, row in borrowings.iterrows():
            interactions.append({
                'user_id': row['user_id'],
                'book_id': row['book_id'],
                'weight': 3.0
            })
        
        # 评分记录权重为评分值
        for _, row in ratings.iterrows():
            interactions.append({
                'user_id': row['user_id'],
                'book_id': row['book_id'],
                'weight': row['rating']
            })
        
        # 行为记录权重
        behavior_weights = {
            'view': 0.5,
            'search': 0.3,
            'bookmark': 2.0,
            'share': 1.5
        }
        
        for _, row in behaviors.iterrows():
            weight = behavior_weights.get(row['behavior_type'], 0.1)
            # 根据停留时间调整权重
            if row['duration']:
                weight *= min(row['duration'] / 60, 2.0)  # 最多2倍权重
            interactions.append({
                'user_id': row['user_id'],
                'book_id': row['book_id'],
                'weight': weight
            })
        
        # 创建DataFrame
        interactions_df = pd.DataFrame(interactions)
        
        # 聚合相同用户-图书对的权重
        interactions_df = interactions_df.groupby(['user_id', 'book_id'])['weight'].sum().reset_index()
        
        # 创建用户-图书矩阵
        self.user_book_matrix = interactions_df.pivot(
            index='user_id', 
            columns='book_id', 
            values='weight'
        ).fillna(0)
        
        return self.user_book_matrix
    
    def collaborative_filtering(self, user_id, n_recommendations=10):
        """协同过滤推荐"""
        if user_id not in self.user_book_matrix.index:
            return []
        
        # 计算用户相似度
        user_similarities = cosine_similarity(
            self.user_book_matrix.loc[[user_id]], 
            self.user_book_matrix
        )[0]
        
        # 找到最相似的用户
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # 排除自己
        
        # 获取相似用户喜欢的图书
        user_books = set(self.user_book_matrix.columns[self.user_book_matrix.loc[user_id] > 0])
        recommendations = {}
        
        for similar_user_idx in similar_users:
            similar_user_id = self.user_book_matrix.index[similar_user_idx]
            similarity = user_similarities[similar_user_idx]
            
            # 获取相似用户的图书
            similar_user_books = self.user_book_matrix.loc[similar_user_id]
            for book_id, weight in similar_user_books.items():
                if book_id not in user_books and weight > 0:
                    if book_id not in recommendations:
                        recommendations[book_id] = 0
                    recommendations[book_id] += weight * similarity
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [book_id for book_id, score in sorted_recommendations[:n_recommendations]]
    
    def content_based_filtering(self, user_id, books_df, n_recommendations=10):
        """基于内容的推荐"""
        if user_id not in self.user_book_matrix.index:
            return []
        
        # 获取用户喜欢的图书
        user_books = self.user_book_matrix.loc[user_id]
        user_liked_books = user_books[user_books > 0].index.tolist()
        
        if not user_liked_books:
            return []
        
        # 创建图书特征向量
        book_features = books_df[['title', 'author', 'category', 'description']].fillna('')
        book_features['combined'] = (
            book_features['title'] + ' ' + 
            book_features['author'] + ' ' + 
            book_features['category'] + ' ' + 
            book_features['description']
        )
        
        # TF-IDF向量化
        if self.tfidf_vectorizer is None:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000, 
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.book_features = self.tfidf_vectorizer.fit_transform(book_features['combined'])
        
        # 计算图书相似度
        book_similarities = cosine_similarity(self.book_features)
        
        # 获取用户喜欢的图书索引
        liked_book_indices = []
        for book_id in user_liked_books:
            if book_id in books_df.index:
                liked_book_indices.append(books_df.index.get_loc(book_id))
        
        if not liked_book_indices:
            return []
        
        # 计算用户对每本书的兴趣分数
        user_profile = np.mean([book_similarities[i] for i in liked_book_indices], axis=0)
        
        # 排除用户已经喜欢的图书
        for book_id in user_liked_books:
            if book_id in books_df.index:
                idx = books_df.index.get_loc(book_id)
                user_profile[idx] = 0
        
        # 返回推荐
        recommended_indices = np.argsort(user_profile)[::-1][:n_recommendations]
        return [books_df.index[i] for i in recommended_indices]
    
    def matrix_factorization(self, user_id, n_recommendations=10):
        """矩阵分解推荐"""
        if user_id not in self.user_book_matrix.index:
            return []
        
        # 使用NMF进行矩阵分解
        if self.nmf_model is None:
            self.nmf_model = NMF(n_components=50, random_state=42)
            self.nmf_model.fit(self.user_book_matrix)
        
        # 获取用户和图书的潜在特征
        user_features = self.nmf_model.transform(self.user_book_matrix)
        book_features = self.nmf_model.components_.T
        
        # 找到用户索引
        user_idx = self.user_book_matrix.index.get_loc(user_id)
        
        # 预测用户对所有图书的评分
        user_profile = user_features[user_idx]
        predicted_ratings = np.dot(book_features, user_profile)
        
        # 获取用户已经交互过的图书
        user_books = set(self.user_book_matrix.columns[self.user_book_matrix.loc[user_id] > 0])
        
        # 排除已交互的图书
        for book_id in user_books:
            if book_id in self.user_book_matrix.columns:
                book_idx = self.user_book_matrix.columns.get_loc(book_id)
                predicted_ratings[book_idx] = 0
        
        # 返回推荐
        recommended_indices = np.argsort(predicted_ratings)[::-1][:n_recommendations]
        return [self.user_book_matrix.columns[i] for i in recommended_indices]
    
    def hybrid_recommendation(self, user_id, books_df, n_recommendations=10):
        """混合推荐算法"""
        # 获取各种推荐结果
        cf_recommendations = self.collaborative_filtering(user_id, n_recommendations)
        cb_recommendations = self.content_based_filtering(user_id, books_df, n_recommendations)
        mf_recommendations = self.matrix_factorization(user_id, n_recommendations)
        
        # 计算综合分数
        book_scores = {}
        
        # 协同过滤权重0.4
        for i, book_id in enumerate(cf_recommendations):
            if book_id not in book_scores:
                book_scores[book_id] = 0
            book_scores[book_id] += 0.4 * (n_recommendations - i) / n_recommendations
        
        # 内容过滤权重0.3
        for i, book_id in enumerate(cb_recommendations):
            if book_id not in book_scores:
                book_scores[book_id] = 0
            book_scores[book_id] += 0.3 * (n_recommendations - i) / n_recommendations
        
        # 矩阵分解权重0.3
        for i, book_id in enumerate(mf_recommendations):
            if book_id not in book_scores:
                book_scores[book_id] = 0
            book_scores[book_id] += 0.3 * (n_recommendations - i) / n_recommendations
        
        # 排序并返回推荐
        sorted_recommendations = sorted(
            book_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [book_id for book_id, score in sorted_recommendations[:n_recommendations]]
    
    def get_popular_books(self, category=None, n_recommendations=10):
        """获取热门图书推荐"""
        # 计算图书的总体受欢迎程度
        book_popularity = self.user_book_matrix.sum(axis=0)
        
        if category:
            # 如果指定了类别，需要结合图书信息
            books_df = pd.read_sql(
                db.session.query(Book).filter(Book.category == category).statement,
                db.session.bind
            )
            category_books = set(books_df.index)
            book_popularity = book_popularity[book_popularity.index.isin(category_books)]
        
        # 返回最受欢迎的图书
        return book_popularity.nlargest(n_recommendations).index.tolist()
    
    def get_recent_books(self, n_recommendations=10):
        """获取最新图书推荐"""
        recent_books = db.session.query(Book).order_by(Book.created_at.desc()).limit(n_recommendations).all()
        return [book.id for book in recent_books]
    
    def get_personalized_recommendations(self, user_id, n_recommendations=10):
        """获取个性化推荐"""
        # 加载数据
        borrowings, ratings, behaviors, books = self.load_data()
        
        # 创建用户-图书矩阵
        self.create_user_book_matrix(borrowings, ratings, behaviors)
        
        # 使用混合推荐算法
        recommendations = self.hybrid_recommendation(user_id, books, n_recommendations)
        
        # 获取推荐图书的详细信息
        recommended_books = []
        for book_id in recommendations:
            book = db.session.query(Book).filter(Book.id == book_id).first()
            if book:
                recommended_books.append(book.to_dict())
        
        return recommended_books