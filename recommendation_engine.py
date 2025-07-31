import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from scipy.sparse import csr_matrix
import pickle
from datetime import datetime, timedelta
from models import db, User, Book, Borrowing, Rating, UserBehavior

class RecommendationEngine:
    """图书馆推荐引擎"""
    
    def __init__(self):
        self.user_book_matrix = None
        self.book_similarity_matrix = None
        self.user_similarity_matrix = None
        self.nmf_model = None
        self.tfidf_vectorizer = None
        self.book_features = None
        
    def build_user_book_matrix(self):
        """构建用户-图书交互矩阵"""
        # 获取所有借阅记录和评分
        borrowings_query = db.session.query(Borrowing.user_id, Borrowing.book_id).all()
        ratings_query = db.session.query(Rating.user_id, Rating.book_id, Rating.rating).all()
        
        # 转换为DataFrame
        borrowings = pd.DataFrame(borrowings_query, columns=['user_id', 'book_id'])
        ratings = pd.DataFrame(ratings_query, columns=['user_id', 'book_id', 'rating'])
        
        # 合并借阅和评分数据
        interactions = []
        
        # 借阅记录权重为1
        for _, row in borrowings.iterrows():
            interactions.append({
                'user_id': row['user_id'],
                'book_id': row['book_id'],
                'weight': 1.0
            })
        
        # 评分记录权重为评分值
        for _, row in ratings.iterrows():
            interactions.append({
                'user_id': row['user_id'],
                'book_id': row['book_id'],
                'weight': row['rating']
            })
        
        if not interactions:
            return None
            
        interactions_df = pd.DataFrame(interactions)
        
        # 创建用户-图书矩阵
        self.user_book_matrix = interactions_df.pivot_table(
            index='user_id', 
            columns='book_id', 
            values='weight', 
            fill_value=0
        )
        
        return self.user_book_matrix
    
    def collaborative_filtering_recommendations(self, user_id, n_recommendations=10):
        """基于协同过滤的推荐"""
        if self.user_book_matrix is None:
            self.build_user_book_matrix()
            
        if self.user_book_matrix is None or user_id not in self.user_book_matrix.index:
            return []
        
        # 计算用户相似度
        user_similarities = cosine_similarity(
            self.user_book_matrix.loc[[user_id]], 
            self.user_book_matrix
        )[0]
        
        # 找到最相似的用户
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # 排除自己
        
        # 获取相似用户喜欢的图书
        recommendations = {}
        for similar_user_idx in similar_users:
            similar_user_id = self.user_book_matrix.index[similar_user_idx]
            similarity = user_similarities[similar_user_idx]
            
            # 获取该用户的高评分图书
            user_books = self.user_book_matrix.loc[similar_user_id]
            high_rated_books = user_books[user_books > 0].index
            
            for book_id in high_rated_books:
                if book_id not in recommendations:
                    recommendations[book_id] = 0
                recommendations[book_id] += similarity * user_books[book_id]
        
        # 排序并返回推荐结果
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:n_recommendations]
        
        return [book_id for book_id, score in sorted_recommendations]
    
    def content_based_recommendations(self, user_id, n_recommendations=10):
        """基于内容的推荐"""
        # 获取用户历史借阅的图书
        user_books = db.session.query(Book).join(Borrowing).filter(
            Borrowing.user_id == user_id
        ).all()
        
        if not user_books:
            return []
        
        # 构建图书特征矩阵
        books_data = []
        for book in user_books:
            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'category': book.category,
                'description': book.description or ''
            })
        
        if not books_data:
            return []
        
        # 创建文本特征
        book_texts = []
        for book in books_data:
            text = f"{book['title']} {book['author']} {book['category']} {book['description']}"
            book_texts.append(text)
        
        # TF-IDF向量化
        if self.tfidf_vectorizer is None:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000, 
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.book_features = self.tfidf_vectorizer.fit_transform(book_texts)
        else:
            self.book_features = self.tfidf_vectorizer.transform(book_texts)
        
        # 计算用户偏好向量（平均所有借阅图书的特征）
        user_profile = np.asarray(self.book_features.mean(axis=0))
        
        # 获取所有图书
        all_books = db.session.query(Book).all()
        all_book_texts = []
        all_book_ids = []
        
        for book in all_books:
            if book.id not in [b['id'] for b in books_data]:  # 排除已借阅的图书
                text = f"{book.title} {book.author} {book.category} {book.description or ''}"
                all_book_texts.append(text)
                all_book_ids.append(book.id)
        
        if not all_book_texts:
            return []
        
        # 计算所有图书的特征向量
        all_book_features = self.tfidf_vectorizer.transform(all_book_texts)
        
        # 计算相似度
        similarities = cosine_similarity(user_profile.reshape(1, -1), all_book_features)[0]
        
        # 排序并返回推荐结果
        book_scores = list(zip(all_book_ids, similarities))
        book_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [book_id for book_id, score in book_scores[:n_recommendations]]
    
    def matrix_factorization_recommendations(self, user_id, n_recommendations=10):
        """基于矩阵分解的推荐"""
        if self.user_book_matrix is None:
            self.build_user_book_matrix()
            
        if self.user_book_matrix is None or user_id not in self.user_book_matrix.index:
            return []
        
        # 使用NMF进行矩阵分解
        if self.nmf_model is None:
            self.nmf_model = NMF(n_components=50, random_state=42)
            self.nmf_model.fit(self.user_book_matrix)
        
        # 获取用户和图书的潜在因子
        user_factors = self.nmf_model.transform(self.user_book_matrix)
        book_factors = self.nmf_model.components_
        
        # 找到用户索引
        user_idx = self.user_book_matrix.index.get_loc(user_id)
        
        # 预测用户对所有图书的评分
        predicted_ratings = np.dot(user_factors[user_idx], book_factors)
        
        # 获取用户已借阅的图书索引
        user_books = self.user_book_matrix.iloc[user_idx]
        borrowed_books = user_books[user_books > 0].index
        
        # 排除已借阅的图书
        book_ids = self.user_book_matrix.columns
        recommendations = []
        
        for i, book_id in enumerate(book_ids):
            if book_id not in borrowed_books:
                recommendations.append((book_id, predicted_ratings[i]))
        
        # 排序并返回推荐结果
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [book_id for book_id, score in recommendations[:n_recommendations]]
    
    def hybrid_recommendations(self, user_id, n_recommendations=10):
        """混合推荐算法"""
        # 获取不同算法的推荐结果
        cf_recommendations = self.collaborative_filtering_recommendations(user_id, n_recommendations)
        cb_recommendations = self.content_based_recommendations(user_id, n_recommendations)
        mf_recommendations = self.matrix_factorization_recommendations(user_id, n_recommendations)
        
        # 计算综合得分
        book_scores = {}
        
        # 协同过滤权重
        for i, book_id in enumerate(cf_recommendations):
            if book_id not in book_scores:
                book_scores[book_id] = 0
            book_scores[book_id] += (n_recommendations - i) * 0.4
        
        # 内容推荐权重
        for i, book_id in enumerate(cb_recommendations):
            if book_id not in book_scores:
                book_scores[book_id] = 0
            book_scores[book_id] += (n_recommendations - i) * 0.3
        
        # 矩阵分解权重
        for i, book_id in enumerate(mf_recommendations):
            if book_id not in book_scores:
                book_scores[book_id] = 0
            book_scores[book_id] += (n_recommendations - i) * 0.3
        
        # 排序并返回推荐结果
        sorted_recommendations = sorted(
            book_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:n_recommendations]
        
        return [book_id for book_id, score in sorted_recommendations]
    
    def get_popular_books(self, n_recommendations=10):
        """获取热门图书推荐"""
        # 统计借阅次数
        borrow_counts = db.session.query(
            Book.id, 
            db.func.count(Borrowing.id).label('borrow_count')
        ).join(Borrowing).group_by(Book.id).order_by(
            db.func.count(Borrowing.id).desc()
        ).limit(n_recommendations).all()
        
        return [book_id for book_id, count in borrow_counts]
    
    def get_recent_books(self, n_recommendations=10):
        """获取最新图书推荐"""
        recent_books = db.session.query(Book).order_by(
            Book.publish_year.desc()
        ).limit(n_recommendations).all()
        
        return [book.id for book in recent_books]
    
    def get_personalized_recommendations(self, user_id, n_recommendations=10):
        """获取个性化推荐"""
        # 检查用户是否有足够的历史数据
        user_borrowings = db.session.query(Borrowing).filter(
            Borrowing.user_id == user_id
        ).count()
        
        if user_borrowings < 3:
            # 新用户，返回热门图书
            return self.get_popular_books(n_recommendations)
        else:
            # 老用户，使用混合推荐
            return self.hybrid_recommendations(user_id, n_recommendations)